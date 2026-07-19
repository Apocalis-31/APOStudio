import json

from pathlib import Path

from models import project
from models.project import Project
from services.path_service import PathService


class ProjectStorage:

  
    def save(self, project: Project):

        root = PathService.projects()

        print(f"[ProjectStorage] Root = {root}")

        series_folder = root / project.series

        print(f"[ProjectStorage] Project = {series_folder}")

        if project.episode:
            project_folder = series_folder / f"Episode {project.episode}"
        else:
            project_folder = series_folder

        project_folder.mkdir(parents=True, exist_ok=True)

        project.project_path = project_folder

        project_file = project_folder / "apo_project.json"

        with open(project_file, "w", encoding="utf-8") as file:

            json.dump(
                project.to_dict(),
                file,
                indent=4,
                ensure_ascii=False
            )

        return project_folder
    
    def load(
        self,
        project_folder: Path
    ) -> Project:

        project_file = (
            project_folder
            / "apo_project.json"
        )

        with open(
            project_file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        project = Project.from_dict(data)

        project.project_path = project_folder

        return project