from pathlib import Path
import subprocess

from services.path_service import PathService

from assisted_editing.models.episode_project import (
    EpisodeProject,
)
from assisted_editing.services.episode_storage import (
    EpisodeStorage,
)


class FFmpegRunner:

    def __init__(self, ui, cancel_event=None):

        self.ui = ui
        self.cancel_event = cancel_event

    # ==========================================

    def _check_cancel(self):

        if self.cancel_event and self.cancel_event.is_set():
            from workers.transcription_worker import Cancelled
            raise Cancelled()

    # ==========================================

    def run(
        self,
        project,
        plans,
        settings
    ):

        if not plans:
            return

        self.ui.log("✂️ Début du découpage des épisodes...")

        total = len(plans)

        for index, plan in enumerate(plans):

            self._check_cancel()

            self._cut_episode(
                project,
                plan,
                settings
            )

            progress = 75 + int(
                25 * (index + 1) / total
            )

            self.ui.progress(progress, 100)

        self.ui.log("✅ Découpage terminé.")

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

        # ==========================================
        # Dossier de l'épisode
        # ==========================================

        episode_folder = (
            project.project_path
            / f"Episode {plan.index}"
        )

        episode_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # ==========================================
        # Vidéo
        # ==========================================

        output = (
            episode_folder
            / f"{project.series} Episode {plan.index}.mp4"
        )

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

        self._check_cancel()

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= (
            subprocess.STARTF_USESHOWWINDOW
        )

        subprocess.run(
            command,
            check=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        # ==========================================
        # Projet APO Studio
        # ==========================================

        EpisodeStorage().save(

            EpisodeProject(

                version="1.0",

                series=project.series,

                episode=plan.index,

                prepared=False,

                edited=False,

                uploaded=False,

            ),

            episode_folder,

        )

        self.ui.log(
            "📄 Projet épisode créé"
        )