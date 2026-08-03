import json

from pathlib import Path

from assisted_editing.models.episode_project import (
    EpisodeProject
)


class EpisodeStorage:

    FILE_NAME = "apo_episode.json"

    # ==========================================

    def save(
        self,
        episode: EpisodeProject,
        folder: Path
    ):

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        path = folder / self.FILE_NAME

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                episode.__dict__,
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================

    def load(
        self,
        folder: Path
    ) -> EpisodeProject:

        path = folder / self.FILE_NAME

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return EpisodeProject(**data)

    # ==========================================

    def exists(
        self,
        folder: Path
    ) -> bool:

        return (
            folder / self.FILE_NAME
        ).exists()