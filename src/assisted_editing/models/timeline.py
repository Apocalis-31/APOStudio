from dataclasses import dataclass, field
from pathlib import Path

from assisted_editing.models.audio_settings import AudioSettings
from assisted_editing.models.resource import Resource
from assisted_editing.models.video_settings import VideoSettings


@dataclass(slots=True)
class Timeline:
    """
    Représentation d'un montage vidéo.

    Cette classe décrit le contenu de la timeline.
    Elle est indépendante de FFmpeg.
    """

    # ==================================================
    # Médias principaux
    # ==================================================

    master_video: Path
    output_video: Path

    # ==================================================
    # Ressources
    # ==================================================

    introduction: Resource | None = None
    ending: Resource | None = None
    music: Resource | None = None
    logo: Resource | None = None

    overlays: list[Resource] = field(
        default_factory=list
    )

    # ==================================================
    # Informations calculées
    # ==================================================

    master_duration: float | None = None

    introduction_duration: float | None = None

    logo_duration: float | None = None

    ending_duration: float | None = None

    music_duration: float | None = None

    # ==================================================
    # Paramètres audio
    # ==================================================

    audio: AudioSettings = field(
        default_factory=AudioSettings
    )

    # ==================================================
    # Paramètres vidéo
    # ==================================================

    video: VideoSettings = field(
        default_factory=VideoSettings
    )