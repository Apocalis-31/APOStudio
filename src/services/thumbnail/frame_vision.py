from models.project import Project
import base64
from pathlib import Path
from services.ai.glm_service import GLMService
from services.thumbnail.frame_tournament import FrameTournament
from services.ai.glm_parser import GLMParser
from services.path_service import PathService

class FrameVision:

    def __init__(self, ui):

        self.ui = ui

    # =====================================================

    def rank(
        self,
        project: Project,
        frames: list
    ):

        images = self._encode_images(frames)

        prompt = self._build_prompt()
        
        response, finalists = FrameTournament(
            self.ui
        ).run(
            prompt,
            images
        )

        self._validate_response(
            response,
            len(finalists)
        )

        return self._sort_frames(
            finalists,
            response
        )

    # =====================================================

    def _encode_images(
        self,
        frames
    ):

        self.ui.log(
            f"📦 Encodage de {len(frames)} captures..."
        )

        images = []

        for frame in frames:

            with open(frame, "rb") as f:

                images.append(
                    {
                        "path": frame,
                        "base64": base64.b64encode(
                            f.read()
                        ).decode("utf-8")
                    }
                )

        return images

    # =====================================================

    def _build_prompt(self):

        prompt = (
            PathService.prompts()
            / "thumbnail_vision.md"
        )

        return prompt.read_text(
            encoding="utf-8"
        )

    # =====================================================

    def _validate_response(
        self,
        response,
        image_count
    ):

        if "ranking" not in response:
            raise Exception(
                "GLM n'a renvoyé aucun classement."
            )

        ranking = [
            int(index)
            for index in response["ranking"]
        ]

        if not ranking:
            raise Exception(
                "Classement vide."
            )

        return ranking
    # =====================================================

    def _sort_frames(
        self,
        images,
        response
    ):

        ranking = response["ranking"]

        sorted_frames = []

        for index in ranking[:3]:

            parsed = GLMParser.parse_index(index)

            sorted_frames.append(
                images[parsed - 1]["path"]
            )

        return sorted_frames