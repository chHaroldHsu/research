"""Shared return types for the metrics module.

Why a separate file: pe / discard / fragmentation all need the same TimeSeries
container, and downstream viz code wants a stable surface to import from
without dragging in metric-specific logic.

All structs are frozen so they're safe to pass into viz / experiment runners
without worrying about accidental mutation between cells of the factorial
sweep.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class TimeSeries:
    """A (t, value) pair sampled at event times.

    ``t`` is event timestamps (monotonic non-decreasing — equal ticks happen
    when a departure and arrival share a time, both produce snapshots).
    ``value`` is the metric at each tick. Both 1D, same length.

    ``label`` identifies which metric this is (``"pe"``, ``"discard_rate"``,
    ``"fragmentation"``) so a single plotting helper can title axes correctly
    without the caller passing the name in separately.
    """
    t: np.ndarray
    value: np.ndarray
    label: str

    def __post_init__(self) -> None:
        if self.t.ndim != 1 or self.value.ndim != 1:
            raise ValueError(f"TimeSeries arrays must be 1D (got t.ndim={self.t.ndim}, value.ndim={self.value.ndim})")
        if self.t.shape != self.value.shape:
            raise ValueError(f"TimeSeries t and value must align (got {self.t.shape} vs {self.value.shape})")


@dataclass(frozen=True)
class PEStats:
    """Aggregates over a PE (Packing Efficiency 裝填效率) trace.

    ``mean`` is time-weighted (∫PE dt / T), not the arithmetic mean of
    samples — events cluster unevenly in time, so a sample mean would
    over-weight dense regions.
    """
    peak: float
    peak_t: int
    mean: float
    final: float
    series: TimeSeries


@dataclass(frozen=True)
class DiscardStats:
    """Aggregates over arrival outcomes.

    ``series_windowed`` is Optional because the rolling rate only makes sense
    when the caller picks a window size; for a quick-look run with window=None
    we still produce the cumulative curve.
    """
    total: int
    rate_overall: float
    series_cumulative: TimeSeries
    series_windowed: Optional[TimeSeries]


@dataclass(frozen=True)
class FragStats:
    """Aggregates over the Tabero perimeter² fragmentation trace."""
    peak: float
    peak_t: int
    mean: float
    series: TimeSeries
