from unittest import result

from models.project import Project
import json
from services.ai.prompt_builder import PromptBuilder
from services.ai.ai_factory import AIFactory
from services.config_service import ConfigService


class YoutubeService:

    def __init__(self, ui):

        self.ui = ui

    def generate(self, project: Project):

        provider = AIFactory.create(self.ui)

        self.ui.log(f"🤖 IA utilisée : {provider.__class__.__name__}")

        self.ui.log("🧠 Génération des données YouTube...")

        self.ui.log("🧩 Construction du prompt...")

        builder = PromptBuilder()

        provider_name = ConfigService().get("ai.provider")

        prompt = builder.build(
            project,
            provider_name
        )

        prompt_file = project.project_path / "prompt.txt"

        with open(prompt_file, "w", encoding="utf-8") as f:

            f.write("========== SYSTEM ==========\n\n")
            f.write(prompt.system)

            f.write("\n\n========== USER ==========\n\n")
            f.write(prompt.user)

        self.ui.log("📄 Prompt généré")

        self.ui.log("🤖 Envoi du prompt à l'IA...")

        result = provider.ask_json(
            prompt.system,
            prompt.user
            )

        self.ui.log("✅ Réponse reçue !")

        output = project.project_path / "youtube.json"

        data = result

        data["version"] = "1.0"
        data["game"] = project.series
        data["episode"] = project.episode

        with open(output, "w", encoding="utf-8") as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        self.ui.log("✅ youtube.json créé")

        self.save_intro(
            project,
            data
        )

    def save_intro(self, project: Project, data):

        intro_file = project.project_path / "intro.txt"

        subtitle = data["youtube"]["subtitle"]
        intro = data["intro"]["text"]

        content = f"""\
    ====================================================
                APO STUDIO - INTRO YOUTUBE
    ====================================================

    🎬 Projet

    {project.name}

    ----------------------------------------------------

    📝 Sous-titre

    {subtitle}

    ----------------------------------------------------

    🎤 INTRODUCTION

    {intro}

    ====================================================

    Généré automatiquement par APO Studio
    """

        with open(intro_file, "w", encoding="utf-8") as f:
            f.write(content)

        self.ui.log("📄 intro.txt créé")