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
    ) -> Timeline:

        timeline = Timeline(
            master_video=render_job.master_video,
            output_video=render_job.output_video,
        )

        timeline.introduction = render_job.introduction
        timeline.logo = render_job.logo
        timeline.ending = render_job.ending
        timeline.music = render_job.music

        if render_job.introduction:

            timeline.introduction_duration = (
                self._probe.get_duration(
                    render_job.introduction.path
                )
            )
        if render_job.logo:

            timeline.logo_duration = (
                self._probe.get_duration(
                    render_job.logo.path
                )
            )

        return timeline