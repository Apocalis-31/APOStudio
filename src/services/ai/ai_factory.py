from services.ai.ollama_service import OllamaService
from services.ai.openai_service import OpenAIService
from services.config_service import ConfigService
from services.ai.glm_service import GLMService


class AIFactory:

    @staticmethod
    def create(ui=None):

        config = ConfigService()

        provider = config.get("ai.provider")

        if provider == "openai":
            return OpenAIService(ui)

        elif provider == "claude":
            return ClaudeService(ui)

        elif provider == "ollama":
            return OllamaService(ui)
        
        elif provider == "glm":
            return GLMService(ui)

        raise ValueError(
            f"Provider inconnu : {provider}"
        )
    
