"""Time-evolution grid for one preset: 4 heuristics × k time samples.

Week-4 mode-naming input: peak-only snapshots can't show how a mode *builds*.
This script picks k snapshots roughly equally spaced across each run (peak
is always included) and renders them as a heuristic × time grid for a single
workload preset. Reading left→right within a row shows how that heuristic's
free-space pattern evolves under the same workload.

Run from research/code/:
    uv run python scripts/demo_timeseries.py
    uv run python scripts/demo_timeseries.py --preset large_items --k 6
    uv run python scripts/demo_timeseries.py --preset heavy_departure --seed 7
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.simulator import Simulator
from dyn2dbp.heuristics import BFS, BLF, FFS, NFS
from dyn2dbp.metrics import fragmentation
from dyn2dbp.viz.grid_view import PanelData, render_h_by_w_grid
from dyn2dbp.viz.snapshot import peak_occupancy_snapshot, sample_snapshots
from dyn2dbp.workloads.presets import PRESETS


HEURISTICS = [("BLF", BLF), ("NFS", NFS), ("FFS", FFS), ("BFS", BFS)]


def run_row(strategy_cls, workload_factory, *, n_items, seed, bin_W, bin_H, k):
    """Run one heuristic on a preset, return k PanelData across time.

    Each panel's annotation carries the tick, the PE on that snapshot, and
    the fragmentation F — so reading down a column compares heuristics at
    a similar time, reading across a row compares time within one heuristic.

    We restrict sampling to the *arrival window* (first event → last arrival
    tick). Past the last arrival the bin only drains, so equally-spaced
    samples otherwise burn most frames on empty grids — wasted for mode
    naming, since modes form *during* placement pressure, not after it ends.
    """
    bin_state = BinState(W=bin_W, H=bin_H)
    sim = Simulator(bin_state, strategy_cls())
    items = workload_factory(n_items=n_items, seed=seed).generate()
    result = sim.run(items)
    items_by_id = {item.id: item for item in items}

    if not result.snapshots:
        return [None] * k

    t_last_arrival = max(item.t_arrive for item in items)
    arrival_window_snaps = [s for s in result.snapshots if s[0] <= t_last_arrival]
    # If the bin emptied before the last arrival (very low load), fall back
    # to all snapshots so we still get something to render.
    snaps_for_sampling = arrival_window_snaps or result.snapshots

    sampled = sample_snapshots(snaps_for_sampling, k=k, include_peak=True)

    # Mark which sample is the peak so the annotation can flag it — modes
    # are most legible at peak occupancy, and the reader should know which
    # column to look at first.
    peak = peak_occupancy_snapshot(result.snapshots)
    peak_t = peak[0] if peak else None

    panels = []
    bin_area = bin_W * bin_H
    for t, grid in sampled:
        pe_here = float((grid != 0).sum()) / bin_area
        f_here = fragmentation(grid)
        tag = "  *peak*" if t == peak_t else ""
        panels.append(PanelData(
            grid=grid,
            items_by_id=items_by_id,
            annotation=f"t={t}{tag}\nPE={pe_here:.0%}  F={f_here:.1f}",
        ))

    # Pad to k so the grid layout stays rectangular when sample_snapshots
    # returned fewer frames than requested (rare; only if the run had < k
    # snapshots in total).
    while len(panels) < k:
        panels.append(None)
    return panels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", type=str, default="heavy_departure",
                        choices=list(PRESETS.keys()),
                        help="Which workload preset to render (default heavy_departure)")
    parser.add_argument("--n", type=int, default=200, help="Items per run (default 200)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (default 42)")
    parser.add_argument("--bin", type=int, default=50, help="Bin side (default 50)")
    parser.add_argument("--k", type=int, default=5, help="Time samples per heuristic (default 5)")
    args = parser.parse_args()

    wl_factory = PRESETS[args.preset]

    rows = [
        run_row(h_cls, wl_factory,
                n_items=args.n, seed=args.seed,
                bin_W=args.bin, bin_H=args.bin, k=args.k)
        for _, h_cls in HEURISTICS
    ]

    row_labels = [name for name, _ in HEURISTICS]
    col_labels = [f"frame {i+1}/{args.k}" for i in range(args.k)]

    suptitle = (
        f"Time evolution — {args.preset} "
        f"(n={args.n}, seed={args.seed}, bin={args.bin}×{args.bin})"
    )
    fig = render_h_by_w_grid(rows, row_labels, col_labels, suptitle=suptitle)

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"timeseries_{args.preset}_seed{args.seed}.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    print(f"Saved: {out_path}")

    print()
    for r, (h_name, _) in enumerate(HEURISTICS):
        for c in range(args.k):
            panel = rows[r][c]
            note = panel.annotation.replace("\n", "  ") if panel else "n/a"
            print(f"  {h_name:>4}  frame {c+1}/{args.k}  {note}")


if __name__ == "__main__":
    main()
