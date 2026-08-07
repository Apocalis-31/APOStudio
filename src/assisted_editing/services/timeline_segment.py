from assisted_editing.models.timeline import Timeline
from assisted_editing.models.timeline_segment import TimelineSegment
from assisted_editing.services.media_probe import MediaProbe


class SegmentBuilder:

    def __init__(self):

        self._probe = MediaProbe()

    # ==================================================

    def build(
        self,
        timeline: Timeline,
    ) -> list[TimelineSegment]:

        video_duration = self._probe.get_duration(
            timeline.master_video
        )

        segments = []

        # ==========================================
        # Durée des effets
        # ==========================================

        effect_end = 0.0

        if timeline.logo:

            effect_end = max(
                effect_end,
                timeline.logo_duration or 0.0
            )

        if timeline.introduction:

            effect_end = max(
                effect_end,
                timeline.introduction_duration or 0.0
            )

        # Petite marge de sécurité

        effect_end += 0.2

        # ==========================================
        # Segment encodé
        # ==========================================

        if effect_end > 0:

            segments.append(

                TimelineSegment(

                    start=0.0,

                    end=effect_end,

                    encode=True,

                    intro=timeline.introduction is not None,

                    logo=timeline.logo is not None,

                )

            )

        # ==========================================
        # Segment en copy
        # ==========================================

        if effect_end < video_duration:

            segments.append(

                TimelineSegment(

                    start=effect_end,

                    end=video_duration,

                    encode=False,

                )

            )

        return segments