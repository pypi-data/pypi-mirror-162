"""Library defining the interface to Data Collector."""

import itertools
import json
import logging
from datetime import datetime
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

from google.protobuf.timestamp_pb2 import Timestamp

from rime_sdk.data_format_check.tabular_checker import FORMAT_DAYS, FORMAT_SECONDS
from rime_sdk.internal.backend import RIMEBackend
from rime_sdk.protos.data_collector.data_collector_pb2 import (
    NewDatapoint,
    StoreDatapointsRequest,
)

logger = logging.getLogger(__name__)

GRPC_MAX_BYTES_SIZE = 3500000


class NewDatapointIterator:
    """Iterator that transforms an iterator of inputs to datapoints."""

    def __init__(self, it: Iterator, model_id: Optional[str]):
        """Initialize iterator."""
        self.it = it
        self.model_id = model_id

    def __iter__(self) -> Iterator:
        """Return iterator."""
        return self

    def __next__(self) -> NewDatapoint:
        """Take next datapoint and convert to proto datapoint."""
        input_data, datapoint_id, pred, label, timestamp, query_id = self.it.__next__()
        return convert_input_to_datapoint(
            input_data, datapoint_id, timestamp, pred, label, query_id, self.model_id
        )


def convert_input_to_datapoint(
    input_data: Dict,
    datapoint_id: Optional[str] = None,
    timestamp: Optional[str] = None,
    pred: Optional[Union[Dict, List, float, int]] = None,
    label: Optional[Union[Dict, int, float]] = None,
    query_id: Optional[Union[str, float, int]] = None,
    model_id: Optional[str] = None,
) -> NewDatapoint:
    """Convert input data to a datapoint."""
    datapoint = NewDatapoint(
        input_data=json_serialize(input_data),
        created_time=convert_timestamp_to_proto_time(timestamp),
    )

    if datapoint_id is not None:
        datapoint.datapoint_id = datapoint_id
    if model_id is not None:
        datapoint.model_id = model_id
    if pred is not None:
        datapoint.pred = json_serialize(pred)
    if label is not None:
        datapoint.label = json_serialize(label)
    if query_id is not None:
        datapoint.query_id = json_serialize(query_id)

    return datapoint


def convert_timestamp_to_proto_time(timestamp: Optional[str]) -> Optional[Timestamp]:
    """Convert timestamp to datetime."""
    if timestamp is None:
        return None

    for time_format in [FORMAT_SECONDS, FORMAT_DAYS]:
        try:
            date = datetime.strptime(timestamp, time_format)
            proto_time = Timestamp()
            proto_time.FromDatetime(date)
            return proto_time
        except ValueError:
            continue

    raise ValueError(
        f"{timestamp} is an in invalid format."
        f" Acceptable timestamp formats are {FORMAT_DAYS}"
        f" and {FORMAT_SECONDS}."
    )


def json_serialize(serialize_object: Any) -> bytes:
    """Encode using UTF-8 or return as None."""
    return json.dumps(serialize_object).encode("utf-8")


def validate_log_datapoints(
    inputs: List[Dict], lists_to_validate: List[Optional[List]], list_names: List[str]
) -> None:
    """Create string message with everything wrong with inputs to log datapoints.

    Returns None if no errors.
    """
    input_len = len(inputs)

    for index, elements in enumerate(lists_to_validate):
        if elements is not None and len(elements) != input_len:
            error_str = "Size Mismatch in {}: {} data points, {} {}".format(
                list_names[index], input_len, len(elements), list_names[index]
            )
            raise ValueError(error_str)


class DataCollector:
    """Data Collector wrapper with helpful methods for working with the Data Collector.

    Attributes:
        backend: RIMEBackend
            The RIME backend used to query about the status of the insert.
        firewall_id: str
            ID of the Firewall associated with the Data Collector.
    """

    def __init__(self, backend: RIMEBackend, firewall_id: str,) -> None:
        """Create a new Data Collector wrapper object.

        Arguments:
            backend: RIMEBackend
                The RIME backend used to query about the status of the job.
            firewall_id: str
                The Firewall identifier the Data Collector is for.
        """
        self._backend = backend
        self._firewall_id = firewall_id

    def upload_datapoints_with_buffer(self, datapoints: Iterator) -> None:
        """Upload a list of Data Collector datapoints, buffering message size."""
        datapoint_list: List[NewDatapoint] = []
        bytes_counter = 0

        # Parse through datapoints, uploading the max amount that GRPC supports
        # each time
        with self._backend.GRPCErrorHandler():
            with self._backend.get_data_collector_stub() as data_collector_tester:
                for datapoint in datapoints:
                    # Request will error if a single datapoint is too large
                    # This is OK because if it does, it means that the user
                    # is using the product in a way we don't currently want to support
                    # 4MB GRPC Message limit is large enough
                    if bytes_counter + datapoint.ByteSize() > GRPC_MAX_BYTES_SIZE:
                        req = StoreDatapointsRequest(
                            firewall_id=self._firewall_id,
                            datapoints_to_store=datapoint_list,
                        )
                        data_collector_tester.StoreDatapoints(req)

                        datapoint_list = [datapoint]
                        bytes_counter = datapoint.ByteSize()
                    else:
                        datapoint_list.append(datapoint)
                        bytes_counter += datapoint.ByteSize()
                # Upload remaining datapoints
                if len(datapoint_list) > 0:
                    req = StoreDatapointsRequest(
                        firewall_id=self._firewall_id,
                        datapoints_to_store=datapoint_list,
                    )
                    data_collector_tester.StoreDatapoints(req)

    def log_datapoints(
        self,
        inputs: List[Dict],
        datapoint_ids: Optional[List[str]] = None,
        timestamps: Optional[List[str]] = None,
        preds: Optional[List[Union[Dict, List, float, int]]] = None,
        labels: Optional[List[Union[Dict, int, float]]] = None,
        query_ids: Optional[List[Union[str, float, int]]] = None,
        model_id: Optional[str] = None,
    ) -> None:
        """Log Datapoints in batch."""
        # Validate Datapoint List
        validate_log_datapoints(
            inputs,
            [preds, labels, timestamps, datapoint_ids, query_ids],
            ["preds", "labels", "timestamps", "datapoint_ids", "query_ids"],
        )

        # Easier for looping through options
        it_data_ids: Iterable[Any] = datapoint_ids or itertools.repeat(None)
        it_timestamps: Iterable[Any] = timestamps or itertools.repeat(None)
        it_preds: Iterable[Any] = preds or itertools.repeat(None)
        it_labels: Iterable[Any] = labels or itertools.repeat(None)
        it_queries: Iterable[Any] = query_ids or itertools.repeat(None)

        data_vals = zip(
            inputs, it_data_ids, it_preds, it_labels, it_timestamps, it_queries,
        )
        datapoint_iterator = NewDatapointIterator(iter(data_vals), model_id)
        self.upload_datapoints_with_buffer(datapoint_iterator)
