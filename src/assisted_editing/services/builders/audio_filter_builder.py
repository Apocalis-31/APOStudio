from assisted_editing.models.timeline import Timeline


class AudioFilterBuilder:
    """
    Construit les filtres audio
    de la seconde passe.
    """

    # ==================================================

    def build(
        self,
        timeline: Timeline,
    ) -> str | None:

        if not timeline.introduction:
            return None

        audio = timeline.audio

        intro_duration = (
            timeline.introduction_duration
            or 0.0
        )

        fade_duration = (
            audio.fade_duration
        )

        ducking = self._build_ducking_expression(

            intro_duration,

            audio.vod_volume,

            fade_duration,

        )

        return (

            "[0:a]"

            "asetpts=PTS-STARTPTS,"

            f"volume='{ducking}':eval=frame"

            "[bg];"

            "[1:a]"

            "asetpts=PTS-STARTPTS,"

            f"volume={audio.intro_volume}"

            "[intro];"

            "[bg][intro]"

            "amix="

            "inputs=2:"

            "duration=longest:"

            "normalize=0"

            "[a]"

        )

    # ==================================================

    def _build_ducking_expression(

        self,

        intro_duration: float,

        ducking_volume: float,

        fade_duration: float,

    ) -> str:

        fade_end = (
            intro_duration
            + fade_duration
        )

        return (

            "if("

            f"lt(t,{intro_duration}),"

            f"{ducking_volume},"

            "if("

            f"lt(t,{fade_end}),"

            f"{ducking_volume}"

            f"+(t-{intro_duration})"

            f"*({1-ducking_volume}"

            f"/{fade_duration}),"

            "1"

            "))"

        )