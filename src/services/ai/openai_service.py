import json
import base64
from schemas.youtube_schema import YOUTUBE_SCHEMA
from openai import OpenAI
from services.config_service import ConfigService
import traceback

class OpenAIService:


    def __init__(self, ui=None):

        self.ui = ui

        config = ConfigService()

        self.model = config.get("openai.model")

        self.client = OpenAI(
            api_key=config.get("openai.api_key")
        )

    def ask(self, prompt: str):

        try:

            response = self.client.responses.create(
                model="gpt-5.5",
                input=prompt
            )

            return response.output_text

        except Exception as e:

            return f"ERREUR OPENAI : {e}"
        
    def ask_json(
            self,
            system_prompt: str,
            user_prompt: str
        ):

        response = self.client.responses.create(

            model=self.model,

            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            text={
                "format": {
                    "type": "json_schema",
                    "name": "youtube",
                    "schema": YOUTUBE_SCHEMA
                }
            }

        )

        return json.loads(response.output_text)
    

    def ask_vision(
        self,
        system_prompt,
        user_prompt,
        images
    ):



        images = images[:5]

        images = images[:5]

        vision_images = []

        content = [
            {
                "type": "input_text",
                "text": system_prompt
            },
            {
                "type": "input_text",
                "text": user_prompt
            }
        ]

        for index, image in enumerate(images):

            with open(image, "rb") as f:

                image_base64 = base64.b64encode(
                    f.read()
                ).decode("utf-8")

            content.append({
                "type": "input_text",
                "text": f"Image {index}"
            })

            content.append({
                "type": "input_image",
                "image_url": f"data:image/png;base64,{image_base64}"
            })

        response = self.client.responses.create(

            model="gpt-5.5",

            input=[
                {
                    "role": "user",
                    "content": content
                }
            ],

           text={
                "format": {
                    "type": "json_schema",
                    "name": "youtube",
                    "schema": YOUTUBE_SCHEMA
                }
            }
        )

        return json.loads(response.output_text)