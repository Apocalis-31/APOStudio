from models.project import Project
import base64
from pathlib import Path
from services.ai.glm_service import GLMService
from services.thumbnail.frame_tournament import FrameTournament
from services.ai.glm_parser import GLMParser
from services.path_service import PathService
import cv2

VISION_MAX_SIZE = 512



class FrameVision:

    def __init__(self, ui, cancel_event=None):

        self.ui = ui
        self.cancel_event = cancel_event



    # =====================================================

    def rank(
        self,
        project: Project,
        frames: list
    ):

        images = self._encode_images(frames)

        prompt = self._build_prompt()
        
        response, finalists = FrameTournament(
            self.ui, cancel_event=self.cancel_event
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

            image = cv2.imread(str(frame))

            height, width = image.shape[:2]

            scale = min(
                VISION_MAX_SIZE / width,
                VISION_MAX_SIZE / height,
                1.0
            )

            if scale < 1.0:

                new_width = int(width * scale)
                new_height = int(height * scale)

                image = cv2.resize(
                    image,
                    (new_width, new_height),
                    interpolation=cv2.INTER_AREA
                )

            success, buffer = cv2.imencode(
                ".jpg",
                image,
                [cv2.IMWRITE_JPEG_QUALITY, 90]
            )

            raw_size = len(buffer)
            base64_size = len(base64.b64encode(buffer))

            self.ui.log(
                f"{Path(frame).name} : "
                f"{raw_size/1024:.1f} Ko "
                f"({base64_size/1024:.1f} Ko en Base64)"
            )

            if not success:
                raise Exception(
                    f"Impossible d'encoder : {frame}"
                )

            images.append(
                {
                    "path": frame,
                    "base64": base64.b64encode(
                        buffer.tobytes()
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