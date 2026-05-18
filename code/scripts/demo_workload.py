"""Demo: pick a preset, generate items, push them through BLF, save snapshot.

This is the first real "workload" demo — unlike scripts/demo_blf.py which
uses 10 hand-crafted items, this one runs a generated 200-item Poisson
workload and shows what BLF's bin actually looks like at the end.

Run from research/code/:
    uv run python scripts/demo_workload.py
    uv run python scripts/demo_workload.py heavy_departure
    uv run python scripts/demo_workload.py mixed_lifetime --n 300
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python scripts/demo_workload.py` from anywhere — add repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
import numpy as np

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.simulator import Simulator
from dyn2dbp.heuristics.blf import BLF
from dyn2dbp.viz.snapshot import peak_occupancy_snapshot, render_grid
from dyn2dbp.workloads.presets import PRESETS


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "preset",
        nargs="?",
        default="heavy_departure",
        choices=sorted(PRESETS.keys()),
        help="Workload preset to run (default: heavy_departure)",
    )
    parser.add_argument("--n", type=int, default=200, help="Number of items (default 200)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (default 42)")
    parser.add_argument("--bin", type=int, default=50, help="Bin side length (default 50)")
    args = parser.parse_args()

    bin_state = BinState(W=args.bin, H=args.bin)
    workload = PRESETS[args.preset](n_items=args.n, seed=args.seed)
    items = workload.generate()

    sim = Simulator(bin_state, BLF())
    result = sim.run(items)

    placed = len(items) - result.discarded_count
    print(f"Preset:           {args.preset}")
    print(f"Workload config:  {workload.config.short_name()}")
    print(f"Bin:              {args.bin}×{args.bin}")
    print(f"Items generated:  {len(items)}")
    print(f"Items placed:     {placed} ({placed / len(items):.1%})")
    print(f"Items discarded:  {result.discarded_count} ({result.discarded_count / len(items):.1%})")
    print(f"Snapshots:        {len(result.snapshots)}")
    print(f"Final occupancy:  {result.final_occupancy:.2%}")

    # Lifetime stats — useful for sanity-checking the preset choice.
    lifetimes = [i.lifetime for i in items]
    print()
    print(f"Lifetime stats:   min={min(lifetimes)}  mean={sum(lifetimes)/len(lifetimes):.1f}  max={max(lifetimes)}")
    sizes = [i.w * i.h for i in items]
    print(f"Item area stats:  min={min(sizes)}  mean={sum(sizes)/len(sizes):.1f}  max={max(sizes)}")

    # The simulator processes every arrival AND every departure, so the live
    # bin_state is empty at end-of-run (everything that came in also left).
    # The interesting visuals are the mid-run snapshots — render the peak.
    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(exist_ok=True)
    items_by_id = {item.id: item for item in items}

    peak = peak_occupancy_snapshot(result.snapshots)
    if peak is None:
        print("\nNo snapshots captured (nothing placed) — skipping figure.")
        return

    peak_t, peak_grid = peak
    peak_pe = np.count_nonzero(peak_grid) / (args.bin * args.bin)

    fig, ax = plt.subplots(figsize=(7, 7))
    title = (
        f"BLF × {args.preset}  (n={args.n}, seed={args.seed})\n"
        f"peak occupancy at t={peak_t}, PE={peak_pe:.2%}"
    )
    render_grid(peak_grid, title=title, ax=ax, items_by_id=items_by_id)
    out_path = out_dir / f"demo_workload_{args.preset}_seed{args.seed}.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    print(f"\nSaved peak snapshot (t={peak_t}, PE={peak_pe:.2%}): {out_path}")


if __name__ == "__main__":
    main()
