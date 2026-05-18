"""Workload generator tests.

Two classes of property to guard:

1. **Deterministic** — same seed must yield identical sequences. The H × W
   factorial design is meaningless if rerunning a (heuristic, workload)
   cell gives a different sequence each time.

2. **In-bounds** — sizes, ids, and times must respect the documented
   semantics. A negative lifetime or a zero id would crash the simulator
   only at runtime, halfway through an experiment.
"""
import pytest

from dyn2dbp.core.item import Item
from dyn2dbp.workloads.presets import PRESETS, light_departure, heavy_departure, mixed_lifetime
from dyn2dbp.workloads.synthetic import SyntheticWorkload, WorkloadConfig


def test_same_seed_yields_identical_sequence():
    """Replaying with the same seed must produce bit-identical Item lists."""
    cfg = WorkloadConfig(n_items=100, seed=123)
    a = SyntheticWorkload(cfg).generate()
    b = SyntheticWorkload(cfg).generate()
    assert a == b


def test_different_seeds_yield_different_sequences():
    a = SyntheticWorkload(WorkloadConfig(n_items=100, seed=1)).generate()
    b = SyntheticWorkload(WorkloadConfig(n_items=100, seed=2)).generate()
    assert a != b


def test_item_count_matches_config():
    items = SyntheticWorkload(WorkloadConfig(n_items=37, seed=1)).generate()
    assert len(items) == 37


def test_item_ids_are_positive_and_unique():
    """Reserved id 0 must never appear (BinState relies on this)."""
    items = SyntheticWorkload(WorkloadConfig(n_items=200, seed=1)).generate()
    ids = [item.id for item in items]
    assert 0 not in ids
    assert len(set(ids)) == len(ids)


def test_sizes_respect_configured_range():
    cfg = WorkloadConfig(
        n_items=200, seed=1,
        size_w_range=(5, 10), size_h_range=(3, 8),
    )
    items = SyntheticWorkload(cfg).generate()
    for item in items:
        assert 5 <= item.w <= 10
        assert 3 <= item.h <= 8


def test_arrivals_are_non_decreasing():
    """Inter-arrivals come from an exponential — cumulative sum is monotonic."""
    items = SyntheticWorkload(WorkloadConfig(n_items=100, seed=1)).generate()
    arrivals = [item.t_arrive for item in items]
    assert arrivals == sorted(arrivals)


def test_lifetime_is_at_least_one():
    """Quantization plus the explicit floor must guarantee positive lifetime."""
    items = SyntheticWorkload(WorkloadConfig(n_items=500, seed=1)).generate()
    for item in items:
        assert item.t_depart > item.t_arrive
        assert item.lifetime >= 1


def test_exponential_lifetime_mean_in_expected_range():
    """With n=2000, sample mean should be within 15% of the configured mean."""
    cfg = WorkloadConfig(n_items=2000, seed=1, mean_lifetime=50.0)
    items = SyntheticWorkload(cfg).generate()
    mean_lt = sum(item.lifetime for item in items) / len(items)
    assert 0.85 * 50.0 <= mean_lt <= 1.15 * 50.0


def test_pareto_alpha_le_one_rejected():
    """Pareto with α ≤ 1 has infinite mean — refuse to misconfigure."""
    cfg = WorkloadConfig(
        n_items=10, seed=1,
        lifetime_dist="pareto", pareto_alpha=0.9,
    )
    with pytest.raises(ValueError):
        SyntheticWorkload(cfg).generate()


def test_unknown_distribution_raises():
    cfg = WorkloadConfig(n_items=10, seed=1, lifetime_dist="lognormal")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        SyntheticWorkload(cfg).generate()


def test_all_presets_generate_valid_items():
    """Smoke test: every preset must produce a non-empty, valid sequence."""
    for name, factory in PRESETS.items():
        items = factory(n_items=50, seed=1).generate()
        assert len(items) == 50, f"Preset {name} returned wrong count"
        assert all(isinstance(i, Item) for i in items), f"Preset {name} returned non-Item"
        assert all(i.w > 0 and i.h > 0 for i in items), f"Preset {name} has zero-size item"


def test_heavy_departure_has_shorter_mean_lifetime_than_light():
    """Sanity check the preset hypothesis: light < heavy in lifetime, both same load."""
    light = light_departure(n_items=500, seed=1).generate()
    heavy = heavy_departure(n_items=500, seed=1).generate()
    light_mean = sum(i.lifetime for i in light) / len(light)
    heavy_mean = sum(i.lifetime for i in heavy) / len(heavy)
    assert heavy_mean < light_mean


def test_mixed_lifetime_has_heavy_tail():
    """Pareto preset's max lifetime should be much larger than its mean."""
    items = mixed_lifetime(n_items=500, seed=1).generate()
    lifetimes = [i.lifetime for i in items]
    mean_lt = sum(lifetimes) / len(lifetimes)
    max_lt = max(lifetimes)
    # Heavy-tail signature: max ≥ 5× mean. Exponential would typically
    # give max ≈ 6× mean for n=500 too, so this is a weak check — the
    # real heavy-tail evidence is visible in a histogram. Still, ≥ 5×
    # is a reasonable floor.
    assert max_lt >= 5 * mean_lt
