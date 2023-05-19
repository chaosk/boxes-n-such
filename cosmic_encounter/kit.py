from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, Iterable

from cadquery import Workplane, Assembly


@dataclass
class Object:
    name: str
    workplane: Workplane


class Part(ABC):
    """Base class for cq models."""

    name: str
    objects: Iterable[Object]

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.objects = list(self.normalize_objects(self.make()))

    @abstractmethod
    def make(self) -> Iterable[Object | Workplane]:
        ...

    def normalize_objects(
        self, objects: Iterable[Object | Workplane]
    ) -> Iterable[Object]:
        return (
            obj if isinstance(obj, Object) else Object(f"{self.name}_{idx}", obj)
            for idx, obj in enumerate(objects, start=1)
        )


@dataclass
class Project:
    parts: Iterable[Part]
    show_object: Callable

    @property
    def assembly(self) -> Assembly:
        assembly = Assembly()
        for name, workplane in self.workplanes.items():
            assembly.add(workplane, name=name)
        return assembly

    def show(self) -> None:
        self.show_object(self.assembly)

    @property
    def objects(self) -> Dict[str, Object]:
        return {obj.name: obj for part in self.parts for obj in part.objects}

    @property
    def workplanes(self) -> Dict[str, Workplane]:
        return {name: obj.workplane for name, obj in self.objects.items()}
