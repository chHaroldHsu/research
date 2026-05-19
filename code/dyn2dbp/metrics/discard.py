"""Discard rate time-series and aggregates.

A discard is an ARRIVAL with success=False: the strategy couldn't find any
position for the item, so it's dropped. The Simulator already counts discards
(``result.discarded_count``) and logs every arrival outcome, so this module
is a pure post-processor.

Two complementary views, both keyed off arrival events:

  * **Cumulative**: rate over all arrivals seen so far. Smooth, monotone-ish,
    converges toward the overall rate. Good for the "headline number" plot.
  * **Windowed**: rate over arrivals in [t - window, t]. Catches local bursts
    of failure that the cumulative curve dampens — the kind of signal we
    need to spot fragmentation building up over time.

Window units are simulator ticks (same as ``Item.t_arrive``), *not* event
indices. Time-based is right for dynamic workloads where arrivals are
unevenly paced: a busy burst and a quiet stretch should be comparable.

Departures are ignored entirely: discards are an arrival-only outcome,
and including DEPARTURE rows in the denominator would dilute the rate.
"""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from ..core.simulator import ARRIVAL, SimResult
from .types import DiscardStats, TimeSeries


def discard_series(
    result: SimResult, window: Optional[int] = None
) -> Tuple[TimeSeries, Optional[TimeSeries]]:
    """Return (cumulative_rate_series, windowed_rate_series or None).

    Both series are sampled at every arrival event (success or failure), so
    the x-axis is "arrival ticks" — a discard at t=42 shows up at t=42 in
    both curves.

    Empty result (no arrivals) → two empty series (windowed is None when
    ``window`` is None either way).
    """
    arrivals = [e for e in result.events if e.event_type == ARRIVAL]
    if not arrivals:
        empty = TimeSeries(
            t=np.zeros(0, dtype=np.int64),
            value=np.zeros(0, dtype=np.float64),
            label="discard_cumulative",
        )
        return empty, None

    t = np.fromiter((e.t for e in arrivals), dtype=np.int64, count=len(arrivals))
    failed = np.fromiter(
        ((not e.success) for e in arrivals), dtype=bool, count=len(arrivals)
    )

    # Cumulative: at arrival k (1-indexed), rate = (# failures in first k) / k.
    n = np.arange(1, len(arrivals) + 1, dtype=np.int64)
    cum_failed = np.cumsum(failed.astype(np.int64))
    cumulative = TimeSeries(
        t=t,
        value=cum_failed.astype(np.float64) / n.astype(np.float64),
        label="discard_cumulative",
    )

    if window is None:
        return cumulative, None

    if window <= 0:
        raise ValueError(f"window must be positive (got {window})")

    # Windowed: at each arrival i, look back to t[i] - window (inclusive).
    # Arrivals are emitted in time order by the heapq, so t is non-decreasing
    # and searchsorted finds the left edge of the window in O(log n).
    windowed = np.zeros(len(arrivals), dtype=np.float64)
    cum_with_zero = np.concatenate(([0], cum_failed))  # cum_with_zero[k] = failures in first k arrivals
    for i in range(len(arrivals)):
        start = int(np.searchsorted(t, t[i] - window, side="left"))
        end = i + 1
        n_window = end - start
        n_failed_window = int(cum_with_zero[end] - cum_with_zero[start])
        windowed[i] = n_failed_window / n_window  # n_window >= 1 because i is in the window

    windowed_series = TimeSeries(t=t, value=windowed, label="discard_windowed")
    return cumulative, windowed_series


def discard_stats(result: SimResult, window: Optional[int] = None) -> DiscardStats:
    """Total / overall-rate / cumulative series / optional windowed series.

    ``total`` mirrors ``result.discarded_count`` — we re-derive it from the
    event log here so the stats are self-consistent if a caller ever
    constructs a SimResult by hand (e.g. tests).
    """
    arrivals = [e for e in result.events if e.event_type == ARRIVAL]
    total = sum(1 for e in arrivals if not e.success)
    rate_overall = (total / len(arrivals)) if arrivals else 0.0

    cumulative, windowed = discard_series(result, window=window)
    return DiscardStats(
        total=total,
        rate_overall=rate_overall,
        series_cumulative=cumulative,
        series_windowed=windowed,
    )
