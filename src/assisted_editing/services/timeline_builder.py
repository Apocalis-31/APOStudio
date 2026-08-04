from assisted_editing.models.audio_settings import AudioSettings
from assisted_editing.models.render_job import RenderJob
from assisted_editing.models.timeline import Timeline
from assisted_editing.services.media_probe import MediaProbe


class TimelineBuilder:
    """
    Construit une Timeline à partir d'un RenderJob.
    """

    def __init__(
        self,
        probe: MediaProbe,
    ) -> None:

        self._probe = probe

    # =====================================================

    def build(
        self,
        render_job: RenderJob,
        audio_settings: AudioSettings,
    ) -> Timeline:

        timeline = Timeline(
            master_video=render_job.master_video,
            output_video=render_job.output_video,
        )

        # ==================================================
        # Ressources
        # ==================================================

        timeline.introduction = render_job.introduction
        timeline.logo = render_job.logo
        timeline.ending = render_job.ending
        timeline.music = render_job.music
        timeline.overlays = render_job.overlays

        # ==================================================
        # Paramètres audio
        # ==================================================

        timeline.audio = audio_settings

        # ==================================================
        # Durées
        # ==================================================

        if timeline.introduction:

            timeline.introduction_duration = (
                self._probe.get_duration(
                    timeline.introduction.path
                )
            )

        if timeline.logo:

            timeline.logo_duration = (
                self._probe.get_duration(
                    timeline.logo.path
                )
            )

        return timeline