from dataclasses import dataclass
from pathlib import Path

from assisted_editing.models.resource_type import ResourceType


@dataclass(frozen=True, slots=True)
class Resource:
    """Représente une ressource appartenant à la bibliothèque d'APO Studio."""

    name: str
    type: ResourceType
    path: Path