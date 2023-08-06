"""Library defining the interface to firewall."""
import json
from typing import Any, Dict, List, Optional, Tuple, cast

import pandas as pd
from google.protobuf.json_format import MessageToDict, ParseDict

from rime_sdk.data_collector import DataCollector
from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.internal.throttle_queue import ThrottleQueue
from rime_sdk.job import ContinuousTestJob
from rime_sdk.protos.firewall.firewall_pb2 import (
    DataLocation,
    DataLocationType,
    DeleteFirewallRequest,
    FirewallComponents,
    FirewallRules,
    GetServiceMetricsRequest,
    GetServiceMetricsResponse,
    ListBatchSummariesRequest,
    ListBatchSummariesResponse,
    ListFirewallsRequest,
    ListFirewallsResponse,
    UpdateFirewallComponentsRequest,
    UpdateFirewallRequest,
    UpdateFirewallResponse,
)
from rime_sdk.protos.jobs.jobs_pb2 import JobMetadata
from rime_sdk.protos.model_testing.model_testing_pb2 import (
    CustomImage,
    RunFirewallIncrementalDataRequest,
)
from rime_sdk.protos.result_synthesizer.result_message_pb2 import (
    CLIConfig,
    DataType,
    ThresholdInfo,
)
from rime_sdk.protos.rime_configs.rime_configs_pb2 import (
    DataCollectorIncrementalConfig,
    PathImagesIncrementalConfig,
    PathNLPIncrementalConfig,
    PathTabularIncrementalConfig,
)
from rime_sdk.test_run import ContinuousTestRun

LOCATION_TYPE_TO_ENUM_MAP: Dict[str, "DataLocationType.V"] = {
    "data_collector": DataLocationType.LOCATION_TYPE_DATA_COLLECTOR
}


def location_args_to_data_location(location_type: str) -> DataLocation:
    """Create Data Location object for Firewall Requests."""
    location_keys = set(LOCATION_TYPE_TO_ENUM_MAP.keys())
    if location_type not in location_keys:
        raise ValueError(
            f"Location type {location_type} must be one of {location_keys}"
        )
    return DataLocation(location_type=LOCATION_TYPE_TO_ENUM_MAP[location_type])


