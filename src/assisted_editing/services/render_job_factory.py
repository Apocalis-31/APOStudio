from pathlib import Path
import json

from assisted_editing.models.render_job import RenderJob
from assisted_editing.models.resource import Resource
from assisted_editing.models.resource_type import ResourceType


class RenderJobFactory:
    """
    Construit un RenderJob à partir
    d'un épisode préparé.
    """

    # ==================================================

    def build(
        self,
        episode,
    ) -> RenderJob:

        resources = (
            episode.episode_folder
            / "Resources"
        )

        return RenderJob(

            master_video=episode.master_video,

            output_video=(
                episode.episode_folder
                / self._build_output_filename(
                    episode
                )
            ),

            introduction=self._load_resource(
                resources,
                "intro",
                ResourceType.INTRODUCTION,
            ),

            ending=self._load_resource(
                resources,
                "outro",
                ResourceType.ENDING,
            ),

            logo=self._load_resource(
                resources,
                "logo",
                ResourceType.LOGO,
            ),

            overlays=[],

            music=self._load_resource(
                resources,
                "music",
                ResourceType.MUSIC,
            ),

            fade_in=1.5,

            fade_out=1.5,

        )

    # ==================================================

    def _load_resource(
        self,
        folder: Path,
        name: str,
        resource_type: ResourceType,
    ) -> Resource | None:

        if not folder.exists():
            return None

        for file in folder.iterdir():

            if not file.is_file():
                continue

            if file.stem != name:
                continue

            return Resource(

                name=name,

                type=resource_type,

                path=file,

            )

        return None

    # ==================================================

    def _build_output_filename(
        self,
        episode,
    ) -> str:

        with open(
            episode.youtube_json,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        subtitle = (
            data
            .get("youtube", {})
            .get("subtitle", "")
            .strip()
        )

        if subtitle:

            filename = (
                f"{episode.master_video.stem}"
                f" - {subtitle}"
            )

        else:

            filename = (
                f"{episode.master_video.stem}"
            )

        return (
            f"{self._sanitize_filename(filename)}.mp4"
        )

    # ==================================================

    def _sanitize_filename(
        self,
        filename: str,
    ) -> str:

        invalid_characters = '<>:"/\\|?*'

        for character in invalid_characters:

            filename = filename.replace(
                character,
                "",
            )

        return filename.strip()