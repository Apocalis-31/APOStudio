from assisted_editing.models.render_job import RenderJob
from assisted_editing.services.ffmpeg_renderer import FFmpegRenderer
from assisted_editing.services.render_validator import RenderValidator
from assisted_editing.services.timeline_builder import TimelineBuilder
from services.ffmpeg.ffmpeg_service import FFmpegService



class EditingEngine:
    """Moteur de montage assisté."""

    def __init__(
        self,
        validator: RenderValidator,
        timeline_builder: TimelineBuilder,
        renderer: FFmpegRenderer,
        ffmpeg_service: FFmpegService,
    ) -> None:

        self._validator = validator
        self._timeline_builder = timeline_builder
        self._renderer = renderer
        self._ffmpeg = ffmpeg_service

    def render(
        self,
        render_job: RenderJob,
    ) -> None:
        """
        Génère la vidéo finale.
        """

        # Validation
        self._validator.validate(render_job)

        # Construction de la timeline
        timeline = self._timeline_builder.build(render_job)

        # Construction de la commande FFmpeg
        command = self._renderer.build(timeline)

        print("\nCommande FFmpeg :")
        print(" ".join(command))

        # Exécution
        self._ffmpeg.run(command)

