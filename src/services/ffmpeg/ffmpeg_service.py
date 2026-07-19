from pathlib import Path
from services.path_service import PathService

class FFmpegService:

    @property
    def executable(self):

        return (
            PathService.ffmpeg()
            / "ffmpeg"
            / "ffmpeg.exe"
        )