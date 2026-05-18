"""Packing Efficiency (PE 裝填效率) time-series and aggregates.

PE = fraction of bin cells occupied. The Simulator already records
``occupancy_after`` on every successful event, so this module is a pure
post-processor — it never re-walks the snapshot grids.

Failed arrivals are excluded from the trace: the bin state didn't change
on a failure, so emitting a point there would either repeat the previous
value or (worse, given the EventLog default) plot a misleading 0.0.

Time-weighted mean: PE is a step function between events. We integrate
left-Riemann over [t[0], t[-1]] — i.e. each sample's value contributes for
the duration until the next event. This is the only honest aggregate when
events cluster unevenly in time; arithmetic mean of samples would over-weight
busy regions. We deliberately do *not* extrapolate before t[0] or after
t[-1] — padding with zeros would inflate the denominator with empty time
that has no defined PE.
"""
from __future__ import annotations

import numpy as np

from ..core.simulator import SimResult
from .types import PEStats, TimeSeries


def pe_series(result: SimResult) -> TimeSeries:
    """Extract (t, occupancy_after) over successful events.

    Empty result (no successful events) → empty TimeSeries; downstream
    aggregates must handle the zero-length case.
    """
    points = [(e.t, e.occupancy_after) for e in result.events if e.success]
    if not points:
        return TimeSeries(
            t=np.zeros(0, dtype=np.int64),
            value=np.zeros(0, dtype=np.float64),
            label="pe",
        )
    ts = np.fromiter((t for t, _ in points), dtype=np.int64, count=len(points))
    vs = np.fromiter((v for _, v in points), dtype=np.float64, count=len(points))
    return TimeSeries(t=ts, value=vs, label="pe")


def pe_stats(result: SimResult) -> PEStats:
    """peak / peak_t / time-weighted mean / final + raw series.

    Degenerate cases:
      * No events → all zeros, peak_t=0.
      * Single event → mean collapses to that single value (no interval
        to integrate over).
      * All events at the same tick → mean collapses to the last value;
        integrating a zero-width interval is undefined.
    """
    series = pe_series(result)
    if series.t.size == 0:
        return PEStats(peak=0.0, peak_t=0, mean=0.0, final=0.0, series=series)

    peak_idx = int(np.argmax(series.value))
    peak = float(series.value[peak_idx])
    peak_t = int(series.t[peak_idx])
    final = float(series.value[-1])

    if series.t.size == 1 or series.t[-1] == series.t[0]:
        mean = float(series.value[-1])
    else:
        # Left-Riemann: value[i] holds from t[i] to t[i+1]. The last sample
        # contributes 0 width, which is correct — we don't know how long it
        # would have lasted after the simulation ended.
        widths = np.diff(series.t).astype(np.float64)
        mean = float(np.sum(series.value[:-1] * widths) / (series.t[-1] - series.t[0]))

    return PEStats(peak=peak, peak_t=peak_t, mean=mean, final=final, series=series)