class Firewall:
    """Firewall object wrapper with helpful methods for working with RIME Firewall.

    Attributes:
        backend: RIMEBackend
            The RIME backend used to query about the status of the job.
        firewall_id: str
            How to refer to the FW in the backend.
            Use this attribute to specify the Firewall for tasks in the backend.
    """

    # A throttler that limits the number of model tests to roughly 20 every 5 minutes.
    # This is a static variable for Client.
    _throttler = ThrottleQueue(desired_events_per_epoch=20, epoch_duration_sec=300)

    def __init__(self, backend: RIMEBackend, firewall_id: str,) -> None:
        """Create a new Firewall wrapper object.

        Arguments:
            backend: RIMEBackend
                The RIME backend used to query about the status of the job.
            firewall_id: str
                The identifier for the RIME job that this object monitors.
        """
        self._backend = backend
        self._firewall_id = firewall_id
        self._data_collector = DataCollector(self._backend, self._firewall_id)

    def __str__(self) -> str:
        """Pretty-print the object."""
        res = {"firewall_id": self._firewall_id}
        return f"Firewall {res}"

    def __eq__(self, obj: Any) -> bool:
        """Check if this FWInstance is equivalent to 'obj'."""
        return isinstance(obj, Firewall) and self._firewall_id == obj._firewall_id

    def get_stress_test_config(self) -> dict:
        """Return the current stress test config."""
        req = ListFirewallsRequest(firewall_ids=[self._firewall_id])
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ListFirewallsResponse = firewall_tester.ListFirewalls(req)
        config_proto = res.firewalls[0].cli_config
        return json.loads(config_proto.data.decode("utf-8"))

    def get_metric_thresholds(self) -> pd.DataFrame:
        """Return the current thresholds for metrics tracked over time.

        Returns:
            A Pandas DataFrame where each row is a threshold for a
            different metric and each column is a threshold attribute.
        """
        req = ListFirewallsRequest(firewall_ids=[self._firewall_id])
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ListFirewallsResponse = firewall_tester.ListFirewalls(req)
        bm = res.firewalls[0].batch_metadata
        parsed_thresholds = []
        for metric_name, proto_threshold_info in bm.threshold_info_map.items():
            threshold_dict = MessageToDict(
                proto_threshold_info,
                including_default_value_fields=True,
                preserving_proto_field_name=True,
            )
            threshold_dict["metric_name"] = metric_name
            parsed_thresholds.append(threshold_dict)
        return pd.DataFrame(parsed_thresholds)

    def get_scheduled_ct_info(self) -> Tuple[bool, dict]:
        """Return the status of scheduled CT and the location data is pulled from.

        Returns:
            Tuple[bool, dict]:
                The first value is a boolean indicating whether
                Scheduled CT has been activated. The second is a dictionary
                containing information about the data location used to run CT.

        Example:

        .. code-block:: python

            # Understand if Scheduled CT is running and from which location data is pulled from.
            is_ct_activated, location_args = firewall.get_scheduled_ct_info()

        :meta private:
        """
        req = ListFirewallsRequest(firewall_ids=[self._firewall_id])
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ListFirewallsResponse = firewall_tester.ListFirewalls(req)
        schedule_status = res.firewalls[0].run_ct_schedule
        data_location_info = res.firewalls[0].data_location_info
        data_location_dict = MessageToDict(
            data_location_info, preserving_proto_field_name=True
        )
        return schedule_status, data_location_dict

    def get_firewall_rules(self) -> dict:
        """Return the current firewall rules."""
        req = ListFirewallsRequest(firewall_ids=[self._firewall_id])
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ListFirewallsResponse = firewall_tester.ListFirewalls(req)
        config_proto = res.firewalls[0].firewall_rules
        return json.loads(config_proto.data.decode("utf-8"))

    def get_data_collector(self) -> DataCollector:
        """Get Data Collector, create if None."""
        if self._data_collector is None:
            self._data_collector = DataCollector(self._backend, self._firewall_id)
        return self._data_collector

    def delete_firewall(self) -> None:
        """Delete firewall."""
        req = DeleteFirewallRequest(firewall_id=self._firewall_id)
        with self._backend.get_firewall_stub() as firewall_tester:
            firewall_tester.DeleteFirewall(req)

    def _update_firewall(self, **update_params: Any) -> UpdateFirewallResponse:
        req = UpdateFirewallRequest(firewall_id=self._firewall_id, **update_params)
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                return firewall_tester.UpdateFirewallTestRunID(req)

    def update_firewall_stress_test_run(
        self, stress_test_run_id: str
    ) -> UpdateFirewallResponse:
        """Update firewall with stress test run id.

        Arguments:
            stress_test_run_id: Stress Test Run Id to configure new firewall

        Returns:
            UpdateFirewallResponse

        Raises:
            ValueError
                If the provided status_filters array has invalid values.
                If the request to the ModelTest service failed.
        """
        return self._update_firewall(stress_test_run_id=stress_test_run_id)

    def update_stress_test_config(
        self, stress_test_config: Dict[str, Any]
    ) -> UpdateFirewallResponse:
        """Update firewall with stress test config.

        Arguments:
            stress_test_config: Stress Test Config to configure new firewall

        Returns:
            UpdateFirewallResponse

        Raises:
            ValueError
                If the provided values are improperly formatted
                If the request to the ModelTest service failed.
        """
        return self._update_firewall_components(stress_test_config=stress_test_config)

    def activate_ct_schedule(self, location_type: str) -> UpdateFirewallResponse:
        """Activate CT Schedule for this firewall with a given data type.

        Arguments:
            data_type: Type of the data location that ScheduledCT will pull data from.

        Returns:
            UpdateFirewallResponse

        Raises:
            ValueError
                If the data_type is invalid
                If the request to the ModelTest service failed

        :meta private:
        """
        return self._update_firewall_components(
            run_ct_schedule=True, location_type=location_type
        )

    def deactivate_ct_schedule(self) -> UpdateFirewallResponse:
        """Deactivate CT Schedule for this firewall.

        Returns:
            UpdateFirewallResponse

        Raises:
            ValueError
                If the request to the ModelTest service failed

        :meta private:
        """
        return self._update_firewall_components(run_ct_schedule=False)

    def update_firewall_rules(
        self, rules: List[Dict[str, Any]]
    ) -> UpdateFirewallResponse:
        """Update firewall with rules.

        Arguments:
            rules: Rules to configure new firewall

        Returns:
            UpdateFirewallResponse

        Raises:
            ValueError
                If the provided values are improperly formatted
                If the request to the ModelTest service failed.
        """
        return self._update_firewall_components(firewall_rules=rules)

    def _update_firewall_components(
        self,
        stress_test_config: Optional[Dict[str, Any]] = None,
        firewall_rules: Optional[List[Dict[str, Any]]] = None,
        metric_thresholds: Optional[Dict[str, ThresholdInfo]] = None,
        run_ct_schedule: Optional[bool] = None,
        location_type: Optional[str] = None,
    ) -> UpdateFirewallResponse:
        """Update the firewall components manually.

        Only valid non-null arguments are updated.

        Arguments:
            cli_config: CLI Config to update the firewall with.
            firewall_rules: Firewall Rules to update the firewall with.
            metric_thresholds: Threshold info for each summary metric.

        Returns:
            UpdateFirewallResponse

        Raises:
            ValueError
                If the provided values are improperly formatted
                If the request to the ModelTest service failed.
        """
        components_kwargs: Dict[str, Any] = {}
        if stress_test_config is not None:
            components_kwargs["cli_config"] = CLIConfig(
                data=json.dumps(stress_test_config).encode("utf-8")
            )
        if firewall_rules is not None:
            components_kwargs["firewall_rules"] = FirewallRules(
                data=json.dumps(firewall_rules).encode("utf-8")
            )
        if metric_thresholds is not None:
            components_kwargs["threshold_info_map"] = metric_thresholds
        components = (
            FirewallComponents(**components_kwargs) if components_kwargs else None
        )
        req = UpdateFirewallComponentsRequest(
            firewall_id=self._firewall_id, components=components
        )
        if run_ct_schedule is not None:
            req.run_ct_schedule = run_ct_schedule
        if location_type is not None:
            data_location_info = location_args_to_data_location(location_type)
            req.data_location_info.CopyFrom(data_location_info)
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                return firewall_tester.UpdateFirewallComponents(req)

    def get_link(self) -> str:
        """Get the web app URL to the firewall.

        This link directs to your organization's deployment of RIME.
        You can view more detailed information about the firewall
        in the web app, including helpful visualizations, key insights on your
        model's performance, and explanations of test results for each batch.

        Note: this is a string that should be copy-pasted into a browser.
        """
        # Fetch test run metadata and return a dataframe of the single row.
        req = ListFirewallsRequest(firewall_ids=[self._firewall_id])
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                res: ListFirewallsResponse = firewall_tester.ListFirewalls(req)
        return res.firewalls[0].web_app_url.url

    def _get_incremental_config_request(
        self,
        test_run_config: Dict,
        test_run_config_type: str,
        disable_firewall_events: bool,
    ) -> RunFirewallIncrementalDataRequest:
        """Get incremental config request."""
        if test_run_config_type == "data_collector":
            arg = "data_collector_config"
            test_run_config_obj = ParseDict(
                test_run_config, DataCollectorIncrementalConfig()
            )
        else:
            # TODO: this will eventually take in the config_dict in order to load format
            sreq = GetServiceMetricsRequest(firewall_id=self._firewall_id)
            with self._backend.GRPCErrorHandler():
                with self._backend.get_firewall_stub() as firewall_tester:
                    sres: GetServiceMetricsResponse = firewall_tester.GetServiceMetrics(
                        sreq
                    )

            # TODO: each modality will eventually need its own logic
            # to determine config proto
            _DATA_TYPE_TO_CONFIG_MAP = {
                DataType.TABULAR: ("path_tabular_config", PathTabularIncrementalConfig),
                DataType.NLP: ("path_nlp_config", PathNLPIncrementalConfig),
                DataType.IMAGES: ("path_images_config", PathImagesIncrementalConfig),
            }
            arg, config_cls = _DATA_TYPE_TO_CONFIG_MAP[sres.input_type]
            test_run_config_obj = ParseDict(test_run_config, config_cls())

        req = RunFirewallIncrementalDataRequest(
            firewall_id=self._firewall_id,
            disable_firewall_events=disable_firewall_events,
        )
        # NOTE: avoid lint errors
        getattr(req, arg).CopyFrom(test_run_config_obj)

        return req

    def run_firewall_incremental_data(
        self,
        test_run_config: dict,
        test_run_config_type: str = "default",
        disable_firewall_events: bool = True,
        custom_image: Optional[CustomImage] = None,
        rime_managed_image: Optional[str] = None,
        ram_request_megabytes: Optional[int] = None,
        cpu_request_millicores: Optional[int] = None,
    ) -> ContinuousTestJob:
        """Start a RIME model firewall test on the backend's ModelTesting service.

        This allows you to run Firewall Test job on the RIME
        backend. This will run firewall on a batch of tabular data.

        Arguments:
            test_run_config: dict
                Configuration for the test to be run, which specifies paths to
                the model and datasets to used for the test.
            test_run_config_type: Optional[str]
                Specifies the type of test_run_config to pass through. Available options
                are `default`, `data_collector`.
            custom_image: Optional[CustomImage]
                Specification of a customized container image to use running the model
                test. The image must have all dependencies required by your model.
                The image must specify a name for the image and optional a pull secret
                (of type CustomImage.PullSecret) with the name of the kubernetes pull
                secret used to access the given image.
            rime_managed_image: Optional[str]
                Name of a managed image to use when running the model test.
                The image must have all dependencies required by your model. To create
                new managed images with your desired dependencies, use the client's
                ``create_managed_image()`` method.
            ram_request_megabytes: int
                Megabytes of RAM requested for the stress test job. If none
                specified, will default to 4000MB. The limit is 2x the megabytes
                requested.
            cpu_request_millicores: int
                Millicores of CPU requested for the stress test job. If none
                specified, will default to 1500mi. The limit is 2x the millicores
                requested.

        Returns:
            A ``Job`` providing information about the model stress test
            job.

        Raises:
            ValueError
                If the request to the ModelTest service failed.

        Example:

        .. code-block:: python

            # This example will likely not work for you because it requires permissions
            # to a specific S3 bucket. This demonstrates how you might specify such a
            # configuration.
            incremental_config = {
                "eval_path": "s3://rime-datasets/
                   fraud_continuous_testing/eval_2021_04_30_to_2021_05_01.csv",
                "timestamp_col": "timestamp"
            }
            # Run the job using the specified config and the default Docker image in
            # the RIME backend. Use the RIME Managed Image "tensorflow115".
            # This assumes you have already created the Managed Image and waited for it
            # to be ready.
            firewall = rime_client.get_firewall("foo")
            job =
                firewall.run_firewall_incremental_data(
                    test_run_config=incremental_config,
                    rime_managed_image="tensorflow115",
                    ram_request_megabytes=8000,
                    cpu_request_millicores=2000)
        """
        # TODO(blaine): Add config validation service.
        if not isinstance(test_run_config, dict):
            raise ValueError("The configuration must be a dictionary")

        if custom_image and rime_managed_image:
            raise ValueError(
                "Cannot specify both 'custom_image' and 'rime_managed_image'"
            )

        req = self._get_incremental_config_request(
            test_run_config, test_run_config_type, disable_firewall_events
        )
        if custom_image:
            req.custom_image_type.testing_image.CopyFrom(custom_image)
        if rime_managed_image:
            req.custom_image_type.managed_image.name = rime_managed_image
        if ram_request_megabytes:
            req.ram_request_megabytes = ram_request_megabytes
        if cpu_request_millicores:
            req.cpu_request_millicores = cpu_request_millicores
        with self._backend.GRPCErrorHandler():
            Firewall._throttler.throttle(  # pylint: disable=W0212
                throttling_msg="Your request is throttled to limit # of model tests."
            )
            with self._backend.get_model_testing_stub() as model_tester:
                job: JobMetadata = model_tester.RunFirewallIncrementalData(
                    request=req
                ).job
        return ContinuousTestJob(self._backend, job.job_id)

    def get_test_runs(self) -> List[ContinuousTestRun]:
        """Get a list of continuous test runs associated with this firewall."""
        req = ListBatchSummariesRequest(firewall_id=self._firewall_id)
        test_runs = []
        with self._backend.GRPCErrorHandler():
            with self._backend.get_firewall_stub() as firewall_tester:
                for result in firewall_tester.ListBatchSummaries(req):
                    result = cast(ListBatchSummariesResponse, result)
                    metadata = result.batch_summary.batch_result_metadata
                    start_time = metadata.start_time_epoch_seconds.ToDatetime()
                    end_time = metadata.end_time_epoch_seconds.ToDatetime()
                    test_run_id = result.batch_summary.batch_result_metadata.test_run_id
                    test_run = ContinuousTestRun(
                        self._backend, test_run_id, (start_time, end_time),
                    )
                    test_runs.append(test_run)
        return test_runs
