from assisted_editing.models.timeline import Timeline


class FFmpegRenderer:
    """
    Construit les commandes FFmpeg à partir d'une Timeline.
    """

    # =====================================================

    def __init__(self):

        self._timeline = None

        self._inputs = []
        self._filters = []
        self._maps = []
        self._codecs = []
        self._output = []
        self._master_index = 0
        self._intro_index = None
        self._logo_index = None

    # =====================================================

    def build(
        self,
        timeline: Timeline,
    ) -> list[str]:

        self._timeline = timeline

        self._reset()

        self._build_inputs()
        self._build_filters()
        self._build_maps()
        self._build_codecs()
        self._build_output()

        return self._assemble_command()

    # =====================================================

    def _reset(self):

        self._inputs.clear()
        self._filters.clear()
        self._maps.clear()
        self._codecs.clear()
        self._output.clear()
        self._master_index = 0
        self._intro_index = None
        self._logo_index = None

    # =====================================================

    def _build_inputs(self):

        index = 0

        self._master_index = index

        self._inputs.extend([

            "-i",
            str(self._timeline.master_video),

        ])

        index += 1

        if self._timeline.introduction:

            self._intro_index = index

            self._inputs.extend([

                "-i",
                str(self._timeline.introduction.path),

            ])

            index += 1

        if self._timeline.logo:

            self._logo_index = index

            self._inputs.extend([

                "-i",
                str(self._timeline.logo.path),

            ])

            index += 1

    # =====================================================

    def _build_filters(self):

        if self._timeline.logo:

            self._filters.append(
                self._build_video_filter()
            )

        if self._timeline.introduction:

            self._filters.append(
                self._build_audio_filter()
            )

    # =====================================================

    def _build_maps(self):

        # ------------------------------
        # Vidéo
        # ------------------------------

        if self._timeline.logo:

            self._maps.extend([

                "-map",
                "[v]",

            ])

        else:

            self._maps.extend([

                "-map",
                "0:v",

            ])

        # ------------------------------
        # Audio
        # ------------------------------

        if self._timeline.introduction:

            self._maps.extend([

                "-map",
                "[a]",

            ])

        else:

            self._maps.extend([

                "-map",
                "0:a",

            ])

    # =====================================================

    def _build_codecs(self):

        # ------------------------------
        # Vidéo
        # ------------------------------

        if self._timeline.logo:

            self._codecs.extend([

                "-c:v",
                "libx264",

                "-preset",
                "veryfast",

                "-crf",
                "18",

            ])

        else:

            self._codecs.extend([

                "-c:v",
                "copy",

            ])

        # ------------------------------
        # Audio
        # ------------------------------

        if self._timeline.introduction:

            self._codecs.extend([

                "-c:a",
                "aac",

                "-b:a",
                "192k",

            ])

        else:

            self._codecs.extend([

                "-c:a",
                "copy",

            ])

    # =====================================================

    def _build_output(self):

        self._output.append(
            str(self._timeline.output_video)
        )

    # =====================================================

    def _assemble_command(
        self,
    ) -> list[str]:

        command = [

            "-y",

            *self._inputs,

        ]

        if self._filters:

            command.extend([

                "-filter_complex",

                ";".join(self._filters),

            ])

        command.extend(self._maps)
        command.extend(self._codecs)
        command.extend(self._output)

        return command

    # =====================================================

    def _build_video_filter(self) -> str:

        return (

            f"[{self._master_index}:v]"
            "setpts=PTS-STARTPTS[base];"

            f"[{self._logo_index}:v]"
            "setpts=PTS-STARTPTS[logo];"

            "[base][logo]"

            "overlay=0:0[v]"

        )

    # =====================================================

    def _build_audio_filter(
        self,
    ) -> str:
        """
        Construit le filtre audio complet.
        """

        audio = self._timeline.audio

        intro_duration = (
            self._timeline.introduction_duration
            if self._timeline.introduction_duration is not None
            else 0.0
        )

        ducking_expression = self._build_ducking_expression(
            intro_duration,
            audio.vod_volume,
            audio.fade_duration,
        )

        return (

            f"[{self._master_index}:a]"
            f"volume='{ducking_expression}'[bg];"

            f"[{self._intro_index}:a]"
            f"volume={audio.intro_volume}[intro];"

            "[bg][intro]"

            "amix=inputs=2:duration=longest[a]"

        )

    # =====================================================

    def _build_ducking_expression(
        self,
        intro_duration: float,
        ducking_volume: float,
        fade_duration: float,
    ) -> str:
        """
        Construit l'expression FFmpeg permettant
        de réduire le volume de la VOD pendant
        l'introduction puis de le rétablir
        progressivement.
        """

        fade_end = intro_duration + fade_duration

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