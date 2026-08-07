from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class VideoRenderResult:
    """
    Résultat de la première passe vidéo.
    """

    video: Path