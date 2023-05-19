from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

from cadquery import Workplane, Assembly


class Part(ABC):
    """Base class for cq models."""

    @abstractmethod
    def make(self) -> Iterable[Workplane]:
        ...


@dataclass
class Project:
    parts: Iterable[Part]

    @property
    def assembly(self):
        assembly = Assembly()
        for part in self.parts:
            assembly.add(part.make())
        return assembly
