"""H × W panel grid — heuristics × workloads, one bin snapshot per cell.

Week-3's main visual artefact for failure-mode taxonomy: rows are heuristics,
columns are workload presets, each cell is a peak-occupancy snapshot. The
grid layout *itself* enforces the comparison — a recurring shape across one
row but not another (or one column but not another) is a taxonomy candidate.

Pure orchestrator: every cell is drawn by ``render_grid`` from snapshot.py.
This module only owns layout — picking subplot dimensions, attaching row
and column labels, slotting per-cell annotations under the column header.
That separation matters because week-3 will iterate on the per-cell visual
(e.g. overlaying free-region contours) without touching grid layout code.

Empty cells are an intentional supported case: a (heuristic, workload) that
produced no placements yields a blank panel with "n/a", not a crash — we
want the grid to keep rendering when one cell degenerates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from ..core.item import Item
from .snapshot import render_grid


@dataclass(frozen=True)
class PanelData:
    """One cell of the H × W grid.

    ``annotation`` is the per-cell subtitle that appears under the column
    header. Use it for headline numbers (peak PE, discard rate, snapshot
    tick) — those need to sit next to the picture, not in a side table.
    """
    grid: np.ndarray
    items_by_id: Dict[int, Item]
    annotation: str = ""


def render_h_by_w_grid(
    panels: Sequence[Sequence[Optional[PanelData]]],
    row_labels: Sequence[str],
    col_labels: Sequence[str],
    *,
    suptitle: Optional[str] = None,
    color_by: str = "lifetime",
    figsize_per_panel: Tuple[float, float] = (3.0, 3.0),
) -> Figure:
    """Render a rows × cols matrix of bin snapshots.

    Parameters
    ----------
    panels
        2D sequence (rows × cols). A None cell renders a blank axis with an
        "n/a" placeholder so the grid keeps its shape when one combination
        degenerates.
    row_labels, col_labels
        Must match ``len(panels)`` and ``len(panels[0])``. Row labels go on
        the left of column 0; column labels go on top of row 0.
    suptitle
        Figure-level title.
    color_by
        Forwarded to ``render_grid`` — ``"lifetime"`` (default, matches the
        variant-E hypothesis that lifetime drives failure shape) or ``"id"``.
    figsize_per_panel
        Per-cell ``(width, height)`` in inches. Total figure size scales
        with the grid dimensions.

    Returns
    -------
    matplotlib.figure.Figure
        Caller owns ``savefig`` / ``show`` / ``close``.
    """
    n_rows = len(panels)
    n_cols = len(panels[0]) if n_rows else 0
    if n_rows == 0 or n_cols == 0:
        raise ValueError("panels must be non-empty")
    if len(row_labels) != n_rows:
        raise ValueError(
            f"row_labels length {len(row_labels)} != n_rows {n_rows}"
        )
    if len(col_labels) != n_cols:
        raise ValueError(
            f"col_labels length {len(col_labels)} != n_cols {n_cols}"
        )
    for r, row in enumerate(panels):
        if len(row) != n_cols:
            raise ValueError(
                f"panels row {r} has {len(row)} cells, expected {n_cols}"
            )

    w_per, h_per = figsize_per_panel
    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(w_per * n_cols, h_per * n_rows),
        squeeze=False,
        constrained_layout=True,  # handles suptitle + per-cell titles cleanly
    )

    for r in range(n_rows):
        for c in range(n_cols):
            ax = axes[r][c]
            panel = panels[r][c]
            header = col_labels[c] if r == 0 else ""

            if panel is None:
                if header:
                    ax.set_title(header, fontsize=10)
                ax.text(
                    0.5, 0.5, "n/a",
                    ha="center", va="center",
                    transform=ax.transAxes,
                    color="gray", fontsize=12,
                )
                ax.set_xticks([])
                ax.set_yticks([])
            else:
                # Column header goes above as the title (top row only);
                # per-cell annotation goes *below* as the xlabel. Stacking
                # everything in the title made wide annotations overflow into
                # neighbouring panels — separating them lets each text element
                # claim its own slot.
                render_grid(
                    panel.grid,
                    title=header if header else None,
                    ax=ax,
                    items_by_id=panel.items_by_id,
                    color_by=color_by,
                )
                ax.set_xlabel(panel.annotation, fontsize=9)
                ax.set_ylabel("")
                ax.set_xticks([])
                ax.set_yticks([])

            # Row label only on the leftmost column. Goes after render_grid
            # so it overrides the "y" label that render_grid sets.
            if c == 0:
                ax.set_ylabel(
                    row_labels[r], rotation=90, labelpad=8, fontsize=11
                )

    if suptitle:
        fig.suptitle(suptitle, fontsize=12)

    return fig
