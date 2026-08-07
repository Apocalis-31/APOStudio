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

        if not intro:

            self._remove_resource(
                resources_folder,
                "intro",
            )

        elif intro_path is not None:

            destination = (
                resources_folder
                / f"intro{intro_path.suffix}"
            )

            if intro_path.resolve() == destination.resolve():

                self.ui.log(
                    "   ⏩ Intro déjà présente"
                )

            else:

                copy2(
                    intro_path,
                    destination,
                )

                self.ui.log(
                    f"   ✅ Intro : {destination.name}"
                )

        # ==========================================
        # Outro
        # ==========================================

        if not outro:

            self._remove_resource(
                resources_folder,
                "outro",
            )

        elif outro_path is not None:

            destination = (
                resources_folder
                / f"outro{outro_path.suffix}"
            )

            if outro_path.resolve() == destination.resolve():

                self.ui.log(
                    "   ⏩ Outro déjà présent"
                )

            else:

                copy2(
                    outro_path,
                    destination,
                )

                self.ui.log(
                    f"   ✅ Outro : {destination.name}"
                )

        # ==========================================
        # Logo
        # ==========================================

        if not logo:

            self._remove_resource(
                resources_folder,
                "logo",
            )

        elif logo_path is not None:

            destination = (
                resources_folder
                / f"logo{logo_path.suffix}"
            )

            if logo_path.resolve() == destination.resolve():

                self.ui.log(
                    "   ⏩ Logo déjà présent"
                )

            else:

                copy2(
                    logo_path,
                    destination,
                )

                self.ui.log(
                    f"   ✅ Logo : {destination.name}"
                )

        # ==========================================
        # Musique
        # ==========================================

        if not music:

            self._remove_resource(
                resources_folder,
                "music",
            )

        elif music_path is not None:

            destination = (
                resources_folder
                / f"music{music_path.suffix}"
            )

            if music_path.resolve() == destination.resolve():

                self.ui.log(
                    "   ⏩ Musique déjà présente"
                )

            else:

                copy2(
                    music_path,
                    destination,
                )

                self.ui.log(
                    f"   ✅ Musique : {destination.name}"
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

    # ==================================================

    def _remove_resource(
        self,
        resources_folder,
        name: str,
    ):

        removed = False

        for file in resources_folder.glob(f"{name}.*"):

            file.unlink()

            removed = True

            self.ui.log(
                f"   🗑️ {file.name} supprimé"
            )

        if not removed:

            self.ui.log(
                f"   ⏩ Aucun {name} à supprimer"
            )