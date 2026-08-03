from dataclasses import dataclass


@dataclass
class EpisodeProject:

    version: str = "1.0"

    series: str = ""

    episode: int = 0

    prepared: bool = False

    edited: bool = False

    uploaded: bool = False