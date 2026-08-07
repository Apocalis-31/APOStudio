from assisted_editing.models.timeline import Timeline


class VideoFilterBuilder:
    """
    Construit les filtres vidéo
    de la première passe.
    """

    # ==================================================

    def build(
        self,
        timeline: Timeline,
    ) -> str | None:

        filters = []

        current = "0:v"

        # ==================================================
        # Fade In
        # ==================================================

        if timeline.video.fade_in > 0:

            filters.append(

                f"[{current}]"
                f"fade=t=in:st=0:d={timeline.video.fade_in}"
                "[fadein]"

            )

            current = "fadein"

        # ==================================================
        # Logo
        # ==================================================

        if timeline.logo:

            logo_end = (
                timeline.logo_duration or 0.0
            ) + 0.2

            filters.append(

                "[1:v]"
                "setpts=PTS-STARTPTS"
                "[logo]"

            )

            filters.append(

                f"[{current}]"
                "[logo]"
                "overlay="
                "x=0:"
                "y=0:"
                "eof_action=pass:"
                "repeatlast=0:"
                f"enable='lt(t,{logo_end:.3f})'"
                "[logoed]"

            )

            current = "logoed"

        # ==================================================
        # Fade Out
        # ==================================================

        if (
            timeline.video.fade_out > 0
            and timeline.master_duration
        ):

            fade_start = (

                timeline.master_duration
                - timeline.video.fade_out

            )

            filters.append(

                f"[{current}]"
                f"fade=t=out:st={fade_start:.3f}:d={timeline.video.fade_out}"
                "[fadeout]"

            )

            current = "fadeout"

        # ==================================================

        if current == "0:v":

            return None

        filters.append(

            f"[{current}]copy[v]"

        )

        return ";".join(filters)