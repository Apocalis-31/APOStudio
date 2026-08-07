from dataclasses import dataclass
from pathlib import Path

from assisted_editing.models.episode_info import EpisodeInfo


@dataclass(slots=True)
class EditingQueueItem:

    # ==================================================
    # Episode
    # ==================================================

    episode: EpisodeInfo

    # ==================================================
    # Ressources
    # ==================================================

    intro: bool
    intro_path: Path | None

    outro: bool
    outro_path: Path | None

    logo: bool
    logo_path: Path | None

    overlay: bool

    music: bool
    music_path: Path | None

    # ==================================================
    # Audio
    # ==================================================

    intro_volume: float
    vod_volume: float
    fade_duration: float

    # ==================================================
    # Vidéo
    # ==================================================

    video_fade_in: float
    video_fade_out: float