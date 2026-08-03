from pathlib import Path

from assisted_editing.models.episode_info import EpisodeInfo
from assisted_editing.services.episode_storage import EpisodeStorage

from services.path_service import PathService


class EpisodeRepository:

    # ==========================================

    def get_pending(self):

        episodes = []

        projects_root = PathService.projects()

        if not projects_root.exists():
            return episodes

        storage = EpisodeStorage()

        # ==========================================
        # Toutes les séries
        # ==========================================

        for project_folder in sorted(projects_root.iterdir()):

            if not project_folder.is_dir():
                continue

            # ======================================
            # Tous les dossiers Episode X
            # ======================================

            for episode_folder in sorted(
                project_folder.glob("Episode *")
            ):

                if not episode_folder.is_dir():
                    continue

                if not storage.exists(
                    episode_folder
                ):
                    continue

                project = storage.load(
                    episode_folder
                )

                if project.prepared:
                    continue

                # ==================================
                # Recherche de la vidéo
                # ==================================

                videos = list(
                    episode_folder.glob("*.mp4")
                )

                if not videos:
                    continue

                master_video = videos[0]

                # ==================================
                # youtube.json
                # ==================================

                youtube_json = (
                    episode_folder
                    / "youtube.json"
                )

                episodes.append(

                    EpisodeInfo(

                        project_name=project.series,

                        episode_number=project.episode,

                        title=(
                            f"Episode {project.episode}"
                        ),

                        episode_folder=episode_folder,

                        master_video=master_video,

                        youtube_json=youtube_json,

                        project=project,

                    )

                )

        episodes.sort(

            key=lambda e: (

                e.project_name.lower(),

                e.episode_number,

            )

        )

        return episodes