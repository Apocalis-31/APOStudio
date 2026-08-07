from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AudioRenderResult:
    """
    Résultat de la seconde passe audio.
    """

    video: Path