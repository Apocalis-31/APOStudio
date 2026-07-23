import customtkinter as ctk
from tkinter import filedialog
from services.config_service import ConfigService
from services.ai.nvidia_service import NVIDIA_MODELS
from services.ai.gemini_service import GEMINI_MODELS


PROVIDER_MODELS = {
    "nvidia": NVIDIA_MODELS,
    "gemini": GEMINI_MODELS,
}

API_KEY_PROVIDERS = ("openai", "claude", "glm", "nvidia", "gemini")


class SettingsWindow(ctk.CTkToplevel):

    FIELD_WIDTH = 320

    def __init__(self, master):

        super().__init__(master)

        self.transient(master)
        self.lift()
        self.focus_force()
        self.grab_set()

        self.config_service = ConfigService()

        provider = self.config_service.get("ai.provider")

        if provider in API_KEY_PROVIDERS:
            value1 = self.config_service.get(f"{provider}.api_key")
            value2 = self.config_service.get(f"{provider}.model")
        else:
            value1 = self.config_service.get(f"{provider}.url")
            value2 = self.config_service.get(f"{provider}.model")

        self.title("Paramètres - APO Studio")
        self.geometry("650x550")
        self.resizable(False, False)
        self.grab_set()

        title = ctk.CTkLabel(
            self,
            text="⚙ Paramètres",
            font=("Segoe UI", 24, "bold")
        )
        title.pack(pady=(25, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Configuration d'APO Studio",
            font=("Segoe UI", 14)
        )
        subtitle.pack()

        # =====================================================
        # Fournisseur IA
        # =====================================================

        provider_title = ctk.CTkLabel(
            self,
            text="🤖 Fournisseur IA",
            font=("Segoe UI", 14, "bold")
        )
        provider_title.pack(pady=(35, 5))

        self.provider_combo = ctk.CTkComboBox(
            self,
            values=[
                "openai",
                "claude",
                "nvidia",
                "gemini",
                "ollama",
                "lmstudio",
                "glm"
            ],
            width=self.FIELD_WIDTH,
            command=self.on_provider_changed
        )

        self.provider_combo.pack()
        self.provider_combo.set(provider)

        # =====================================================
        # Clé API / URL
        # =====================================================

        self.api_title = ctk.CTkLabel(
            self,
            text="🔑 Clé API",
            font=("Segoe UI", 14, "bold")
        )
        self.api_title.pack(pady=(20, 5))

        self.api_entry = ctk.CTkEntry(
            self,
            width=self.FIELD_WIDTH,
            show="*"
        )

        self.api_entry.pack()

        # =====================================================
        # Modèle
        # =====================================================

        model_title = ctk.CTkLabel(
            self,
            text="📦 Modèle",
            font=("Segoe UI", 14, "bold")
        )
        model_title.pack(pady=(20, 5))

        self.model_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.model_frame.pack()

        self.model_combo = None
        self.model_entry = None

        self._build_model_widget(provider, value2)

        # =====================================================
        # Bouton
        # =====================================================

        self.save_button = ctk.CTkButton(
            self,
            text="💾 Enregistrer",
            width=180,
            command=self.save_settings,
        )

        self.save_button.pack(pady=(35, 20))

        # =====================================================
        # Dossier des projets
        # =====================================================

        projects_title = ctk.CTkLabel(
            self,
            text="📁 Dossier des projets",
            font=("Segoe UI", 14, "bold")
        )

        projects_title.pack(pady=(20, 5))

        projects_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        projects_frame.pack()

        self.projects_entry = ctk.CTkEntry(
            projects_frame,
            width=260
        )

        self.projects_entry.pack(
            side="left",
            padx=(0, 10)
        )

        self.projects_entry.insert(
            0,
            self.config_service.get("paths.projects") or ""
        )

        ctk.CTkButton(
            projects_frame,
            text="Parcourir...",
            width=110,
            command=self.browse_projects
        ).pack(side="left")

    def _build_model_widget(self, provider, current_value):

        if self.model_combo:
            self.model_combo.destroy()
            self.model_combo = None

        if self.model_entry:
            self.model_entry.destroy()
            self.model_entry = None

        if provider in PROVIDER_MODELS:

            models_list = PROVIDER_MODELS[provider]
            model_names = [name for name, _ in models_list]
            model_ids = [mid for _, mid in models_list]

            display_values = model_names + ["Autre (personnalisé)"]

            self.model_combo = ctk.CTkComboBox(
                self.model_frame,
                values=display_values,
                width=self.FIELD_WIDTH,
                command=self._on_model_combo_changed
            )
            self.model_combo.pack()

            self._provider_models_map = dict(models_list)
            self._provider_models_map["Autre (personnalisé)"] = ""

            if current_value in model_ids:
                idx = model_ids.index(current_value)
                self.model_combo.set(model_names[idx])
            elif current_value:
                self.model_combo.set("Autre (personnalisé)")
                self.model_entry = ctk.CTkEntry(
                    self.model_frame,
                    width=self.FIELD_WIDTH,
                    placeholder_text="provider/model-name"
                )
                self.model_entry.pack(pady=(5, 0))
                self.model_entry.insert(0, current_value)
            else:
                self.model_combo.set(model_names[0])

        else:

            self.model_entry = ctk.CTkEntry(
                self.model_frame,
                width=self.FIELD_WIDTH
            )
            self.model_entry.pack()
            if current_value:
                self.model_entry.insert(0, current_value)

    def _on_model_combo_changed(self, display_name):

        if display_name == "Autre (personnalisé)":

            if not self.model_entry:
                self.model_entry = ctk.CTkEntry(
                    self.model_frame,
                    width=self.FIELD_WIDTH,
                    placeholder_text="provider/model-name"
                )
                self.model_entry.pack(pady=(5, 0))

        else:

            if self.model_entry:
                self.model_entry.destroy()
                self.model_entry = None

    def _get_model_value(self):

        if self.model_combo:

            display = self.model_combo.get()

            if display == "Autre (personnalisé)":
                if self.model_entry:
                    return self.model_entry.get().strip()
                return ""

            return self._provider_models_map.get(display, display)

        if self.model_entry:
            return self.model_entry.get()

        return ""

    def save_settings(self):

        provider = self.provider_combo.get()

        self.config_service.set("ai.provider", provider)

        if provider in API_KEY_PROVIDERS:
            self.config_service.set(
                f"{provider}.api_key",
                self.api_entry.get()
            )
        else:
            self.config_service.set(
                f"{provider}.url",
                self.api_entry.get()
            )

        self.config_service.set(
            f"{provider}.model",
            self._get_model_value()
        )

        self.config_service.set(
            "paths.projects",
            self.projects_entry.get()
        )

        self.config_service.save()

        self.master.refresh_ai_status()

        self.destroy()

    def on_provider_changed(self, provider):

        if provider in API_KEY_PROVIDERS:
            value1 = self.config_service.get(f"{provider}.api_key")
            label = "🔑 Clé API"
            self.api_entry.configure(show="*")
        else:
            value1 = self.config_service.get(f"{provider}.url")
            label = "🌐 URL"
            self.api_entry.configure(show="")

        value2 = self.config_service.get(f"{provider}.model")

        self.api_title.configure(text=label)

        self.api_entry.delete(0, "end")
        self.api_entry.insert(0, value1 or "")

        self._build_model_widget(provider, value2)

    def browse_projects(self):

        folder = filedialog.askdirectory(parent=self)
        if folder:
            self.projects_entry.delete(0, "end")
            self.projects_entry.insert(0, folder)
