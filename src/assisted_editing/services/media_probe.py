import json
import subprocess

from pathlib import Path

from services.path_service import PathService


class MediaProbe:
    """
    Récupère les informations d'un média via ffprobe.
    """

    # =====================================================

    def get_duration(
        self,
        media: Path,
    ) -> float:
        """
        Retourne la durée d'un média en secondes.
        """

        ffprobe = (
            PathService.ffmpeg()
            / "ffprobe.exe"
        )

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= (
            subprocess.STARTF_USESHOWWINDOW
        )

        result = subprocess.run(

            [

                str(ffprobe),

                "-v",
                "quiet",

                "-print_format",
                "json",

                "-show_format",

                str(media),

            ],

            capture_output=True,

            text=True,

            check=True,

            startupinfo=startupinfo,

            creationflags=subprocess.CREATE_NO_WINDOW,

        )

        data = json.loads(
            result.stdout
        )

        return float(
            data["format"]["duration"]
        )