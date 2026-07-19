from pathlib import Path
import subprocess
from services.path_service import PathService

class FFmpegRunner:

    def __init__(self, ui):

        self.ui = ui

    # ==========================================

    def run(
        self,
        project,
        plans,
        settings
    ):

        if not plans:
            return

        for plan in plans:

            self._cut_episode(
                project,
                plan,
                settings
            )

    # ==========================================

    def _cut_episode(
        self,
        project,
        plan,
        settings
    ):

        self.ui.log(
            f"🎬 Découpage de l'épisode {plan.index}..."
        )

        output = (
            project.project_path
            / f"{project.series} Episode {plan.index}.mp4"
        )

        from pathlib import Path

        ffmpeg = (
            PathService.ffmpeg()
            / "ffmpeg.exe"
        )

        start = max(

            0,

            plan.start - settings.overlap_seconds

        )

        duration = plan.end - start

        command = [

            str(ffmpeg),

            "-y",

           "-ss",
            str(start),

            "-i",
            str(project.video_path),

            "-t",
            str(duration),

            "-c",
            "copy",

            str(output)

        ]

        self.ui.log(
            f"FFmpeg : {ffmpeg}"
        )

        self.ui.log(
            "⚡ Mode : Découpe instantanée"
        )

        subprocess.run(
            command,
            check=True
        )