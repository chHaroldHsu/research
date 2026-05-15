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

from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from ..core.bin import BinState


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
