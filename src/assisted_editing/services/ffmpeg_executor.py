from pathlib import Path
import subprocess

from services.path_service import PathService


class FFmpegExecutor:
    """
    Exécute une commande FFmpeg.
    """

    def __init__(self, ui):

        self.ui = ui

    # ==================================================

    def execute(
        self,
        command: list[str],
    ):

        ffmpeg = (
            PathService.ffmpeg()
            / "ffmpeg.exe"
        )

        full_command = [

            str(ffmpeg),

            *command,

        ]

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🎥 Rendu vidéo")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= (
            subprocess.STARTF_USESHOWWINDOW
        )

        try:

            subprocess.run(

                full_command,

                check=True,

                startupinfo=startupinfo,

                creationflags=subprocess.CREATE_NO_WINDOW,

            )

            self.ui.log("✅ Vidéo générée")

        except subprocess.CalledProcessError:

            self.ui.log("❌ Le rendu FFmpeg a échoué")
            raise