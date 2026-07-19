import customtkinter as ctk

from services.config_service import ConfigService


class AIStatus(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        self.config = ConfigService()

        # Provider (GLM, OpenAI, Claude...)

        self.provider = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        )

        # Modèle

        self.model = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 13),
            text_color="gray70",
            anchor="w"
        )

        self.provider.pack(
            anchor="w"
        )

        self.model.pack(
            anchor="w",
            pady=(2, 0)
        )

        self.refresh()

    def refresh(self):

        self.config = ConfigService()

        provider = self.config.get("ai.provider")
        model = self.config.get(f"{provider}.model")

        icons = {
            "openai": "🟢",
            "claude": "🟣",
            "glm": "🔵",
            "ollama": "🟠"
        }

        icon = icons.get(provider.lower(), "🤖")

        self.provider.configure(
            text=f"{icon} {provider.upper()}"
        )

        self.model.configure(
            text=model
        )