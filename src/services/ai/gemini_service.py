import json
import base64
import requests
from services.config_service import ConfigService


GEMINI_MODELS = [
    ("Gemini 3.6 Flash", "gemini-3.6-flash"),
    ("Gemini 3.5 Flash", "gemini-3.5-flash"),
    ("Gemini 3.1 Pro Preview", "gemini-3.1-pro-preview"),
    ("Gemini 2.5 Pro", "gemini-2.5-pro"),
    ("Gemini 2.5 Flash", "gemini-2.5-flash"),
    ("Gemini 2.5 Flash Lite", "gemini-2.5-flash-lite"),
]

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiService:

    def __init__(self, ui=None):

        self.ui = ui

        config = ConfigService()

        self.model = config.get("gemini.model")
        self.api_key = config.get("gemini.api_key")

    def _url(self, action="generateContent"):

        return (
            f"{GEMINI_BASE_URL}/models/{self.model}:{action}"
            f"?key={self.api_key}"
        )

    def _headers(self):

        return {"Content-Type": "application/json"}

    def _call(self, contents, system_instruction=None):

        body = {"contents": contents}

        if system_instruction:
            body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        response = requests.post(
            self._url(),
            headers=self._headers(),
            json=body,
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    def ask(self, prompt: str):

        try:

            contents = [
                {"role": "user", "parts": [{"text": prompt}]}
            ]

            return self._call(contents)

        except Exception as e:

            return f"ERREUR GEMINI : {e}"

    def ask_json(
            self,
            system_prompt: str,
            user_prompt: str
        ):

        contents = [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ]

        result = self._call(
            contents,
            system_instruction=system_prompt
        )

        cleaned = result.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        return json.loads(cleaned)

    def ask_vision(
        self,
        system_prompt,
        user_prompt,
        images
    ):

        images = images[:5]

        parts = [
            {"text": user_prompt}
        ]

        for image in images:

            with open(image, "rb") as f:
                image_base64 = base64.b64encode(
                    f.read()
                ).decode("utf-8")

            parts.append({
                "inlineData": {
                    "mimeType": "image/png",
                    "data": image_base64
                }
            })

        contents = [
            {"role": "user", "parts": parts}
        ]

        result = self._call(
            contents,
            system_instruction=system_prompt
        )

        cleaned = result.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

        return json.loads(cleaned)
