"""Structural tests for the H × W grid view.

We don't compare rendered images — that's brittle across matplotlib versions
and adds nothing. We *do* check the structural contracts (axis count, label
validation, None-cell handling), because those are exactly what week-3's
factorial-sweep driver will rely on.

The Agg backend is forced before importing pyplot so the suite runs in
headless CI without a display.
"""
import matplotlib

matplotlib.use("Agg")  # noqa: E402 — must come before pyplot import

import matplotlib.pyplot as plt
import numpy as np
import pytest

from dyn2dbp.core.item import Item
from dyn2dbp.viz.grid_view import PanelData, render_h_by_w_grid


def _tiny_panel() -> PanelData:
    """Smallest possible non-trivial panel: a 2×2 grid with one cell occupied.

    Kept minimal so test failures point at layout logic, not at fancy
    rendering details that belong in snapshot.py's domain.
    """
    grid = np.array([[1, 0], [0, 0]], dtype=np.int32)
    items_by_id = {1: Item(id=1, w=1, h=1, t_arrive=0, t_depart=5)}
    return PanelData(grid=grid, items_by_id=items_by_id, annotation="PE=25%")


def test_grid_axes_shape_matches_panels():
    """A 2 × 3 panel grid produces a 2 × 3 axes array."""
    panels = [[_tiny_panel() for _ in range(3)] for _ in range(2)]
    fig = render_h_by_w_grid(
        panels,
        row_labels=["BLF", "NFDH"],
        col_labels=["w1", "w2", "w3"],
    )
    try:
        axes = fig.get_axes()
        assert len(axes) == 6
    finally:
        plt.close(fig)


def test_none_cell_renders_without_crash():
    """A None cell renders the 'n/a' placeholder instead of raising.

    Important: the factorial driver should keep producing the rest of the
    grid even if one (heuristic, workload) cell collapses (e.g. no
    placements). Crashing on None would force callers to special-case
    empty cells in the driver, which is exactly the wrong place for it.
    """
    panels = [[_tiny_panel(), None]]
    fig = render_h_by_w_grid(
        panels,
        row_labels=["BLF"],
        col_labels=["ok", "empty"],
    )
    try:
        # The "n/a" goes onto the second axis. Verify it's there so a future
        # refactor doesn't silently drop the placeholder.
        ax_empty = fig.get_axes()[1]
        texts = [t.get_text() for t in ax_empty.texts]
        assert "n/a" in texts
    finally:
        plt.close(fig)


def test_row_label_length_mismatch_raises():
    panels = [[_tiny_panel()]]
    with pytest.raises(ValueError, match="row_labels"):
        render_h_by_w_grid(
            panels,
            row_labels=["BLF", "extra"],
            col_labels=["w1"],
        )


def test_col_label_length_mismatch_raises():
    panels = [[_tiny_panel(), _tiny_panel()]]
    with pytest.raises(ValueError, match="col_labels"):
        render_h_by_w_grid(
            panels,
            row_labels=["BLF"],
            col_labels=["only_one"],
        )


def test_ragged_panels_row_raises():
    """All rows must have the same number of cells.

    A ragged grid almost certainly indicates a driver bug (one heuristic
    forgot to run a workload). Loud failure is correct — we'd rather see
    the bug than silently render a misaligned grid.
    """
    panels = [
        [_tiny_panel(), _tiny_panel()],
        [_tiny_panel()],
    ]
    with pytest.raises(ValueError, match="row 1"):
        render_h_by_w_grid(
            panels,
            row_labels=["a", "b"],
            col_labels=["w1", "w2"],
        )


def test_empty_panels_raises():
    with pytest.raises(ValueError, match="non-empty"):
        render_h_by_w_grid([], row_labels=[], col_labels=[])
