from dataclasses import dataclass


@dataclass(slots=True)
class VideoSettings:
    """
    Paramètres du rendu vidéo.
    """

    fade_in: float = 1.5
    fade_out: float = 1.5