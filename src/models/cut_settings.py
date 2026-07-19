from dataclasses import dataclass


@dataclass
class CutSettings:

    mode: str = "duration"

    target_duration: int = 60

    tolerance: int = 15

    episode_count: int = 0

    intro_duration: int = 90

    ending_duration: int = 60

    rename: bool = True

    series_name: str = ""

    first_episode: int = 1

    use_ai: bool = True

    overlap_seconds: int = 5