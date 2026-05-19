"""Metrics — post-processors over SimResult.

Three families, all pure functions of a ``SimResult``:

  * ``pe`` — Packing Efficiency 裝填效率 (instantaneous occupancy fraction)
  * ``discard`` — arrival drop rate (cumulative and rolling)
  * ``fragmentation`` — perimeter² shape factor of free space

Re-exported here so callers do ``from dyn2dbp.metrics import pe_stats`` rather
than reaching into submodules. Types live next to the metrics that produce
them in ``types`` for the same reason — one import point per concept.
"""
from .discard import discard_series, discard_stats
from .fragmentation import (
    fragmentation,
    fragmentation_series,
    fragmentation_stats,
)
from .pe import pe_series, pe_stats
from .types import DiscardStats, FragStats, PEStats, TimeSeries

__all__ = [
    "DiscardStats",
    "FragStats",
    "PEStats",
    "TimeSeries",
    "discard_series",
    "discard_stats",
    "fragmentation",
    "fragmentation_series",
    "fragmentation_stats",
    "pe_series",
    "pe_stats",
]
