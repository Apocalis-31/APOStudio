from dataclasses import dataclass
from pathlib import Path

from assisted_editing.models.resource import Resource


@dataclass(slots=True)
class RenderJob:
    """Décrit un travail de rendu vidéo."""

    master_video: Path

    output_video: Path

    introduction: Resource | None

    ending: Resource | None

    overlays: list[Resource]

    fade_in: float

    fade_out: float

    music: Resource | None = None