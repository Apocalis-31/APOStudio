from assisted_editing.models.timeline import Timeline
from assisted_editing.models.video_render_result import (
    VideoRenderResult,
)
from assisted_editing.services.builders.audio_command_builder import (
    AudioCommandBuilder,
)
from assisted_editing.services.ffmpeg_executor import (
    FFmpegExecutor,
)
from assisted_editing.models.audio_render_result import (
    AudioRenderResult,
)

class AudioRenderer:
    """
    Seconde passe.

    Ne traite QUE l'audio.
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
        video: VideoRenderResult,
        timeline: Timeline,
    ) -> AudioRenderResult:

        self._ui.log("")
        self._ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._ui.log("🎵 Seconde passe audio")
        self._ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        command = (
            AudioCommandBuilder().build(
                video,
                timeline,
            )
        )

        FFmpegExecutor(
            self._ui
        ).execute(
            command
        )

        return AudioRenderResult(
            video=timeline.output_video
        )