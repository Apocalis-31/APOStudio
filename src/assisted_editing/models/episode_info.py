from dataclasses import dataclass
from pathlib import Path

from assisted_editing.models.episode_project import EpisodeProject


@dataclass(slots=True)
class EpisodeInfo:
    """
    Représente un épisode APO Studio
    prêt à être finalisé.
    """

    project_name: str

    episode_number: int

    title: str

    episode_folder: Path

    master_video: Path

    youtube_json: Path

    project: EpisodeProject