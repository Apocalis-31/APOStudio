from services.thumbnail.vision.vision_prompt import VisionPrompt
from services.ai.ai_factory import AIFactory


class VisionService:

    def __init__(self, ui):

        self.ui = ui

    def select(self, project, images):

        self.ui.log("🤖 Analyse des miniatures...")

        prompt = VisionPrompt().build(project)

        provider = AIFactory.create()

        result = provider.ask_vision(
            prompt["system"],
            prompt["user"],
            images
        )

        selected = images[result["best_index"]]

        return selected
