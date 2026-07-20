import customtkinter as ctk
from tkinter import filedialog
from services.config_service import ConfigService


class SettingsWindow(ctk.CTkToplevel):

    FIELD_WIDTH = 320

    def __init__(self, master):

        super().__init__(master)

        # Associer cette fenêtre à la fenêtre principale
        self.transient(master)

        # La placer immédiatement au premier plan
        self.lift()
        self.focus_force()

        # Fenêtre modale
        self.grab_set()

        # ------------------------
        # Configuration
        # ------------------------

        self.config_service = ConfigService()

        provider = self.config_service.get("ai.provider")

        if provider in ("openai", "claude", "glm"):

            value1 = self.config_service.get(f"{provider}.api_key")
            value2 = self.config_service.get(f"{provider}.model")

        else:

            value1 = self.config_service.get(f"{provider}.url")
            value2 = self.config_service.get(f"{provider}.model")


        # ------------------------
        # Fenêtre
        # ------------------------

        self.title("Paramètres")
        self.geometry("650x550")
        self.resizable(False, False)
        self.grab_set()

        # ------------------------
        # Titre
        # ------------------------

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
        # Clé API
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

        self.model_entry = ctk.CTkEntry(
            self,
            width=self.FIELD_WIDTH
        )

        self.model_entry.pack()



        # =====================================================
        # Bouton
        # =====================================================

        self.save_button = ctk.CTkButton(
            self,
            text="💾 Enregistrer",
            width=180,
            command=self.save_settings,
        )

        self.save_button.pack(
            pady=(35, 20)
        )

        self.provider_combo.set(provider)

        self.load_provider(provider)

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
  
  
    def save_settings(self):

        provider = self.provider_combo.get()

        self.config_service.set(
            "ai.provider",
            provider
        )

        if provider in ("openai", "claude", "glm"):

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
            self.model_entry.get()
        )

        print("Provider :", provider)
        print("API :", self.api_entry.get())
        print("Model :", self.model_entry.get())
        print(self.config_service.data)

        self.config_service.set(
            "paths.projects",
            self.projects_entry.get()
        )

        self.config_service.save()

        self.master.refresh_ai_status()
        
        self.destroy()

        
    def on_provider_changed(self, provider):

        self.load_provider(provider)



    def load_provider(self, provider):

        if provider in ("openai", "claude", "glm"):

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

        self.model_entry.delete(0, "end")
        self.model_entry.insert(0, value2 or "")

    def browse_projects(self):

        folder = filedialog.askdirectory(
            parent=self
        )
        if folder:

            self.projects_entry.delete(0, "end")
            self.projects_entry.insert(0, folder)