from pathlib import Path
from shutil import copy2

from assisted_editing.services.episode_storage import EpisodeStorage


class ResourcePreparer:

    def __init__(self, ui):

        self.ui = ui

    # ==================================================

    def prepare(
        self,
        episode,

        intro=True,
        intro_path=None,

        outro=True,
        outro_path=None,

        logo=True,
        logo_path=None,

        overlay=True,

        music=True,
        music_path=None,
    ):

        self.ui.log("📦 Préparation des ressources...")

        self.ui.log(f"intro      : {intro}")
        self.ui.log(f"intro_path : {intro_path}")

        self.ui.log(f"outro      : {outro}")
        self.ui.log(f"outro_path : {outro_path}")

        self.ui.log(f"logo       : {logo}")
        self.ui.log(f"logo_path  : {logo_path}")

        self.ui.log(f"music      : {music}")
        self.ui.log(f"music_path : {music_path}")

        resources_folder = (
            episode.episode_folder
            / "Resources"
        )

        resources_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ==========================================
        # Intro
        # ==========================================

        if intro and intro_path is not None:

            copy2(

                intro_path,

                resources_folder
                / intro_path.name,

            )

            self.ui.log(
                f"   ✅ Intro : {intro_path.name}"
            )

        # ==========================================
        # Outro
        # ==========================================

        if outro and outro_path is not None:

            copy2(

                outro_path,

                resources_folder
                / outro_path.name,

            )

            self.ui.log(
                f"   ✅ Outro : {outro_path.name}"
            )

        # ==========================================
        # Logo
        # ==========================================

        if logo and logo_path is not None:

            copy2(

                logo_path,

                resources_folder
                / logo_path.name,

            )

            self.ui.log(
                f"   ✅ Logo : {logo_path.name}"
            )

        # ==========================================
        # Musique
        # ==========================================

        if music and music_path is not None:

            copy2(

                music_path,

                resources_folder
                / music_path.name,

            )

            self.ui.log(
                f"   ✅ Musique : {music_path.name}"
            )

        # ==========================================

        storage = EpisodeStorage()

        project = storage.load(
            episode.episode_folder
        )

        project.prepared = True

        storage.save(
            project,
            episode.episode_folder,
        )

        self.ui.log("✅ Ressources préparées")