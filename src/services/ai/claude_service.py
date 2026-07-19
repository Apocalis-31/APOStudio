import json

from anthropic import Anthropic

from services.config_service import ConfigService


class ClaudeService:

    def __init__(self):

        config = ConfigService()

        self.client = Anthropic(
            api_key=config.get("claude.api_key")
        )

        self.model = config.get("claude.model")

    def ask(self, prompt: str):

        try:

            response = self.client.messages.create(

                model=self.model,

                max_tokens=4096,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:

            return f"ERREUR CLAUDE : {e}"
        
    def ask_json(
            self,
            system_prompt,
            user_prompt
        ):

        response = self.client.messages.create(

            model=self.model,

            system=system_prompt,

            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            max_tokens=4096

        )