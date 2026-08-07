from pathlib import Path

from assisted_editing.models.timeline import Timeline
from assisted_editing.services.video_renderer import (
    VideoRenderer,
)
from assisted_editing.services.audio_renderer import (
    AudioRenderer,
)


class RenderingPipeline:
    """
    Orchestre les différentes
    passes de rendu.

    VideoRenderer
            ↓
        video_temp.mp4
            ↓
    AudioRenderer
            ↓
        output.mp4
    """

    # ==================================================

    def __init__(
        self,
        ui,
    ):

        self._ui = ui

    # ==================================================

    def render(
        self,
        timeline: Timeline,
    ):

        # --------------------------------------
        # Première passe
        # --------------------------------------

        video = VideoRenderer(
            self._ui
        ).render(
            timeline
        )

        # --------------------------------------
        # Seconde passe
        # --------------------------------------

        AudioRenderer(
            self._ui
        ).render(
            video,
            timeline,
        )

        # --------------------------------------
        # Nettoyage
        # --------------------------------------

        self._cleanup(
            video.video
        )

    # ==================================================

    def _cleanup(
        self,
        temp: Path,
    ):

        if not temp.exists():
            return

        try:

            temp.unlink()

            self._ui.log("")
            self._ui.log(
                "🗑️ video_temp.mp4 supprimé"
            )

        except Exception as ex:

            self._ui.log("")
            self._ui.log(
                f"⚠️ Impossible de supprimer "
                f"{temp.name}"
            )

            self._ui.log(str(ex))