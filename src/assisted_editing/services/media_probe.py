import json
from pathlib import Path

from services.ffmpeg.ffmpeg_service import FFmpegService


class MediaProbe:
    """
    Récupère les informations d'un média via ffprobe.
    """

    def __init__(
        self,
        ffmpeg: FFmpegService,
    ) -> None:

        self._ffmpeg = ffmpeg

    # =====================================================

    def get_duration(
        self,
        media: Path,
    ) -> float:
        """
        Retourne la durée d'un média en secondes.
        """

        result = self._ffmpeg.run_ffprobe([

            "-v",
            "quiet",

            "-print_format",
            "json",

            "-show_format",

            str(media),

        ])

        data = json.loads(result.stdout)

        return float(data["format"]["duration"])