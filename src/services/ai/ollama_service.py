import json
import requests

from services.config_service import ConfigService
from schemas.youtube_schema import YOUTUBE_SCHEMA


class OllamaService:

    def __init__(self):

        config = ConfigService()

        self.url = config.get("ollama.url")
        self.model = config.get("ollama.model")

    def ask(self, prompt: str):

        response = requests.post(

            f"{self.url}/api/generate",

            json={

                "model": self.model,
                "prompt": prompt,
                "stream": False

            }

        )

        response.raise_for_status()

        data = response.json()

        return data["response"]

    def ask_json(
        self,
        system_prompt,
        user_prompt
    ):

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "format": YOUTUBE_SCHEMA,
            "stream": False
        }

        response = requests.post(

            f"{self.url}/api/chat",

            json=payload,

            timeout=300

        )

        response.raise_for_status()

        data = response.json()

        text = data["message"]["content"]

        try:

            return json.loads(text)

        except json.JSONDecodeError:

            return None