"""Utility functions for converting between SDK args and proto objects."""

from rime_sdk.protos.firewall.firewall_pb2 import BinSize


def get_bin_size_proto(bin_size_str: str) -> BinSize:
    """Get bin size proto from string."""
    years = 0
    months = 0
    seconds = 0
    if bin_size_str == "year":
        years += 1
    elif bin_size_str == "month":
        months += 1
    elif bin_size_str == "week":
        seconds += 7 * 24 * 60 * 60
    elif bin_size_str == "day":
        seconds += 24 * 60 * 60
    elif bin_size_str == "hour":
        seconds += 60 * 60
    else:
        raise ValueError(
            f"Got unknown bin size ({bin_size_str}), "
            f"should be one of: `year`, `month`, `week`, `day`, `hour`"
        )
    return BinSize(years=years, months=months, seconds=seconds)
