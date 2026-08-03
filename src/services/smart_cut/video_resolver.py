from pathlib import Path

from parsers.filename_parser import FilenameParser
from services.project_storage import ProjectStorage
from services.path_service import PathService


class VideoResolver:

    def __init__(self, ui):

        self.ui = ui

    # ==========================================

    def resolve(self, video_path):

        print("DEBUG : Resolve", video_path)

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

        print("DEBUG : Projet trouvé")

        return self._find_project(parsed)

    # ==========================================

    def _find_project(self, parsed):

        project_folder = (
            PathService.projects()
            / parsed["series"]
        )

        self.ui.log("🔍 Recherche du dossier...")

        project_file = (
            project_folder
            / f"{parsed['series']}_apo_project.json"
        )

        self.ui.log(f"DEBUG : {project_file}")

        if not project_file.exists():

            self.ui.log("❌ Aucun projet trouvé")
            return None

        self.ui.log("✅ Projet trouvé")

        project = ProjectStorage().load(project_folder)

        # ==========================================
        # Vérification du transcript
        # ==========================================

        transcript = self._find_transcript(project)

        if transcript is None:

            self.ui.log("📝 Aucun transcript trouvé")
            return None

        self.ui.log(f"✅ Transcript trouvé : {transcript.name}")
        self.ui.log(f"📂 {transcript.parent}")

        return project

    # ==========================================

    def _find_transcript(self, project):

        candidates = []

        if project.project_path is not None:
            candidates.append(
                project.project_path / "transcript.txt"
            )

        if project.working_path is not None:
            candidates.append(
                project.working_path / "transcript.txt"
            )

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # Repli : recherche dans les dossiers "Episode N"
        if project.project_path is not None:

            for folder in sorted(
                project.project_path.glob("Episode *")
            ):

                candidate = folder / "transcript.txt"

                if candidate.exists():
                    return candidate

        return None