"""Seed sweep — 4 heuristics × 5 presets × N seeds.

Purpose: validate whether the seed=42 results in the 4×5 grid (FFS ≈ BFS, in
particular) are stable across seeds, or seed-specific artefacts.

Metrics collected per run:
  * peak PE                      (occupancy at the moment of densest packing)
  * mean PE  (time-weighted)     (average occupancy over the run)
  * mean/peak PE ratio           (third mode-signature element)
  * discard rate (overall)       (fraction of arrivals dropped)
  * peak fragmentation F         (peak shape factor of free space)
  * F at peak-PE time            (shape factor when the bin is densest)

Outputs:
  * figures/seed_sweep_raw.csv  — one row per (heuristic, preset, seed)
  * stdout — mean ± std table for each metric, grouped by metric

Run from research/code/:
    uv run python scripts/seed_sweep.py
    uv run python scripts/seed_sweep.py --seeds 1 2 3 4 5 --n 200
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from dyn2dbp.core.bin import BinState
from dyn2dbp.core.simulator import Simulator
from dyn2dbp.heuristics import BFS, BLF, FFS, NFS
from dyn2dbp.metrics import (
    discard_stats,
    fragmentation,
    fragmentation_stats,
    pe_stats,
)
from dyn2dbp.workloads.presets import PRESETS


HEURISTICS = [("BLF", BLF), ("NFS", NFS), ("FFS", FFS), ("BFS", BFS)]


def run_once(strategy_cls, workload_factory, *, n_items, seed, bin_W, bin_H):
    """Run one (heuristic, preset, seed) and return a metrics dict."""
    bin_state = BinState(W=bin_W, H=bin_H)
    sim = Simulator(bin_state, strategy_cls())
    items = workload_factory(n_items=n_items, seed=seed).generate()
    result = sim.run(items)

    pe = pe_stats(result)
    disc = discard_stats(result)
    frag = fragmentation_stats(result)

    # Fragmentation at the *time of peak PE*. Snapshots are stored on every
    # successful event, so we look up the snapshot whose t matches PE peak_t.
    # If multiple snapshots share that tick (e.g. simultaneous events), the
    # last one wins — that's the post-event state, which is what we want.
    f_at_peak_pe = 0.0
    if pe.peak > 0 and result.snapshots:
        for t, grid in result.snapshots:
            if t == pe.peak_t:
                f_at_peak_pe = fragmentation(grid)

    ratio = (pe.mean / pe.peak) if pe.peak > 0 else 0.0

    return {
        "peak_pe": pe.peak,
        "mean_pe": pe.mean,
        "mean_over_peak": ratio,
        "discard_rate": disc.rate_overall,
        "peak_f": frag.peak,
        "f_at_peak_pe": f_at_peak_pe,
    }


def aggregate(rows, heuristics, presets):
    """Group per-run rows into a (heuristic, preset) -> {metric: (mean, std)} dict."""
    out = {}
    for h_name, _ in heuristics:
        for p_name, _ in presets:
            cell_rows = [r for r in rows if r["heuristic"] == h_name and r["preset"] == p_name]
            if not cell_rows:
                continue
            agg = {}
            for key in ["peak_pe", "mean_pe", "mean_over_peak", "discard_rate", "peak_f", "f_at_peak_pe"]:
                vals = np.array([r[key] for r in cell_rows], dtype=np.float64)
                agg[key] = (float(vals.mean()), float(vals.std(ddof=0)))
            out[(h_name, p_name)] = agg
    return out


def print_metric_table(agg, heuristics, presets, metric, *, fmt="{:.3f}", title=None):
    """Print a (heuristic × preset) table for one metric, mean ± std per cell."""
    header_title = title or metric
    col_w = 22
    name_w = 4
    print(f"\n=== {header_title} ===")
    head = " " * name_w + "  " + "  ".join(f"{p:>{col_w}}" for p, _ in presets)
    print(head)
    for h_name, _ in heuristics:
        row_cells = []
        for p_name, _ in presets:
            key = (h_name, p_name)
            if key not in agg:
                row_cells.append("n/a")
                continue
            mean, std = agg[key][metric]
            row_cells.append(f"{fmt.format(mean)} ± {fmt.format(std)}")
        print(f"{h_name:<{name_w}}  " + "  ".join(f"{c:>{col_w}}" for c in row_cells))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 11)),
                        help="Seeds to sweep (default: 1..10)")
    parser.add_argument("--n", type=int, default=200, help="Items per run (default 200)")
    parser.add_argument("--bin", type=int, default=50, help="Bin side (default 50)")
    args = parser.parse_args()

    preset_items = list(PRESETS.items())
    print(f"Sweeping {len(HEURISTICS)} heuristics × {len(preset_items)} presets "
          f"× {len(args.seeds)} seeds = {len(HEURISTICS)*len(preset_items)*len(args.seeds)} runs")
    print(f"n_items={args.n}, bin={args.bin}×{args.bin}, seeds={args.seeds}")

    rows = []
    for seed in args.seeds:
        for h_name, h_cls in HEURISTICS:
            for p_name, wl_factory in preset_items:
                metrics = run_once(
                    h_cls, wl_factory,
                    n_items=args.n, seed=seed,
                    bin_W=args.bin, bin_H=args.bin,
                )
                rows.append({"heuristic": h_name, "preset": p_name, "seed": seed, **metrics})

    # ---- raw CSV (one row per run) ------------------------------------
    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(exist_ok=True)
    csv_path = out_dir / "seed_sweep_raw.csv"
    fieldnames = ["heuristic", "preset", "seed",
                  "peak_pe", "mean_pe", "mean_over_peak",
                  "discard_rate", "peak_f", "f_at_peak_pe"]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nRaw runs → {csv_path}")

    # ---- aggregate ----------------------------------------------------
    agg = aggregate(rows, HEURISTICS, preset_items)
    print_metric_table(agg, HEURISTICS, preset_items, "peak_pe",
                       fmt="{:.3f}", title="Peak PE (mean ± std)")
    print_metric_table(agg, HEURISTICS, preset_items, "discard_rate",
                       fmt="{:.3f}", title="Discard rate (mean ± std)")
    print_metric_table(agg, HEURISTICS, preset_items, "mean_over_peak",
                       fmt="{:.3f}", title="mean/peak PE ratio (mean ± std)")
    print_metric_table(agg, HEURISTICS, preset_items, "peak_f",
                       fmt="{:.2f}", title="Peak fragmentation F (mean ± std)")
    print_metric_table(agg, HEURISTICS, preset_items, "f_at_peak_pe",
                       fmt="{:.2f}", title="F at peak-PE time (mean ± std)")

    # ---- FFS vs BFS overlap check -------------------------------------
    print("\n=== FFS vs BFS overlap (peak PE) ===")
    for p_name, _ in preset_items:
        ffs = agg.get(("FFS", p_name), {}).get("peak_pe")
        bfs = agg.get(("BFS", p_name), {}).get("peak_pe")
        if ffs is None or bfs is None:
            continue
        ffs_m, ffs_s = ffs
        bfs_m, bfs_s = bfs
        gap = abs(ffs_m - bfs_m)
        # "Indistinguishable" heuristic: gap <= max(σ_FFS, σ_BFS).
        # This is the 1σ rule mentioned in the original discussion — easy
        # to read off and conservative enough for a sanity check (not a
        # formal statistical test, just a triage signal).
        verdict = "≈ same" if gap <= max(ffs_s, bfs_s) else "DIFFERS"
        print(f"  {p_name:<16}  FFS={ffs_m:.3f}±{ffs_s:.3f}  "
              f"BFS={bfs_m:.3f}±{bfs_s:.3f}  Δ={gap:.3f}  → {verdict}")


if __name__ == "__main__":
    main()
