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
        Retourne la durée d'un média.

        Les images (PNG, JPG, ...) ne possèdent
        pas de durée. Dans ce cas on retourne 0.0.
        """

        data = self._probe(media)

        duration = (
            data
            .get("format", {})
            .get("duration")
        )

        if duration is None:
            return 0.0

        return float(duration)

    # =====================================================

    def get_fps(
        self,
        media: Path,
    ) -> float:
        """
        Retourne le FPS de la première piste vidéo.
        """

        data = self._probe(media)

        if not data.get("streams"):
            return 0.0

        stream = data["streams"][0]

        rate = stream.get("r_frame_rate", "0/1")

        numerator, denominator = map(
            int,
            rate.split("/")
        )

        if denominator == 0:
            return 0.0

        return numerator / denominator

    # =====================================================

    def snap_to_frame(
        self,
        media: Path,
        time: float,
    ) -> float:
        """
        Aligne un temps sur la frame la plus proche.
        """

        fps = self.get_fps(media)

        if fps <= 0:
            return time

        frame = round(time * fps)

        return frame / fps

    # =====================================================

    def _probe(
        self,
        media: Path,
    ) -> dict:
        """
        Exécute ffprobe et retourne le JSON complet.
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

                "-show_streams",

                str(media),

            ],

            capture_output=True,

            text=True,

            check=True,

            startupinfo=startupinfo,

            creationflags=subprocess.CREATE_NO_WINDOW,

        )

        return json.loads(
            result.stdout
        )