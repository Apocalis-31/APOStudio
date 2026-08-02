from dataclasses import dataclass, field
from pathlib import Path

from assisted_editing.models.resource import Resource


@dataclass(slots=True)
class Timeline:
    """
    Représentation d'un montage vidéo.

    Cette classe décrit le contenu de la timeline.
    Elle est indépendante de FFmpeg.
    """

    # ==========================
    # Médias principaux
    # ==========================

    master_video: Path
    output_video: Path

    # ==========================
    # Audio
    # ==========================

    introduction: Resource | None = None
    ending: Resource | None = None
    music: Resource | None = None

    # ==========================
    # Overlays
    # ==========================

    overlays: list[Resource] = field(default_factory=list)

    # ==========================
    # Intro
    # ==========================

    introduction_duration: float | None = None