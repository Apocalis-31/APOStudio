from pathlib import Path
from shutil import copy2

from assisted_editing.models.resource import Resource
from assisted_editing.models.resource_type import ResourceType


class ResourceLibrary:
    """Gestion de la bibliothèque des ressources d'APO Studio."""

    _RESOURCE_DIRECTORIES = {
        ResourceType.INTRODUCTION: "Introduction",
        ResourceType.ENDING: "Ending",
        ResourceType.OVERLAY: "Overlay",
        ResourceType.MUSIC: "Music",
    }

    def __init__(self, library_path: Path) -> None:
        self._library_path = library_path

    def import_resource(
        self,
        resource_type: ResourceType,
        source_path: Path,
    ) -> Resource:
        """
        Importe une ressource dans la bibliothèque.

        Args:
            resource_type: Type de la ressource.
            source_path: Chemin du fichier à importer.

        Returns:
            La ressource importée.

        Raises:
            FileNotFoundError: Si le fichier source n'existe pas.
            FileExistsError: Si une ressource du même nom existe déjà.
        """

        if not source_path.exists():
            raise FileNotFoundError(source_path)

        destination_directory = (
            self._library_path
            / self._RESOURCE_DIRECTORIES[resource_type]
        )

        destination_directory.mkdir(parents=True, exist_ok=True)

        destination_path = destination_directory / source_path.name

        if destination_path.exists():
            raise FileExistsError(destination_path)

        copy2(source_path, destination_path)

        return Resource(
            name=destination_path.stem,
            type=resource_type,
            path=destination_path,
        )

    def list_resources(
        self,
        resource_type: ResourceType,
    ) -> list[Resource]:
        """
        Retourne toutes les ressources d'un type.
        """

        directory = (
            self._library_path
            / self._RESOURCE_DIRECTORIES[resource_type]
        )

        if not directory.exists():
            return []

        resources: list[Resource] = []

        for file in sorted(directory.iterdir()):
            if not file.is_file():
                continue

            resources.append(
                Resource(
                    name=file.stem,
                    type=resource_type,
                    path=file,
                )
            )

        return resources

    def delete_resource(
        self,
        resource: Resource,
    ) -> None:
        """
        Supprime une ressource de la bibliothèque.
        """

        if resource.path.exists():
            resource.path.unlink()