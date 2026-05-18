"""Abstract workload — anything that produces a list[Item] for the simulator.

Why an interface at all (rather than just a function): later we want to swap
SyntheticWorkload for TraceReplayWorkload (real FPGA / DSA traces) without
touching the experiment runner. A common ``generate() -> list[Item]`` shape
is the contract that lets that swap stay one-line.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..core.item import Item


class WorkloadGenerator(ABC):
    """A reproducible source of Item sequences."""

    #: Human-readable identifier used in result tables / plots.
    name: str = "abstract"

    @abstractmethod
    def generate(self) -> List[Item]:
        """Return the full item sequence for one simulation run.

        Must be deterministic given the generator's configured seed —
        otherwise the H × W factorial scan is irreproducible.
        """
        raise NotImplementedError
