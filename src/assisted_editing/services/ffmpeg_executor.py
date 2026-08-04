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
        self.ui.log(f"FFmpeg : {ffmpeg}")
        self.ui.log("")
        print(full_command)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= (
            subprocess.STARTF_USESHOWWINDOW
        )

        try:

            result = subprocess.run(

                full_command,

                text=True,

                capture_output=True,

                startupinfo=startupinfo,

                creationflags=subprocess.CREATE_NO_WINDOW,

            )

            if result.stdout.strip():

                self.ui.log("📤 Sortie FFmpeg")
                self.ui.log(result.stdout)

            if result.stderr.strip():

                self.ui.log("📤 Journal FFmpeg")
                self.ui.log(result.stderr)

            result.check_returncode()

            self.ui.log("")
            self.ui.log("✅ Vidéo générée")

        except subprocess.CalledProcessError:

            self.ui.log("")
            self.ui.log("❌ Le rendu FFmpeg a échoué")

            raise