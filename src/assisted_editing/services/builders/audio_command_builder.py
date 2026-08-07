from assisted_editing.models.timeline import Timeline
from assisted_editing.models.video_render_result import (
    VideoRenderResult,
)
from assisted_editing.services.builders.audio_filter_builder import (
    AudioFilterBuilder,
)

class AudioCommandBuilder:
    """
    Construit la commande FFmpeg
    de la seconde passe.

    Cette passe applique uniquement
    les traitements audio :
        - Intro
        - Ducking
        - Musique
    """

    # ==================================================

    def build(
        self,
        video: VideoRenderResult,
        timeline: Timeline,
    ) -> list[str]:

        command = [

            "-y",

            # -------------------------
            # Vidéo issue de la passe 1
            # -------------------------

            "-i",
            str(video.video),

        ]

        # -------------------------
        # Intro
        # -------------------------

        if timeline.introduction:

            command.extend([

                "-i",
                str(
                    timeline.introduction.path
                ),

            ])

        # ==================================================
        # Filter Complex
        # ==================================================

        filter_graph = (
            AudioFilterBuilder().build(
                timeline
            )
        )

        if filter_graph:

            command.extend([

                "-filter_complex",
                filter_graph,

                "-map",
                "0:v",

                "-map",
                "[a]",

            ])

        else:

            command.extend([

                "-map",
                "0:v",

                "-map",
                "0:a",

            ])

        # ==================================================
        # Codecs
        # ==================================================

        command.extend([

            "-c:v",
            "copy",

            "-c:a",
            "aac",

            "-b:a",
            "192k",

        ])

        # ==================================================
        # Sortie finale
        # ==================================================

        command.append(
            str(
                timeline.output_video
            )
        )

        return command