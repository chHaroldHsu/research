"""Prereq #3: render 4×5 grid_view across N seeds for visual mode-stability check.

For each seed, generates one grid_view PNG (4 heuristics × 5 presets), saved to
figures/seed_grid/grid_view_seed{N}.png. Use to count how often each visual mode
candidate appears across seeds (target: stable = appears in ≥60% of seeds).

Run from research/code/:
    uv run python scripts/mode_stability_sweep.py --seeds $(seq 1 30)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.simulator import Simulator
from dyn2dbp.heuristics import BFS, BLF, FFS, NFS
from dyn2dbp.metrics import discard_stats, fragmentation, pe_stats
from dyn2dbp.viz.grid_view import PanelData, render_h_by_w_grid
from dyn2dbp.viz.snapshot import peak_occupancy_snapshot
from dyn2dbp.workloads.presets import PRESETS


HEURISTICS = [("BLF", BLF), ("NFS", NFS), ("FFS", FFS), ("BFS", BFS)]


def run_cell(strategy_cls, workload_factory, *, n_items, seed, bin_W, bin_H):
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


def render_seed(seed: int, *, n_items: int, bin_side: int, out_dir: Path) -> Path:
    preset_items = list(PRESETS.items())
    panels = [
        [
            run_cell(strat_cls, wl_factory,
                     n_items=n_items, seed=seed,
                     bin_W=bin_side, bin_H=bin_side)
            for _, wl_factory in preset_items
        ]
        for _, strat_cls in HEURISTICS
    ]
    row_labels = [name for name, _ in HEURISTICS]
    col_labels = [name for name, _ in preset_items]
    suptitle = (
        f"Peak-occupancy snapshots — H × W scan "
        f"(n={n_items}, seed={seed}, bin={bin_side}×{bin_side})"
    )
    fig = render_h_by_w_grid(panels, row_labels, col_labels, suptitle=suptitle)
    out_path = out_dir / f"grid_view_seed{seed:02d}.png"
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 31)))
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--bin", type=int, default=50)
    args = parser.parse_args()

    out_dir = Path(__file__).resolve().parent.parent / "figures" / "seed_grid"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Rendering {len(args.seeds)} seeds → {out_dir}")
    for seed in args.seeds:
        path = render_seed(seed, n_items=args.n, bin_side=args.bin, out_dir=out_dir)
        print(f"  seed={seed:2d} → {path.name}")
    print(f"\nDone. {len(args.seeds)} PNGs in {out_dir}")


if __name__ == "__main__":
    main()
