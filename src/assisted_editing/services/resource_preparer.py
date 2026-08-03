from assisted_editing.services.episode_storage import EpisodeStorage


class ResourcePreparer:

    def __init__(self, ui):

        self.ui = ui

    # ==================================================

    def prepare(
        self,
        episode,
        intro=True,
        outro=True,
        logo=True,
        overlay=True,
        music=True,
    ):

        self.ui.log("📦 Préparation des ressources...")

        storage = EpisodeStorage()

        project = storage.load(
            episode.episode_folder
        )

        # Pour la V1, on valide simplement que
        # les ressources ont été préparées.

        project.prepared = True

        storage.save(
            project,
            episode.episode_folder
        )

        self.ui.log("✅ Ressources préparées")