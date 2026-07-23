from pathlib import Path
import json
from services.path_service import PathService

DEFAULT_CONFIG = {
    "ai": {
        "provider": "openai"
    },

    "openai": {
        "api_key": "",
        "model": "gpt-5.5"
    },

    "claude": {
        "api_key": "",
        "model": "claude-sonnet-4"
    },

    "glm": {
        "api_key": "",
        "model": "glm-4.7-flash",
        "vision_model": "glm-4.6v-flash",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/"
    },

    "nvidia": {
        "api_key": "",
        "model": "deepseek-ai/deepseek-v4-flash"
    },

    "gemini": {
        "api_key": "",
        "model": "gemini-2.5-flash"
    },

    "ollama": {
        "url": "http://localhost:11434",
        "model": "llama3.2"
    },

    "lmstudio": {
        "url": "http://localhost:1234/v1",
        "model": ""
    },

    "paths": {
            "projects": ""
        },
}


class ConfigService:

    def __init__(self):

        root = PathService.ffmpeg()

        self.config_path = (
            PathService.config()
            / "config.json"
        )
        if not self.config_path.exists():
            self.create_default_config()

        self.load()

        if self._merge_defaults(DEFAULT_CONFIG, self.data):
            self.save()

    def create_default_config(self):

        self.config_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        with open(self.config_path, "w", encoding="utf-8") as f:

            json.dump(
                DEFAULT_CONFIG,
                f,
                indent=4,
                ensure_ascii=False
            )

    def load(self):

        with open(self.config_path, encoding="utf-8") as f:

            self.data = json.load(f)

    def get(self, path, default=None):

        value = self.data

        for key in path.split("."):

            if key not in value:
                return default

            value = value[key]

        return value

    def set(self, path, value):

        keys = path.split(".")

        data = self.data

        for key in keys[:-1]:
            data = data[key]

        data[keys[-1]] = value

    def save(self):

        with open(
            self.config_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.data,
                f,
                indent=4,
                ensure_ascii=False
            )

    def _merge_defaults(self, defaults, current):
        modified = False

        for key, value in defaults.items():
            if key not in current:
                current[key] = value
                modified = True
            elif isinstance(value, dict) and isinstance(current[key], dict):
                if self._merge_defaults(value, current[key]):
                    modified = True

        return modified

