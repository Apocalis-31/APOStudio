from dataclasses import dataclass


@dataclass(slots=True)
class AudioSettings:
    """
    Paramètres audio utilisés
    pendant le montage assisté.
    """

    intro_volume: float = 1.0

    vod_volume: float = 0.10

    fade_duration: float = 1.5