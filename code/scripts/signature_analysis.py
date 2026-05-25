"""Prereq #3–#5: signature-space cluster + mode classification + intrinsic vs induced.

Reads `figures/seed_sweep_raw.csv` (4 heuristic × 5 preset × 30 seeds = 600 rows)
and produces:

  * figures/signature_pca.png      — PCA of (peak_pe, discard, mean/peak) coloured
                                     by (heuristic, preset) cell. Tests #4
                                     (distinguishability) by eye.
  * figures/signature_2d.png        — 2D scatter peak_pe × discard, the two
                                     strong separators. Same colouring.
  * stdout:
      - per-cell mode classification via signature thresholds (#3 quant detector)
      - intrinsic vs workload-induced cross-tab (#5)
      - cluster stats (per-cell σ, nearest-neighbour-cell distance) (#4)

Mode detector definitions (signature-based, no grid topology):
  * Brick-wall       : BLF, peak_pe > 0.55, discard < 0.10
  * Sparse-BLF       : BLF, peak_pe < 0.30 (small_items regime)
  * Top-sliver       : BLF, 0.70 < peak_pe < 0.90, 0.30 < discard < 0.50 (large_items)
  * Horizontal-stripe: shelf family, peak_pe < 0.55, discard > 0.80
  * Sparse-stripe    : shelf family, peak_pe < 0.30, discard < 0.70 (small_items)
  * Item-too-tall    : shelf family, discard > 0.95 (large_items)
  * Unclassified     : anything else

Run from research/code/:
    uv run python scripts/signature_analysis.py
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CSV_PATH = Path(__file__).resolve().parent.parent / "figures" / "seed_sweep_raw.csv"
OUT_DIR = Path(__file__).resolve().parent.parent / "figures"

HEURISTICS = ["BLF", "NFS", "FFS", "BFS"]
PRESETS = ["light_departure", "heavy_departure", "mixed_lifetime", "small_items", "large_items"]


def classify_mode(heuristic: str, peak_pe: float, discard: float, ratio: float) -> str:
    """Signature-based mode detector. Returns the mode label or 'unclassified'."""
    is_shelf = heuristic in {"NFS", "FFS", "BFS"}

    if heuristic == "BLF":
        if peak_pe < 0.30:
            return "Sparse-BLF"
        if 0.70 < peak_pe < 0.90 and 0.30 < discard < 0.50:
            return "Top-sliver"
        if peak_pe > 0.55 and discard < 0.10:
            return "Brick-wall"
        return "BLF-other"

    if is_shelf:
        if discard > 0.95:
            return "Item-too-tall"
        if peak_pe < 0.30 and discard < 0.70:
            return "Sparse-stripe"
        if peak_pe < 0.55 and discard > 0.80:
            return "Horizontal-stripe"
        return "Shelf-other"

    return "unclassified"


def load_csv():
    rows = []
    with CSV_PATH.open() as f:
        for r in csv.DictReader(f):
            rows.append({
                "heuristic": r["heuristic"],
                "preset": r["preset"],
                "seed": int(r["seed"]),
                "peak_pe": float(r["peak_pe"]),
                "mean_pe": float(r["mean_pe"]),
                "mean_over_peak": float(r["mean_over_peak"]),
                "discard_rate": float(r["discard_rate"]),
                "peak_f": float(r["peak_f"]),
                "f_at_peak_pe": float(r["f_at_peak_pe"]),
            })
    return rows


def quant_classify_all(rows):
    """Return list[(heuristic, preset, seed, mode)]."""
    out = []
    for r in rows:
        mode = classify_mode(r["heuristic"], r["peak_pe"], r["discard_rate"], r["mean_over_peak"])
        out.append((r["heuristic"], r["preset"], r["seed"], mode))
    return out


def mode_count_per_cell(classified):
    """For each (heuristic, preset), Counter of modes across seeds."""
    by_cell = defaultdict(Counter)
    for h, p, s, m in classified:
        by_cell[(h, p)][m] += 1
    return by_cell


def print_mode_stability_table(by_cell, total_seeds):
    print("\n=== #3 Mode-stability per (heuristic × preset) cell over", total_seeds, "seeds ===")
    print("Each cell shows: dominant_mode (count/total)")
    col_w = 32
    print(" " * 5 + "  ".join(f"{p:>{col_w}}" for p in PRESETS))
    for h in HEURISTICS:
        cells = []
        for p in PRESETS:
            counter = by_cell.get((h, p), Counter())
            if not counter:
                cells.append("n/a")
                continue
            mode, count = counter.most_common(1)[0]
            cells.append(f"{mode} ({count}/{total_seeds})")
        print(f"{h:<4} " + "  ".join(f"{c:>{col_w}}" for c in cells))


def print_intrinsic_vs_induced(by_cell, total_seeds, *, stable_threshold=0.6):
    print(f"\n=== #5 Intrinsic vs workload-induced (stable = dominant mode ≥ {stable_threshold:.0%} in cell) ===")
    # For each mode, list which (heuristic, preset) cells it dominates.
    mode_to_cells = defaultdict(list)
    for (h, p), counter in by_cell.items():
        if not counter:
            continue
        mode, count = counter.most_common(1)[0]
        if count / total_seeds >= stable_threshold:
            mode_to_cells[mode].append((h, p))

    for mode, cells in sorted(mode_to_cells.items()):
        by_heuristic = defaultdict(list)
        for h, p in cells:
            by_heuristic[h].append(p)
        # Classify mode as intrinsic vs induced:
        #   intrinsic if it appears across >=4 of 5 presets within a heuristic
        #   induced   if only 1-2 presets within a heuristic
        verdict_parts = []
        for h in HEURISTICS:
            ps = by_heuristic.get(h, [])
            if not ps:
                continue
            n_presets = len(ps)
            tag = "intrinsic" if n_presets >= 4 else ("induced" if n_presets <= 2 else "mixed")
            verdict_parts.append(f"{h}:{n_presets}/5 [{tag}] ({','.join(ps)})")
        print(f"  {mode:<22}  {' | '.join(verdict_parts)}")


def pca_2d(X):
    """Manual PCA to first 2 components. X shape (n, d)."""
    Xc = X - X.mean(axis=0)
    cov = (Xc.T @ Xc) / max(len(Xc) - 1, 1)
    w, v = np.linalg.eigh(cov)
    order = np.argsort(w)[::-1]
    w = w[order]
    v = v[:, order]
    proj = Xc @ v[:, :2]
    var_explained = w[:2] / w.sum()
    return proj, var_explained


def cell_separation_stats(rows):
    """For each cell, compute centroid & σ; report nearest-cell distance."""
    feats_by_cell = defaultdict(list)
    for r in rows:
        feats_by_cell[(r["heuristic"], r["preset"])].append(
            [r["peak_pe"], r["discard_rate"], r["mean_over_peak"]]
        )
    centroids = {}
    sigmas = {}
    for cell, feats in feats_by_cell.items():
        arr = np.array(feats)
        centroids[cell] = arr.mean(axis=0)
        sigmas[cell] = arr.std(axis=0)
    return centroids, sigmas


def print_cluster_stats(centroids, sigmas):
    print("\n=== #4 Cluster stats — per-cell σ (peak_pe, discard, mean/peak) ===")
    for h in HEURISTICS:
        for p in PRESETS:
            c = centroids.get((h, p))
            s = sigmas.get((h, p))
            if c is None:
                continue
            print(f"  {h:>4} × {p:<16}  centroid=({c[0]:.3f},{c[1]:.3f},{c[2]:.3f})  σ=({s[0]:.3f},{s[1]:.3f},{s[2]:.3f})")

    # Nearest-cell distance per cell — does each cell have a clearly closest neighbour?
    print("\n=== #4 Nearest-cell Euclidean distance in (peak_pe, discard, mean/peak) ===")
    cells = list(centroids.keys())
    coords = np.array([centroids[c] for c in cells])
    sigmas_arr = np.array([sigmas[c] for c in cells])
    avg_sigma = np.linalg.norm(sigmas_arr, axis=1)  # rough "cell radius"
    for i, cell in enumerate(cells):
        d = np.linalg.norm(coords - coords[i], axis=1)
        d[i] = np.inf
        j = int(np.argmin(d))
        # Ratio: distance to nearest centroid / typical cell radius. < 1 means cells overlap.
        ratio = d[j] / max(avg_sigma[i], 1e-6)
        marker = "  OVERLAP" if ratio < 1.5 else ""
        print(f"  {cell[0]:>4} × {cell[1]:<16}  nearest={cells[j][0]}×{cells[j][1]:<16}  d={d[j]:.3f}  d/σ={ratio:.2f}{marker}")


def plot_2d_signature(rows):
    """2D scatter peak_pe × discard, colour by cell."""
    fig, ax = plt.subplots(figsize=(10, 7))
    colours = plt.cm.tab20(np.linspace(0, 1, len(HEURISTICS) * len(PRESETS)))
    markers = {"BLF": "o", "NFS": "s", "FFS": "^", "BFS": "D"}
    cell_to_colour = {}
    idx = 0
    for h in HEURISTICS:
        for p in PRESETS:
            cell_to_colour[(h, p)] = colours[idx]
            idx += 1
    for r in rows:
        cell = (r["heuristic"], r["preset"])
        ax.scatter(r["peak_pe"], r["discard_rate"],
                   c=[cell_to_colour[cell]], marker=markers[r["heuristic"]],
                   s=30, alpha=0.6, edgecolors="none")
    # Legend: one marker per cell (means).
    for cell, c in cell_to_colour.items():
        h, p = cell
        ax.scatter([], [], c=[c], marker=markers[h], s=60, label=f"{h}×{p}")
    ax.set_xlabel("peak PE")
    ax.set_ylabel("discard rate")
    ax.set_title("Signature space — peak_pe × discard (30 seeds, 4 heur × 5 preset)")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=7, ncol=1)
    fig.tight_layout()
    out = OUT_DIR / "signature_2d.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved: {out}")


def plot_pca(rows):
    X = np.array([[r["peak_pe"], r["discard_rate"], r["mean_over_peak"]] for r in rows])
    proj, var = pca_2d(X)
    fig, ax = plt.subplots(figsize=(10, 7))
    colours = plt.cm.tab20(np.linspace(0, 1, len(HEURISTICS) * len(PRESETS)))
    markers = {"BLF": "o", "NFS": "s", "FFS": "^", "BFS": "D"}
    cell_to_colour = {}
    idx = 0
    for h in HEURISTICS:
        for p in PRESETS:
            cell_to_colour[(h, p)] = colours[idx]
            idx += 1
    for i, r in enumerate(rows):
        cell = (r["heuristic"], r["preset"])
        ax.scatter(proj[i, 0], proj[i, 1],
                   c=[cell_to_colour[cell]], marker=markers[r["heuristic"]],
                   s=30, alpha=0.6, edgecolors="none")
    for cell, c in cell_to_colour.items():
        h, p = cell
        ax.scatter([], [], c=[c], marker=markers[h], s=60, label=f"{h}×{p}")
    ax.set_xlabel(f"PC1 ({var[0]:.0%} var)")
    ax.set_ylabel(f"PC2 ({var[1]:.0%} var)")
    ax.set_title("Signature-space PCA — (peak_pe, discard, mean/peak) (30 seeds)")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=7, ncol=1)
    fig.tight_layout()
    out = OUT_DIR / "signature_pca.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")
    print(f"  PC1 var={var[0]:.1%}  PC2 var={var[1]:.1%}  total={var[:2].sum():.1%}")


def main():
    rows = load_csv()
    seeds = sorted(set(r["seed"] for r in rows))
    print(f"Loaded {len(rows)} runs over seeds {seeds[0]}..{seeds[-1]} ({len(seeds)} total)")

    # #3 — quantitative mode classification
    classified = quant_classify_all(rows)
    by_cell = mode_count_per_cell(classified)
    print_mode_stability_table(by_cell, total_seeds=len(seeds))

    # #5 — intrinsic vs workload-induced cross-tab
    print_intrinsic_vs_induced(by_cell, total_seeds=len(seeds), stable_threshold=0.6)

    # #4 — cluster stats + PCA / 2D scatter
    centroids, sigmas = cell_separation_stats(rows)
    print_cluster_stats(centroids, sigmas)
    plot_2d_signature(rows)
    plot_pca(rows)


if __name__ == "__main__":
    main()
