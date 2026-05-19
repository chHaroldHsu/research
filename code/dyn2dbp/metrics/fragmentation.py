"""Fragmentation metric — perimeter² shape factor on free space.

Inspired by Tabero et al. (2008)'s FPGA fragmentation measure. We deliberately
do not claim to reproduce that paper's exact formula — there are several
variants in the literature; we adopt one with a clean, interpretable scale
and document it explicitly here.

**Definition**

For each connected component (4-neighbour) of empty cells, compute its
perimeter P_i. Let A be the total empty area. Then::

    F = Σ P_i² / (16 · A)

Shape-factor intuition: a single square free region of side L gives
F = (4L)² / (16 · L²) = 1. Long thin slivers blow up F (perimeter grows
fast, area doesn't). Multiple equal squares give F ≈ 1 too — the metric is
*shape*, not piece count. That's the right semantics for this study: a few
big square holes are not "more fragmented" than one big square hole, but a
maze of thin gaps is.

Edge cases:
  * No empty cells (bin full) → F = 0. There's no free space to fragment.
  * Empty bin → one component, F = ((2W + 2H) / 4·√A)² ≥ 1, equal to 1
    only when the bin is square.

**Why this lives next to PE, not inside the simulator**

Computing connected components per snapshot is O(W·H), which is fine at 50×50
but would slow the simulator's hot loop noticeably. The simulator stores the
snapshot grid (cheap copy) and this module computes F lazily on whoever asks.

**Pure-numpy CC labelling**

We don't depend on scipy. The label routine is an iterative DFS with a
Python-list stack — at 50×50 (2500 cells max per component) this is
microseconds, and avoiding scipy keeps the dependency surface tight.
"""
from __future__ import annotations

import numpy as np

from ..core.simulator import SimResult
from .types import FragStats, TimeSeries


def _label_components(mask: np.ndarray) -> np.ndarray:
    """4-connected component labels (0=background, 1..k=components).

    Iterative DFS rather than recursion: a worst-case 50×50 = 2500-cell
    component would blow Python's recursion limit on a contiguous empty bin.
    """
    H, W = mask.shape
    labels = np.zeros((H, W), dtype=np.int32)
    cur = 0
    for sy in range(H):
        for sx in range(W):
            if not mask[sy, sx] or labels[sy, sx] != 0:
                continue
            cur += 1
            stack = [(sy, sx)]
            while stack:
                y, x = stack.pop()
                if labels[y, x] != 0:
                    continue
                labels[y, x] = cur
                if y > 0 and mask[y - 1, x] and labels[y - 1, x] == 0:
                    stack.append((y - 1, x))
                if y < H - 1 and mask[y + 1, x] and labels[y + 1, x] == 0:
                    stack.append((y + 1, x))
                if x > 0 and mask[y, x - 1] and labels[y, x - 1] == 0:
                    stack.append((y, x - 1))
                if x < W - 1 and mask[y, x + 1] and labels[y, x + 1] == 0:
                    stack.append((y, x + 1))
    return labels


def _perimeter_per_cell(mask: np.ndarray) -> np.ndarray:
    """For each empty cell, count edges that border non-empty or out-of-bounds.

    Vectorised: pad with False (so the bin border counts as occupied → +1
    perimeter per edge cell), then for each cell count empty neighbours and
    subtract from 4.
    """
    H, W = mask.shape
    padded = np.zeros((H + 2, W + 2), dtype=bool)
    padded[1:-1, 1:-1] = mask
    up = padded[0:-2, 1:-1]
    down = padded[2:, 1:-1]
    left = padded[1:-1, 0:-2]
    right = padded[1:-1, 2:]
    empty_neighbours = (
        up.astype(np.int32)
        + down.astype(np.int32)
        + left.astype(np.int32)
        + right.astype(np.int32)
    )
    return ((4 - empty_neighbours) * mask).astype(np.int32)


def fragmentation(grid: np.ndarray) -> float:
    """Perimeter² shape factor for the empty cells of one grid snapshot.

    See module docstring for the definition. Returns 0.0 when the bin is
    completely full (no free space to characterise).
    """
    mask = grid == 0
    total_empty = int(mask.sum())
    if total_empty == 0:
        return 0.0

    labels = _label_components(mask)
    per_cell = _perimeter_per_cell(mask)
    n_components = int(labels.max())

    sum_p_sq = 0
    for k in range(1, n_components + 1):
        comp_mask = labels == k
        p = int(per_cell[comp_mask].sum())
        sum_p_sq += p * p

    return sum_p_sq / (16.0 * total_empty)


def fragmentation_series(result: SimResult) -> TimeSeries:
    """One F value per snapshot the simulator captured.

    The simulator captures a snapshot on every successful event (and skips
    failed arrivals), so the series timing matches ``pe_series`` exactly —
    they can be plotted on a shared x-axis without resampling.
    """
    if not result.snapshots:
        return TimeSeries(
            t=np.zeros(0, dtype=np.int64),
            value=np.zeros(0, dtype=np.float64),
            label="fragmentation",
        )
    ts = np.fromiter(
        (t for t, _ in result.snapshots),
        dtype=np.int64,
        count=len(result.snapshots),
    )
    vs = np.fromiter(
        (fragmentation(g) for _, g in result.snapshots),
        dtype=np.float64,
        count=len(result.snapshots),
    )
    return TimeSeries(t=ts, value=vs, label="fragmentation")


def fragmentation_stats(result: SimResult) -> FragStats:
    """peak / peak_t / time-weighted mean + raw series.

    Same time-weighted-mean rationale as ``pe_stats``: snapshots cluster
    unevenly in time, so a sample mean would over-weight busy stretches.
    Degenerate cases mirror PE — no snapshots → all zeros; single snapshot
    or all-same-tick → mean collapses to the last value.
    """
    series = fragmentation_series(result)
    if series.t.size == 0:
        return FragStats(peak=0.0, peak_t=0, mean=0.0, series=series)

    peak_idx = int(np.argmax(series.value))
    peak = float(series.value[peak_idx])
    peak_t = int(series.t[peak_idx])

    if series.t.size == 1 or series.t[-1] == series.t[0]:
        mean = float(series.value[-1])
    else:
        widths = np.diff(series.t).astype(np.float64)
        mean = float(
            np.sum(series.value[:-1] * widths) / (series.t[-1] - series.t[0])
        )

    return FragStats(peak=peak, peak_t=peak_t, mean=mean, series=series)
