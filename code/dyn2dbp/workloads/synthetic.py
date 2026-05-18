"""Synthetic workload generator — the engine behind variant E's experiments.

Six knobs control the entire shape of the workload, and the same six knobs are
what the H × W factorial sweep varies in week 3. Every parameter here is
either grounded in literature or marked as an explicit hypothesis-testing
starting value (see WorkloadConfig docstring).

Design choice: Poisson arrival + parametric lifetime, both via numpy's
``default_rng`` for reproducibility. We *don't* compose individual events —
we generate the whole Item list up-front so the simulator just consumes it.
This makes runs replayable from the seed alone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Tuple

import numpy as np

from ..core.item import Item
from .base import WorkloadGenerator


LifetimeDist = Literal["exponential", "pareto", "uniform"]


@dataclass(frozen=True)
class WorkloadConfig:
    """All six knobs that shape a synthetic workload.

    Defaults are calibrated for a 50×50 bin (the variant-E experiment scale).
    For larger bins, scale ``size_w_range`` / ``size_h_range`` proportionally
    so items remain "small relative to bin" (Hopper-Turton convention).

    Parameters
    ----------
    n_items : int
        Number of items in the sequence. 500 is a working default — enough
        for a candidate mode to repeat several times so we can quantify it,
        not so large that one run takes minutes.

    arrival_rate : float
        Poisson rate λ (items per tick). Inter-arrival times are drawn from
        Exp(1/λ). Higher rate ⇒ items pile up faster ⇒ pressure on the
        bin's free space, which is the regime where Sliver Strip is
        hypothesized to emerge.

    size_w_range, size_h_range : (int, int)
        Inclusive bounds for item width / height. Sampled uniformly in
        each dimension. Default ``(3, 15)`` on a 50×50 bin means items
        occupy 6–30% of the bin's width — "small to medium", matching
        Hopper-Turton's spirit.

    lifetime_dist : "exponential" | "pareto" | "uniform"
        Shape of the lifetime (= t_depart − t_arrive) distribution.

        * ``exponential``: memoryless, simplest baseline — Exp(1/mean).
        * ``pareto``: heavy-tailed; a few items live much longer than
          the mean. This is the real-world shape (Powers 2023 confirms
          long-tail in allocator traces; FPGA long-running tasks; VM
          long-lived tenants). Heavy tail is the hypothesized trigger
          for Boundary Lockout (long-lived items at the bottom-left
          pin the layout).
        * ``uniform``: control distribution, no skew. Useful as a sanity
          check that observed modes aren't an artifact of skew alone.

    mean_lifetime : float
        Target mean of the lifetime distribution, in ticks. Combined with
        ``arrival_rate`` this controls the *steady-state occupancy* of the
        bin: roughly λ × mean_lifetime × mean_item_area / bin_area. If
        this product ≫ 1 the bin will saturate and discard a lot of items.

    pareto_alpha : float
        Tail index for the Pareto distribution. Only used when
        ``lifetime_dist == "pareto"``. α ∈ (1, 2) gives finite mean but
        infinite variance — the regime that produces dramatic long-tail
        behaviour. α=1.5 is a common default in heavy-tail workload models.

    seed : int | None
        RNG seed. ``None`` means non-deterministic (don't use for
        experiments — only for quick exploration).
    """
    n_items: int = 500
    arrival_rate: float = 0.5
    size_w_range: Tuple[int, int] = (3, 15)
    size_h_range: Tuple[int, int] = (3, 15)
    lifetime_dist: LifetimeDist = "exponential"
    mean_lifetime: float = 30.0
    pareto_alpha: float = 1.5
    seed: Optional[int] = None

    def short_name(self) -> str:
        """Compact identifier for use in filenames / plot titles."""
        return (
            f"n{self.n_items}_r{self.arrival_rate}"
            f"_w{self.size_w_range[0]}-{self.size_w_range[1]}"
            f"_h{self.size_h_range[0]}-{self.size_h_range[1]}"
            f"_lt-{self.lifetime_dist}{self.mean_lifetime}"
            f"_s{self.seed}"
        )


class SyntheticWorkload(WorkloadGenerator):
    """Generate ``n_items`` items via Poisson arrival + configured lifetime dist."""

    def __init__(self, config: WorkloadConfig) -> None:
        self.config = config
        self.name = config.short_name()

    def generate(self) -> List[Item]:
        cfg = self.config
        rng = np.random.default_rng(cfg.seed)

        # ---- arrival times via Poisson process -------------------------
        # Inter-arrival times ~ Exp(1/λ). Sum them to get absolute arrival
        # times. Quantize to integer ticks — the simulator uses int time.
        # Two arrivals can land on the same tick after rounding; that's
        # fine, simulator tie-breaks by id.
        inter_arrivals = rng.exponential(scale=1.0 / cfg.arrival_rate, size=cfg.n_items)
        arrivals_float = np.cumsum(inter_arrivals)
        t_arrives = arrivals_float.astype(np.int64)

        # ---- sizes uniformly within range -------------------------------
        # ``integers`` with endpoint=True is inclusive on both ends, matching
        # the documented "(min, max) inclusive" semantics of size_w_range.
        ws = rng.integers(cfg.size_w_range[0], cfg.size_w_range[1], size=cfg.n_items, endpoint=True)
        hs = rng.integers(cfg.size_h_range[0], cfg.size_h_range[1], size=cfg.n_items, endpoint=True)

        # ---- lifetimes per the configured distribution ------------------
        lifetimes = self._sample_lifetimes(rng, cfg.n_items)
        # Enforce minimum lifetime of 1 tick — a zero-lifetime item would
        # arrive and depart at the same instant, which makes no semantic
        # sense in the dynamic model.
        lifetimes = np.maximum(lifetimes.astype(np.int64), 1)

        items: List[Item] = []
        for i in range(cfg.n_items):
            t_arrive = int(t_arrives[i])
            items.append(Item(
                # Item ids are 1-indexed because 0 is reserved by BinState
                # for "empty cell". Using i+1 keeps that invariant cheap.
                id=i + 1,
                w=int(ws[i]),
                h=int(hs[i]),
                t_arrive=t_arrive,
                t_depart=t_arrive + int(lifetimes[i]),
            ))
        return items

    # ---- private helpers ------------------------------------------------

    def _sample_lifetimes(self, rng: np.random.Generator, n: int) -> np.ndarray:
        """Draw n lifetimes, each with the configured mean."""
        cfg = self.config
        if cfg.lifetime_dist == "exponential":
            # Exp(1/mean) directly has the desired mean.
            return rng.exponential(scale=cfg.mean_lifetime, size=n)

        if cfg.lifetime_dist == "pareto":
            # numpy's pareto draws from Pareto(α) with x_min=1, so the raw
            # samples have mean α/(α-1). We rescale so the result has the
            # target mean: scale = mean_lifetime × (α-1) / α.
            alpha = cfg.pareto_alpha
            if alpha <= 1:
                raise ValueError(
                    f"pareto_alpha must be > 1 for finite mean (got {alpha})"
                )
            scale = cfg.mean_lifetime * (alpha - 1) / alpha
            return scale * (rng.pareto(alpha, size=n) + 1)

        if cfg.lifetime_dist == "uniform":
            # Uniform[0, 2×mean] has mean = mean_lifetime.
            return rng.uniform(0, 2 * cfg.mean_lifetime, size=n)

        raise ValueError(f"Unknown lifetime distribution: {cfg.lifetime_dist}")
