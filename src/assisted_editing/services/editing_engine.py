from assisted_editing.services.resource_preparer import ResourcePreparer


class EditingEngine:

    def __init__(self, ui):

        self.ui = ui

    # ==========================================

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

        if intro and intro_path:
            self.ui.log(f"   ↳ {intro_path.name}")

        self.ui.log(
            f"{'✅' if outro else '❌'} Outro"
        )

        if outro and outro_path:
            self.ui.log(f"   ↳ {outro_path.name}")

        self.ui.log(
            f"{'✅' if logo else '❌'} Logo"
        )

        if logo and logo_path:
            self.ui.log(f"   ↳ {logo_path.name}")

        self.ui.log(
            f"{'✅' if overlay else '❌'} Overlays"
        )

        self.ui.log(
            f"{'✅' if music else '❌'} Musique"
        )

        if music and music_path:
            self.ui.log(f"   ↳ {music_path.name}")

        self.ui.log("")

        ResourcePreparer(self.ui).prepare(

            episode,

            intro=intro,
            intro_path=intro_path,

            outro=outro,
            outro_path=outro_path,

            logo=logo,
            logo_path=logo_path,

            overlay=overlay,

            music=music,
            music_path=music_path,

        )

        self.ui.log("")
        self.ui.log("✅ Episode préparé.")