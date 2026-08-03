from assisted_editing.services.resource_preparer import ResourcePreparer


class EditingEngine:

    def __init__(self, ui):

        self.ui = ui

    # ==========================================

    def prepare(
        self,
        episode,
        intro=True,
        outro=True,
        logo=True,
        overlay=True,
        music=True,
    ):

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🎬 Montage Assisté")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log(
            f"Série : {episode.project_name}"
        )

        self.ui.log(
            f"Episode : {episode.episode_number}"
        )

        self.ui.log("")

        self.ui.log("Ressources :")

        self.ui.log(
            f"{'✅' if intro else '❌'} Intro"
        )

        self.ui.log(
            f"{'✅' if outro else '❌'} Outro"
        )

        self.ui.log(
            f"{'✅' if logo else '❌'} Logo"
        )

        self.ui.log(
            f"{'✅' if overlay else '❌'} Overlays"
        )

        self.ui.log(
            f"{'✅' if music else '❌'} Musique"
        )

        self.ui.log("")

        ResourcePreparer(self.ui).prepare(

            episode,

            intro=intro,

            outro=outro,

            logo=logo,

            overlay=overlay,

            music=music,

        )

        self.ui.log("")
        self.ui.log("✅ Episode préparé.")