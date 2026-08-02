from assisted_editing.models.timeline import Timeline


class FFmpegRenderer:
    """
    Construit les commandes FFmpeg à partir d'une Timeline.
    """

    INTRO_VOLUME = 1.0
    DUCKING_VOLUME = 0.10
    DUCKING_FADE = 1.5

    # =====================================================

    def build(
        self,
        timeline: Timeline,
    ) -> list[str]:

        if timeline.introduction:
            return self._build_intro_command(timeline)

        return self._build_simple_command(timeline)

    # =====================================================

    def _build_simple_command(
        self,
        timeline: Timeline,
    ) -> list[str]:

        return [

            "-y",

            "-i",
            str(timeline.master_video),

            "-c",
            "copy",

            str(timeline.output_video),

        ]

    # =====================================================

    def _build_intro_command(
        self,
        timeline: Timeline,
    ) -> list[str]:

        return [

            "-y",

            "-i",
            str(timeline.master_video),

            "-i",
            str(timeline.introduction.path),

            "-filter_complex",
            self._build_audio_filter(timeline),

            "-map",
            "0:v",

            "-map",
            "[a]",

            "-c:v",
            "copy",

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            str(timeline.output_video),

        ]

    # =====================================================

    def _build_audio_filter(
        self,
        timeline: Timeline,
    ) -> str:
        """
        Construit le filtre audio complet.
        """

        intro_duration = (
            timeline.introduction_duration
            if timeline.introduction_duration is not None
            else 0.0
        )

        ducking_expression = self._build_ducking_expression(
            intro_duration
        )

        return (

            f"[0:a]volume='{ducking_expression}'[bg];"

            f"[1:a]volume={self.INTRO_VOLUME}[intro];"

            "[bg][intro]"

            "amix=inputs=2:duration=longest[a]"

        )

    # =====================================================

    def _build_ducking_expression(
        self,
        intro_duration: float,
    ) -> str:
        """
        Construit l'expression FFmpeg permettant
        de réduire le volume de la VOD pendant
        l'introduction puis de le rétablir
        progressivement.
        """

        fade_end = intro_duration + self.DUCKING_FADE

        return (
            "if("
            f"lt(t,{intro_duration}),"
            f"{self.DUCKING_VOLUME},"
            "if("
            f"lt(t,{fade_end}),"
            f"{self.DUCKING_VOLUME}"
            f"+(t-{intro_duration})"
            f"*({1-self.DUCKING_VOLUME}"
            f"/{self.DUCKING_FADE}),"
            "1"
            "))"
        )