"""Demo: run a hand-crafted 10-item workload through BLF on a 50×50 bin.

Purpose: end-to-end smoke test. Verifies that Item → Simulator → BinState →
BLF → snapshot rendering all hang together. If this script crashes, the
pipeline is broken before we even reach the real workload generator.

Run from the repo root:
    uv run python scripts/demo_blf.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow `python scripts/demo_blf.py` from anywhere — add repo root to sys.path
# so the `dyn2dbp` package resolves without an editable install.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.item import Item
from dyn2dbp.core.simulator import Simulator
from dyn2dbp.heuristics.blf import BLF
from dyn2dbp.viz.snapshot import peak_occupancy_snapshot, render_grid


def main() -> None:
    bin_state = BinState(W=50, H=50)
    strategy = BLF()

    # Hand-crafted items: sizes range from 5×5 to 25×15, lifetimes
    # interleave so we get both arrivals-into-occupied-bin and arrivals-
    # into-just-freed-space. This is the minimum case that exercises the
    # departure-before-arrival tie-break rule.
    items = [
        Item(id=1,  w=15, h=10, t_arrive=0,  t_depart=20),
        Item(id=2,  w=20, h=15, t_arrive=1,  t_depart=10),
        Item(id=3,  w=10, h=20, t_arrive=2,  t_depart=25),
        Item(id=4,  w=8,  h=8,  t_arrive=3,  t_depart=12),
        Item(id=5,  w=12, h=18, t_arrive=4,  t_depart=30),
        Item(id=6,  w=25, h=10, t_arrive=11, t_depart=22),  # after #2 leaves
        Item(id=7,  w=6,  h=6,  t_arrive=13, t_depart=28),
        Item(id=8,  w=10, h=10, t_arrive=15, t_depart=40),
        Item(id=9,  w=18, h=5,  t_arrive=21, t_depart=35),  # after #1 leaves
        Item(id=10, w=5,  h=15, t_arrive=23, t_depart=40),
    ]

    sim = Simulator(bin_state, strategy)
    result = sim.run(items)

    print(f"Strategy:          {strategy.name}")
    print(f"Bin:               {bin_state.W}×{bin_state.H}")
    print(f"Items submitted:   {len(items)}")
    print(f"Discarded:         {result.discarded_count}")
    print(f"Final occupancy:   {result.final_occupancy:.2%}")
    print(f"Snapshots:         {len(result.snapshots)}")
    print()
    print("Event log (first 20):")
    for e in result.events[:20]:
        pos_str = f" @({e.position.x:2d},{e.position.y:2d})" if e.position else ""
        flag = "OK " if e.success else "XX "
        print(f"  t={e.t:3d}  {flag}{e.event_type:9s} item#{e.item_id:<3d}{pos_str}  occ={e.occupancy_after:.2%}")

    # End-of-run bin is empty (every item that arrives also departs), so
    # render the peak-occupancy snapshot — that's where the bin is loaded.
    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(exist_ok=True)
    items_by_id = {item.id: item for item in items}
    peak = peak_occupancy_snapshot(result.snapshots)
    if peak is None:
        print("\nNo snapshots captured — skipping figure.")
        return
    peak_t, peak_grid = peak
    peak_pe = np.count_nonzero(peak_grid) / (bin_state.W * bin_state.H)
    fig, ax = plt.subplots(figsize=(7, 7))
    render_grid(
        peak_grid,
        title=f"BLF demo — peak state at t={peak_t} (PE={peak_pe:.2%})",
        ax=ax,
        items_by_id=items_by_id,
    )
    out_path = out_dir / "demo_blf_peak.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    print(f"\nSaved peak snapshot (t={peak_t}, PE={peak_pe:.2%}): {out_path}")


if __name__ == "__main__":
    main()
