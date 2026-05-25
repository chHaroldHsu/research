"""Demo: H × W peak-snapshot grid (heuristics × workload presets).

Today: 1 × 5 — BLF across all 5 PRESETS. Once NFDH / FFDH / Shelf land in
week 3, the same script becomes the 4 × 5 factorial-scan deliverable
with zero structural changes — just append heuristics to the list below.

Run from research/code/:
    uv run python scripts/demo_grid_view.py
    uv run python scripts/demo_grid_view.py --n 300 --seed 7
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.simulator import Simulator
from dyn2dbp.heuristics import BFS, BLF, FFS, NFS
from dyn2dbp.metrics import discard_stats, fragmentation, pe_stats
from dyn2dbp.viz.grid_view import PanelData, render_h_by_w_grid
from dyn2dbp.viz.snapshot import peak_occupancy_snapshot
from dyn2dbp.workloads.presets import PRESETS


def run_cell(strategy_cls, workload_factory, *, n_items, seed, bin_W, bin_H):
    """Run one (heuristic, workload) cell and pack it into a PanelData.

    Annotation carries the three mode-signature components:
      * peak PE        — densest packing achieved
      * discard rate   — overall arrival drop fraction
      * F@peak         — fragmentation shape factor on the peak-occupancy
                         snapshot (the very grid we're visualising), so the
                         number lines up 1:1 with what the reader sees
      * mean/peak      — time-weighted mean PE divided by peak PE; low ratio
                         means the bin is dense only briefly
    """
    bin_state = BinState(W=bin_W, H=bin_H)
    sim = Simulator(bin_state, strategy_cls())
    items = workload_factory(n_items=n_items, seed=seed).generate()
    result = sim.run(items)

    peak = peak_occupancy_snapshot(result.snapshots)
    if peak is None:
        return None
    peak_t, peak_grid = peak

    pe = pe_stats(result)
    disc = discard_stats(result)
    f_peak = fragmentation(peak_grid)
    ratio = (pe.mean / pe.peak) if pe.peak > 0 else 0.0
    annotation = (
        f"t={peak_t}  peak PE={pe.peak:.0%}  discard={disc.rate_overall:.0%}\n"
        f"F@peak={f_peak:.1f}  mean/peak={ratio:.2f}"
    )
    return PanelData(
        grid=peak_grid,
        items_by_id={item.id: item for item in items},
        annotation=annotation,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=200, help="Items per cell (default 200)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (default 42)")
    parser.add_argument("--bin", type=int, default=50, help="Bin side (default 50)")
    args = parser.parse_args()

    heuristics = [("BLF", BLF), ("NFS", NFS), ("FFS", FFS), ("BFS", BFS)]
    preset_items = list(PRESETS.items())  # ordered as in PRESETS dict

    panels = [
        [
            run_cell(
                strat_cls, wl_factory,
                n_items=args.n, seed=args.seed,
                bin_W=args.bin, bin_H=args.bin,
            )
            for _, wl_factory in preset_items
        ]
        for _, strat_cls in heuristics
    ]
    row_labels = [name for name, _ in heuristics]
    col_labels = [name for name, _ in preset_items]

    suptitle = (
        f"Peak-occupancy snapshots — H × W scan "
        f"(n={args.n}, seed={args.seed}, bin={args.bin}×{args.bin})"
    )
    fig = render_h_by_w_grid(
        panels, row_labels, col_labels, suptitle=suptitle,
    )

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"grid_view_seed{args.seed}.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    print(f"Saved: {out_path}")

    # Brief stdout summary — easier to skim than the figure when iterating
    # on workload parameters.
    print()
    for r, (h_name, _) in enumerate(heuristics):
        for c, (p_name, _) in enumerate(preset_items):
            panel = panels[r][c]
            note = panel.annotation if panel is not None else "n/a (no placements)"
            print(f"  {h_name:>4} × {p_name:<16}  {note}")


if __name__ == "__main__":
    main()
