from services.ai.providers.base_provider import BaseProvider
from services.ai.openai_service import OpenAIService


class OpenAIProvider(BaseProvider):

    def __init__(self):

        self.client = OpenAIService()

    def ask_json(self, prompt):

        return self.client.ask_json(prompt)
    