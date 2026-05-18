"""Workload presets — one per axis of the variant-E factorial design.

Each preset is named after the candidate failure mode it's *hypothesized*
to surface most strongly. Whether that hypothesis holds is exactly what
week-3's H × W scan will test — see ``memory/research-decisions.md``
2026-05-14 "factorial design" section for the experimental rationale.

Calibration note: defaults are tuned for a 50×50 bin. If you change bin
size in your experiment, scale ``size_w_range`` / ``size_h_range`` and
``mean_lifetime`` proportionally so the steady-state occupancy stays
similar.
"""
from __future__ import annotations

from .synthetic import SyntheticWorkload, WorkloadConfig


def light_departure(n_items: int = 500, seed: int = 42) -> SyntheticWorkload:
    """Long-lived items, slow arrivals.

    Hypothesis: items pile up at the bottom-left and stay there. Long-lived
    bottom-row tenants block whole columns ⇒ candidate **Boundary Lockout**.

    Steady-state load = λ × mean_lifetime ≈ 0.2 × 100 = 20 concurrent items.
    """
    return SyntheticWorkload(WorkloadConfig(
        n_items=n_items,
        arrival_rate=0.2,
        size_w_range=(3, 15),
        size_h_range=(3, 15),
        lifetime_dist="exponential",
        mean_lifetime=100.0,
        seed=seed,
    ))


def heavy_departure(n_items: int = 500, seed: int = 42) -> SyntheticWorkload:
    """Short-lived items, fast arrivals — churn-heavy regime.

    Hypothesis: items arrive faster than they leave; voids appear constantly
    in the middle layers of the bin ⇒ candidate **Sliver Strip** or
    **Inland Island**.

    Steady-state load ≈ 1.0 × 20 = 20 concurrent items (same as light
    case for fair comparison — only the distribution shape differs).
    """
    return SyntheticWorkload(WorkloadConfig(
        n_items=n_items,
        arrival_rate=1.0,
        size_w_range=(3, 15),
        size_h_range=(3, 15),
        lifetime_dist="exponential",
        mean_lifetime=20.0,
        seed=seed,
    ))


def mixed_lifetime(n_items: int = 500, seed: int = 42) -> SyntheticWorkload:
    """Pareto-distributed lifetimes — a few very long-lived items among many transients.

    Hypothesis: long-tail mimics real workloads (Powers 2023 confirmed this
    for allocator traces). A handful of "long tenants" should create
    **Inland Island** voids when surrounded by churn ⇒ tests interaction
    between heuristic placement and lifetime heterogeneity.
    """
    return SyntheticWorkload(WorkloadConfig(
        n_items=n_items,
        arrival_rate=0.5,
        size_w_range=(3, 15),
        size_h_range=(3, 15),
        lifetime_dist="pareto",
        mean_lifetime=30.0,
        pareto_alpha=1.5,
        seed=seed,
    ))


def small_items(n_items: int = 500, seed: int = 42) -> SyntheticWorkload:
    """Many small items — tests whether mode shape depends on item scale.

    Hypothesis: small items can fill awkward voids that larger items can't,
    so we expect *less* Inland Island and *more* Staircase Skyline (jagged
    upper boundary of the placed region).
    """
    return SyntheticWorkload(WorkloadConfig(
        n_items=n_items,
        arrival_rate=0.8,
        size_w_range=(2, 6),
        size_h_range=(2, 6),
        lifetime_dist="exponential",
        mean_lifetime=30.0,
        seed=seed,
    ))


def large_items(n_items: int = 500, seed: int = 42) -> SyntheticWorkload:
    """Mostly large items — bin saturates fast, few discards expected.

    Hypothesis: large items dominate the layout, leaving big rectangular
    voids when they depart. Should make Inland Island the most visible
    mode under a heuristic like BLF, and Boundary Lockout under shelf-
    based heuristics.
    """
    return SyntheticWorkload(WorkloadConfig(
        n_items=n_items,
        arrival_rate=0.3,
        size_w_range=(10, 25),
        size_h_range=(10, 25),
        lifetime_dist="exponential",
        mean_lifetime=30.0,
        seed=seed,
    ))


#: Dict-style lookup for the factorial sweep — keep the column order stable
#: so generated tables / plots are reproducible.
PRESETS = {
    "light_departure": light_departure,
    "heavy_departure": heavy_departure,
    "mixed_lifetime": mixed_lifetime,
    "small_items": small_items,
    "large_items": large_items,
}
