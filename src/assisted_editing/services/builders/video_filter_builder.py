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

        # Aucun logo
        if not timeline.logo:
            return None

        logo_end = (
            timeline.logo_duration or 0.0
        ) + 0.2

        return (

            "[0:v]"
            "setpts=PTS-STARTPTS"
            "[base];"

            "[1:v]"
            "setpts=PTS-STARTPTS"
            "[logo];"

            "[base][logo]"

            "overlay="

            "x=0:"
            "y=0:"

            "eof_action=pass:"
            "repeatlast=0:"

            f"enable='lt(t,{logo_end:.3f})'"

            "[v]"

        )