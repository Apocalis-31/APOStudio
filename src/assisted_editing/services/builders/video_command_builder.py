from assisted_editing.models.timeline import Timeline
from assisted_editing.services.builders.video_filter_builder import (
    VideoFilterBuilder,
)

class VideoCommandBuilder:
    """
    Construit la commande FFmpeg
    de la première passe vidéo.

    Cette passe applique uniquement
    les traitements vidéo (logo,
    overlays, fade...) et conserve
    l'audio d'origine sans modification.
    """

    # ==================================================

    def build(
        self,
        timeline: Timeline,
    ) -> list[str]:

        output = (
            timeline.output_video.parent
            / "video_temp.mp4"
        )

        command = [

            "-y",

            # -------------------------
            # Vidéo principale
            # -------------------------

            "-i",
            str(
                timeline.master_video
            ),

        ]

        # -------------------------
        # Logo
        # -------------------------

        if timeline.logo:

            command.extend([

                "-i",
                str(
                    timeline.logo.path
                ),

            ])

        # ==================================================
        # Filter Complex
        # ==================================================

        filter_graph = (
            VideoFilterBuilder().build(
                timeline
            )
        )

        if filter_graph:

            command.extend([

                "-filter_complex",
                filter_graph,

                "-map",
                "[v]",

            ])

        else:

            command.extend([

                "-map",
                "0:v",

            ])

        # ==================================================
        # Audio
        # ==================================================

        command.extend([

            "-map",
            "0:a",

            "-c:a",
            "copy",

        ])

        # ==================================================
        # Vidéo
        # ==================================================

        command.extend([

            "-c:v",
            "libx264",

            "-preset",
            "veryfast",

            "-crf",
            "18",

        ])

        # ==================================================
        # Sortie
        # ==================================================

        command.append(
            str(output)
        )

        return command