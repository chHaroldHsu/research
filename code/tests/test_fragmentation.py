"""Tests for the fragmentation (perimeter² shape factor) metric.

Strategy: most tests are pure ``fragmentation(grid)`` calls on hand-built
arrays — the metric is deterministic geometry, and the simulator's snapshot
plumbing is already covered elsewhere. We do drive the Simulator once at the
end to confirm the series wiring works end-to-end.
"""
import numpy as np

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item
from dyn2dbp.core.simulator import Simulator
from dyn2dbp.heuristics.blf import BLF
from dyn2dbp.metrics.fragmentation import (
    _label_components,
    fragmentation,
    fragmentation_series,
    fragmentation_stats,
)


def test_fragmentation_full_bin_is_zero():
    """No empty cells → F = 0 (no free space to characterise)."""
    grid = np.ones((4, 4), dtype=np.int32)
    assert fragmentation(grid) == 0.0


def test_fragmentation_empty_square_bin_is_one():
    """A perfectly square free region gives F = 1 by construction.

    4×4 empty bin: perimeter = 16 (one cell-edge per outer boundary cell),
    area = 16, F = 16² / (16·16) = 1.0.
    """
    grid = np.zeros((4, 4), dtype=np.int32)
    np.testing.assert_allclose(fragmentation(grid), 1.0)


def test_fragmentation_long_sliver_above_one():
    """A 1×10 slab gives F = 22² / (16·10) ≈ 3.025 — confirms the metric
    penalises long-thin geometry, which is the whole point."""
    grid = np.zeros((1, 10), dtype=np.int32)
    np.testing.assert_allclose(fragmentation(grid), 484 / 160)


def test_fragmentation_l_shape():
    """4×4 with a 2×2 occupied corner gives an L-shaped free region.

    By hand: empty area = 12, perimeter = 16 (computed cell-by-cell in
    the module docstring derivation), so F = 256 / (16·12) = 4/3.
    """
    grid = np.zeros((4, 4), dtype=np.int32)
    grid[0:2, 0:2] = 1  # 2×2 occupied at top-left in (y, x) indexing
    np.testing.assert_allclose(fragmentation(grid), 4 / 3)


def test_fragmentation_components_are_4_connected():
    """Diagonally-adjacent empty cells must NOT merge — we use 4-connectivity.

    ``[[1, 0], [0, 1]]`` has two empty cells that touch only at a corner;
    they belong to separate components.
    """
    grid = np.array([[1, 0], [0, 1]], dtype=np.int32)
    labels = _label_components(grid == 0)
    assert int(labels.max()) == 2
    # Each component is a single cell with perimeter 4 (all 4 sides border
    # something). F = (4² + 4²) / (16·2) = 32/32 = 1.0
    np.testing.assert_allclose(fragmentation(grid), 1.0)


def test_fragmentation_series_matches_snapshots():
    """End-to-end: simulator captures snapshots → series has matching ticks
    and a non-trivial F trace. Concrete check: a bin that goes empty → half
    full → empty must produce a peak F at the intermediate snapshot."""
    bs = BinState(W=4, H=4)
    sim = Simulator(bs, BLF())
    items = [
        Item(id=1, w=2, h=2, t_arrive=0, t_depart=10),
    ]
    result = sim.run(items)

    series = fragmentation_series(result)
    # Snapshots at t=0 (placed) and t=10 (removed).
    assert series.t.tolist() == [0, 10]
    # After placement, free region is an L-shape (12 cells, perimeter 16):
    np.testing.assert_allclose(series.value[0], 4 / 3)
    # After departure, bin is empty again — square region:
    np.testing.assert_allclose(series.value[1], 1.0)


def test_fragmentation_stats_empty():
    """No events → all zeros, no division-by-zero."""
    bs = BinState(W=4, H=4)
    sim = Simulator(bs, BLF())
    result = sim.run([])

    stats = fragmentation_stats(result)
    assert stats.peak == 0.0
    assert stats.peak_t == 0
    assert stats.mean == 0.0
    assert stats.series.t.size == 0
