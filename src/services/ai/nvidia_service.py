import json
import base64
from openai import OpenAI
from services.config_service import ConfigService
from schemas.youtube_schema import YOUTUBE_SCHEMA


NVIDIA_MODELS = [
    ("DeepSeek V4 Flash", "deepseek-ai/deepseek-v4-flash"),
    ("DeepSeek V4 Pro", "deepseek-ai/deepseek-v4-pro"),
    ("Gemma 4 31B IT", "google/gemma-4-31b-it"),
    ("MiniMax M3", "minimaxai/minimax-m3"),
    ("Nemotron 3 Ultra 550B", "nvidia/nemotron-3-ultra-550b-a55b"),
    ("Qwen3.5 122B-A10B", "qwen/qwen3.5-122b-a10b"),
]

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


class NvidiaService:

    def __init__(self, ui=None):

        self.ui = ui

        config = ConfigService()

        self.model = config.get("nvidia.model")

        self.client = OpenAI(
            api_key=config.get("nvidia.api_key"),
            base_url=NVIDIA_BASE_URL
        )

    def ask(self, prompt: str):

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:

            return f"ERREUR NVIDIA : {e}"

    def ask_json(
            self,
            system_prompt: str,
            user_prompt: str
        ):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def ask_vision(
        self,
        system_prompt,
        user_prompt,
        images
    ):

        images = images[:5]

        content = [
            {"type": "text", "text": system_prompt},
            {"type": "text", "text": user_prompt}
        ]

        for index, image in enumerate(images):

            with open(image, "rb") as f:
                image_base64 = base64.b64encode(
                    f.read()
                ).decode("utf-8")

            content.append({
                "type": "text",
                "text": f"Image {index}"
            })

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                }
            })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": content}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
