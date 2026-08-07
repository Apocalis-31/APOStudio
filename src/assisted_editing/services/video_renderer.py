from assisted_editing.models.timeline import Timeline
from assisted_editing.models.video_render_result import (
    VideoRenderResult,
)
from assisted_editing.services.ffmpeg_executor import (
    FFmpegExecutor,
)
from assisted_editing.services.builders.video_command_builder import (
    VideoCommandBuilder,
)

class VideoRenderer:
    """
    Première passe du moteur de rendu.

    Cette passe applique uniquement
    les traitements vidéo :

        • Logo
        • Overlays
        • Fade vidéo

    L'audio est simplement recopié.
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
    ) -> VideoRenderResult:

        output = (
            timeline.output_video.parent
            / "video_temp.mp4"
        )

        self._ui.log("")
        self._ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._ui.log("🎬 Première passe vidéo")
        self._ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        command = (
            VideoCommandBuilder().build(
                timeline
            )
        )

        self._ui.log("")
        self._ui.log("⚙️ Commande FFmpeg (Vidéo)")
        self._ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self._ui.log(
            " ".join(command)
        )

        FFmpegExecutor(
            self._ui
        ).execute(command)

        return VideoRenderResult(
            video=output
        )