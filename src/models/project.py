from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Project:

    name: str
    series: str
    episode: str | None
    video_path: Path

    project_path: Path | None = None

    transcription_done: bool = False
    analysis_done: bool = False

    def to_dict(self):

        data = asdict(self)

        # Les objets Path ne sont pas compatibles JSON
        data["video_path"] = str(self.video_path)

        if self.project_path is not None:
            data["project_path"] = str(self.project_path)

        return data
    
    @classmethod
    def from_dict(
        cls,
        data: dict
    ):

        episode = data.get("episode")

        if episode is not None:
            episode = int(episode)

        project = cls(

            name=data["name"],

            series=data["series"],

            episode=episode,

            video_path=Path(data["video_path"])

        )

        if data.get("project_path"):

            project.project_path = Path(
                data["project_path"]
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