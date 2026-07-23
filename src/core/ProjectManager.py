from pathlib import Path

from parsers.filename_parser import FilenameParser
from models.project import Project

from services.project_storage import ProjectStorage
from services.ai.whisper_service import WhisperService
from services.ai.youtube_service import YoutubeService
from services.thumbnail.thumbnail_service import ThumbnailService

from services.workflow.workflow_manager import WorkflowManager


class ProjectManager:

    def _check_cancel(self, cancel_event):

        if cancel_event and cancel_event.is_set():
            from workers.transcription_worker import Cancelled
            raise Cancelled()

    def create_project(
        self,
        video_path: str,
        ui,
        cancel_event=None,
        forced_modules=None
    ) -> Project:

        video = Path(video_path)

        self._check_cancel(cancel_event)

        ui.log("")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("🎬 Traitement de la vidéo")
        ui.log(f"📄 {video.name}")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("")

        name = video.stem

        parser = FilenameParser()

        parsed = parser.parse(video_path)



        project = Project(
            name=name,
            series=parsed["series"],
            episode=parsed["episode"],
            video_path=video,
        )

        storage = ProjectStorage()
        workflow = WorkflowManager(
            forced_modules=forced_modules
        )
        ui.log("📁 Création du projet...")
        ui.step("project")



        storage.save(project)

        # ==========================================
        # Transcription
        # ==========================================

        self._check_cancel(cancel_event)

        if workflow.enabled("transcription"):

            ui.log("🎙️ Chargement de Whisper...")
            ui.step("whisper")

            transcript = project.project_path / "transcript.txt"

            if transcript.exists():

                ui.log("✅ Transcription déjà présente")
                project.transcription_done = True

            else:

                whisper = WhisperService(ui=ui, cancel_event=cancel_event)
                whisper.transcribe(project)

        # ==========================================
        # YouTube
        # ==========================================

        self._check_cancel(cancel_event)

        if workflow.enabled("youtube"):

            ui.step("youtube")

            youtube = YoutubeService(ui, cancel_event=cancel_event)
            youtube.generate(project)

        # ==========================================
        # Thumbnail
        # ==========================================

        self._check_cancel(cancel_event)

        if workflow.enabled("thumbnail"):

            ui.step("thumbnail")

            thumbnail = ThumbnailService(ui, cancel_event=cancel_event)
            thumbnail.generate(project)

        # ==========================================
        # Sauvegarde
        # ==========================================

        self._check_cancel(cancel_event)

        ui.log("💾 Sauvegarde du projet...")
        ui.step("save")

        storage.save(project)

        ui.log("")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("✅ Projet terminé !")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("")

        return project