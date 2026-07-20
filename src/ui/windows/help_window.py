import customtkinter as ctk
from pathlib import Path
from services.path_service import PathService

class HelpWindow(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        # Associe la fenêtre à la fenêtre principale
        self.transient(master)

        # Empêche l'utilisateur d'interagir avec la fenêtre principale
        self.grab_set()

        # Place la fenêtre au premier plan
        self.lift()
        self.focus_force()

        self.title("Aide - APO Studio")
        self.geometry("1000x700")
        self.minsize(1000, 700)

        self.navigation_buttons = {}

        self.build()

    def build(self):

        title = ctk.CTkLabel(

            self,

            text="📖 Documentation APO Studio",

            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )

        )

        title.pack(
            pady=(20, 10)
        )

        body = ctk.CTkFrame(self)

        body.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.navigation_frame = ctk.CTkFrame(
            body,
            width=220
        )

        self.navigation_frame.pack(
            side="left",
            fill="y"
        )

        self.navigation_frame.pack_propagate(False)

        self.build_navigation()

        self.content_frame = ctk.CTkFrame(body)

        self.content_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        self.content = ctk.CTkTextbox(
            self.content_frame,
            wrap="word",
            font=("Segoe UI", 14)
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.content.configure(
            state="disabled"
        )

        self.load_page("index.md")

        # ==================================================

    def build_navigation(self):

        ctk.CTkLabel(

            self.navigation_frame,

            text="📚 Rubriques",

            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )

        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        pages = {

            "🏠 Guide de démarrage": "index.md",

            "📂 Gestion des projets": "project.md",

            "🎤 Transcription": "transcription.md",

            "🤖 Génération IA": "ai.md",

            "✂️ SmartCut": "smart_cut.md",

            "🖼️ Miniatures": "thumbnail.md",

            "⚙️ Paramètres": "settings.md"

        }

        for title, filename in pages.items():

            button = ctk.CTkButton(
                self.navigation_frame,
                text=title,
                fg_color="transparent",
                hover_color="#3a3a3a",
                anchor="w",
                width=190,
                height=34,
                command=lambda page=filename: self.load_page(page)
            )

            button.pack(
                fill="x",
                padx=10,
                pady=4
            )

            self.navigation_buttons[filename] = button

        # ==================================================


    def load_page(self, filename):

        path = (
            PathService.docs()
            / filename
        )

        if not path.exists():

            text = f"Impossible de trouver : {filename}"

        else:

            text = path.read_text(
                encoding="utf-8"
            )

        self.content.configure(
            state="normal"
        )

        self.content.delete(
            "1.0",
            "end"
        )

        self.content.insert(
            "1.0",
            text
        )

        self.content.configure(
            state="disabled"
        )

        for button in self.navigation_buttons.values():

            button.configure(
                fg_color="transparent"
            )

        self.navigation_buttons[filename].configure(
                fg_color=("#3B8ED0", "#1F6AA5")
            )
        
