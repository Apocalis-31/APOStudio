class BaseAI:

    def ask_json(self, prompt):
        raise NotImplementedError
    
class OpenAIService(BaseAI):
    pass

class ClaudeService(BaseAI):
    pass