from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Project:

    name: str
    series: str

    # Prochain épisode qui sera généré
    next_episode: int = 1

    video_path: Path = None

    # Dossier de la série
    project_path: Path | None = None

    # Dossier de travail courant
    working_path: Path | None = None

    transcription_done: bool = False
    analysis_done: bool = False

    def to_dict(self):

        data = asdict(self)

        data["video_path"] = str(self.video_path)

        if self.project_path is not None:
            data["project_path"] = str(self.project_path)

        if self.working_path is not None:
            data["working_path"] = str(self.working_path)

        return data

    @classmethod
    def from_dict(cls, data: dict):

        project = cls(

            name=data["name"],
            series=data["series"],
            next_episode=int(data.get("next_episode") or 1),
            video_path=Path(data["video_path"])

        )

        if data.get("project_path"):

            project.project_path = Path(
                data["project_path"]
            )

        if data.get("working_path"):

            project.working_path = Path(
                data["working_path"]
            )

        project.transcription_done = data.get(
            "transcription_done",
            False
        )

        project.analysis_done = data.get(
            "analysis_done",
            False
        )

        return project