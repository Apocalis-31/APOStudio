from pathlib import Path
from parsers.filename_parser import FilenameParser
from services.project_storage import ProjectStorage
from services.path_service import PathService

class VideoResolver:

    def __init__(self, ui):

        self.ui = ui

    # ==========================================

    def resolve(self, video_path):

        video = Path(video_path)

        parser = FilenameParser()
        parsed = parser.parse(video_path)

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("📂 Recherche du projet")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.ui.log(f"🎬 {video.name}")

        self.ui.log("🔍 Analyse du nom...")
        self.ui.log(f"📺 Série : {parsed['series']}")
        self.ui.log(f"🎞️ Épisode : {parsed['episode']}")

        project = self._find_project(parsed)

        if project:
            return project

        return None
    # ==========================================

    def _find_project(
            self,
            parsed
        ):

            project_folder = (
                PathService.projects()
                / parsed["series"]
            )

            # Si on cherche un épisode, on descend dans son dossier
            if parsed["episode"] is not None:

                project_folder /= (
                    f"Episode {parsed['episode']}"
                )

            self.ui.log("🔍 Recherche du dossier...")

            project_file = (
                project_folder
                / "apo_project.json"
            )

            self.ui.log(
                f"DEBUG : {project_file}"
            )

            if not project_file.exists():

                self.ui.log("❌ Aucun projet trouvé")

                return None

            self.ui.log("✅ Projet trouvé")

            return ProjectStorage().load(
                project_folder
            )