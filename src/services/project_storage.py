import json

from pathlib import Path

from models.project import Project
from services.path_service import PathService


class ProjectStorage:

    def save(self, project: Project):

        root = PathService.projects()

        # Dossier de la série
        series_folder = root / project.series
        series_folder.mkdir(parents=True, exist_ok=True)

        project.project_path = series_folder

        # Si aucun dossier de travail n'est défini,
        # on travaille par défaut dans le dossier de la série.
        if project.working_path is None:
            project.working_path = series_folder

        # Fichier projet
        project_file = (
            series_folder
            / f"{project.series}_apo_project.json"
        )

        with open(project_file, "w", encoding="utf-8") as file:

            json.dump(
                project.to_dict(),
                file,
                indent=4,
                ensure_ascii=False
            )

        return series_folder

    def load(
        self,
        project_folder: Path
    ) -> Project:

        project_file = (
            project_folder
            / f"{project_folder.name}_apo_project.json"
        )

        with open(
            project_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        project = Project.from_dict(data)

        project.project_path = project_folder

        if project.working_path is None:
            project.working_path = project_folder

        return project

    def exists(self, series):

        project_folder = PathService.projects() / series

        project_file = (
            project_folder
            / f"{series}_apo_project.json"
        )

        return project_file.exists()