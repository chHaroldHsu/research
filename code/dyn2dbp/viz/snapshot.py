"""Static rendering of a BinState — one figure per bin instant.

This is the workhorse for visual mode-spotting in week 3: a grid of these
panels (4 heuristics × 5 workloads) is exactly the H × W matrix that the
factorial design produces, so the human eye can read off candidate failure
modes before we formalize their signatures.

Color encoding by *lifetime* (not item id) is deliberate. Under variant E
the hypothesis is that long-lived items in adverse positions cause the
worst fragmentation; lifetime-coloring makes that pattern visible at a
glance instead of having to cross-reference an id legend.
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from ..core.bin import BinState
from ..core.item import Item


def render_bin(
    bin_state: BinState,
    title: Optional[str] = None,
    ax: Optional[Axes] = None,
    color_by: str = "lifetime",
) -> Axes:
    """Draw the bin's current placed items.

    Parameters
    ----------
    bin_state
        State to render. Read-only — never mutated.
    title
        Optional title above the panel.
    ax
        Existing matplotlib Axes to draw into. If None, a new figure is
        created. Passing an Axes is how we'll build the H × W subplot grid
        later without touching this function.
    color_by
        ``"lifetime"`` — viridis-mapped on item.lifetime (default; matches
        the variant-E hypothesis that lifetime drives failure shape).
        ``"id"`` — cycle through a categorical palette by item id, useful
        for debugging which placement landed where.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))

    # Bin outline. Drawn first so item rectangles overlay on top of it.
    ax.add_patch(Rectangle(
        (0, 0), bin_state.W, bin_state.H,
        fill=False, edgecolor="black", linewidth=1.5,
    ))

    cmap = plt.get_cmap("viridis")

    # Pre-compute the max lifetime for normalization. If the bin is empty
    # we still need a sane denominator to avoid a divide-by-zero.
    if color_by == "lifetime" and bin_state.placed:
        max_lifetime = max(item.lifetime for item, _ in bin_state.placed.values())
        max_lifetime = max(max_lifetime, 1)
    else:
        max_lifetime = 1

    for item, pos in bin_state.placed.values():
        if color_by == "lifetime":
            c = cmap(item.lifetime / max_lifetime)
        else:
            # Modulo 32 keeps adjacent ids visually distinguishable when
            # the bin has lots of small items.
            c = cmap((item.id % 32) / 32)
        ax.add_patch(Rectangle(
            (pos.x, pos.y), item.w, item.h,
            facecolor=c, edgecolor="white", linewidth=0.5, alpha=0.85,
        ))

    # A small margin so the bin outline isn't flush against the axis.
    ax.set_xlim(-1, bin_state.W + 1)
    ax.set_ylim(-1, bin_state.H + 1)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if title:
        ax.set_title(title)
    return ax


def render_grid(
    grid: np.ndarray,
    title: Optional[str] = None,
    ax: Optional[Axes] = None,
    items_by_id: Optional[Dict[int, Item]] = None,
    color_by: str = "lifetime",
) -> Axes:
    """Render a snapshot grid directly (no BinState needed).

    Why this exists: the Simulator stashes grid snapshots after every event,
    but the *live* BinState is empty at the end of a run (every item that
    arrived also departed). To visualise peak occupancy or any mid-run state,
    we need to render from a stored grid — and BinState's bookkeeping is
    long gone by then.

    Parameters
    ----------
    grid
        2D int array as produced by ``BinState.snapshot()``. Cell value 0
        means empty; any positive value is an item id.
    title
        Optional title above the panel.
    ax
        Optional matplotlib Axes to draw into.
    items_by_id
        Optional ``{item_id: Item}`` map. If provided and
        ``color_by == "lifetime"``, cells are coloured by the item's
        lifetime (matches ``render_bin`` semantics for variant E). If
        omitted, falls back to id-based colouring.
    color_by
        ``"lifetime"`` (default) or ``"id"``.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))

    H, W = grid.shape

    # Build a float display matrix: empty cells → NaN (rendered white via
    # the colormap's "bad" colour); non-empty cells → a value in [0, 1].
    display = np.full(grid.shape, np.nan, dtype=float)

    if color_by == "lifetime" and items_by_id:
        max_lt = max(item.lifetime for item in items_by_id.values()) or 1
        for cell_id, item in items_by_id.items():
            display[grid == cell_id] = item.lifetime / max_lt
    else:
        # Categorical id colouring: ids mod 20 keeps adjacent items
        # visually distinguishable without exhausting the palette.
        mask = grid != 0
        display[mask] = (grid[mask] % 20) / 20.0

    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("white")
    ax.imshow(
        display,
        origin="lower",          # y=0 at bottom — matches BLF / Position convention
        cmap=cmap,
        vmin=0.0, vmax=1.0,
        extent=(0, W, 0, H),
        interpolation="nearest",
    )

    ax.add_patch(Rectangle(
        (0, 0), W, H,
        fill=False, edgecolor="black", linewidth=1.5,
    ))
    ax.set_xlim(-1, W + 1)
    ax.set_ylim(-1, H + 1)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if title:
        ax.set_title(title)
    return ax


def peak_occupancy_snapshot(snapshots):
    """Return (t, grid) of the highest-occupancy snapshot, or None if empty.

    Convenience for demos / sanity checks. Picking peak occupancy gives the
    most-loaded frame, which is where failure modes are easiest to spot.
    """
    if not snapshots:
        return None
    return max(snapshots, key=lambda s: np.count_nonzero(s[1]))
