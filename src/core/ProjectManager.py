from pathlib import Path

from parsers.filename_parser import FilenameParser
from models.project import Project

from services.project_storage import ProjectStorage
from services.ai.whisper_service import WhisperService
from services.ai.youtube_service import YoutubeService
from services.thumbnail.thumbnail_service import ThumbnailService

from services.workflow.workflow_manager import WorkflowManager


class ProjectManager:

    def create_project(
        self,
        video_path: str,
        ui,
        forced_modules=None
    ) -> Project:

        video = Path(video_path)

        ui.log("")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("🎬 Traitement de la vidéo")
        ui.log(f"📄 {video.name}")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("")

        name = video.stem

        parser = FilenameParser()

        parsed = parser.parse(video_path)

        print(parsed)
        print(type(parsed["episode"]))

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

        print("VIDEO =", project.video_path)
        print("PROJECT =", project.project_path)

        storage.save(project)

        # ==========================================
        # Transcription
        # ==========================================

        if workflow.enabled("transcription"):

            ui.log("🎙️ Chargement de Whisper...")
            ui.step("whisper")

            transcript = project.project_path / "transcript.txt"

            if transcript.exists():

                ui.log("✅ Transcription déjà présente")
                project.transcription_done = True

            else:

                whisper = WhisperService(ui=ui)
                print("AVANT WHISPER")
                print("VIDEO =", project.video_path)
                print("PROJECT =", project.project_path)
                whisper.transcribe(project)

        # ==========================================
        # YouTube
        # ==========================================

        if workflow.enabled("youtube"):

            ui.step("youtube")

            youtube = YoutubeService(ui)
            youtube.generate(project)

        # ==========================================
        # Thumbnail
        # ==========================================

        if workflow.enabled("thumbnail"):

            ui.step("thumbnail")

            thumbnail = ThumbnailService(ui)
            thumbnail.generate(project)

        # ==========================================
        # Sauvegarde
        # ==========================================

        ui.log("💾 Sauvegarde du projet...")
        ui.step("save")

        storage.save(project)

        ui.log("")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("✅ Projet terminé !")
        ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        ui.log("")

        return project