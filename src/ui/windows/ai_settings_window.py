import customtkinter as ctk

from services.path_service import PathService


class AISettingsWindow(ctk.CTkToplevel):

    FILES = {
        "Profil": "creator.md",
        "Introduction": "intro.md",
        "Miniature": "thumbnail.md",
        "Hook": "hook.md",
    }

    def __init__(self, master):

        super().__init__(master)

        self.title("Préférences IA")
        self.geometry("950x760")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.attributes("-topmost", True)
        self.after(
            100,
            lambda: self.attributes("-topmost", False)
        )

        self.current_file = None

        self.build()

        # Charge le premier onglet
        first = list(self.FILES.keys())[0]
        self.segmented.set(first)
        self.change_category(first)

    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        title = ctk.CTkLabel(
            self,
            text="🤖 Préférences de l'IA",
            font=("Segoe UI", 24, "bold")
        )

        title.pack(
            pady=(20, 10)
        )

        description = ctk.CTkLabel(
            self,
            justify="left",
            wraplength=860,
            text=(
                "Personnalisez le comportement de l'IA.\n"
                "Les règles d'APO Studio sont conservées et vos préférences "
                "sont automatiquement ajoutées au prompt."
            )
        )

        description.pack(
            padx=25,
            pady=(0, 20)
        )

        # -------------------------------------------------

        self.segmented = ctk.CTkSegmentedButton(
            self,
            values=list(self.FILES.keys()),
            command=self.change_category
        )

        self.segmented.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        # -------------------------------------------------

        official_title = ctk.CTkLabel(
            self,
            text="📖 Règles d'APO Studio",
            font=("Segoe UI", 16, "bold")
        )

        official_title.pack(
            anchor="w",
            padx=25
        )

        official_desc = ctk.CTkLabel(
            self,
            text="Ces règles sont utilisées pour toutes les générations.",
            text_color="gray"
        )

        official_desc.pack(
            anchor="w",
            padx=25,
            pady=(0, 5)
        )

        self.official_box = ctk.CTkTextbox(
            self,
            height=180
        )

        self.official_box.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        self.official_box.configure(
            state="disabled"
        )

        # -------------------------------------------------

        user_title = ctk.CTkLabel(
            self,
            text="✏️ Personnalisation",
            font=("Segoe UI", 16, "bold")
        )

        user_title.pack(
            anchor="w",
            padx=25
        )

        user_desc = ctk.CTkLabel(
            self,
            text="Ces informations complètent les règles d'APO Studio.",
            text_color="gray"
        )

        user_desc.pack(
            anchor="w",
            padx=25,
            pady=(0, 5)
        )

        self.user_box = ctk.CTkTextbox(
            self
        )

        self.user_box.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

        # -------------------------------------------------

        self.save_button = ctk.CTkButton(
            self,
            text="💾 Enregistrer les préférences",
            width=250,
            command=self.save
        )

        self.save_button.pack(
            pady=(0, 20)
        )

    # =====================================================
    # CATEGORY
    # =====================================================

    def change_category(self, category):

        filename = self.FILES[category]

        self.current_file = filename

        self.load_official(filename)

        self.load_user(filename)

    # =====================================================
    # LOAD
    # =====================================================

    def load_official(self, filename):

        self.official_box.configure(
            state="normal"
        )

        self.official_box.delete(
            "1.0",
            "end"
        )

        path = (
            PathService.knowledge()
            / filename
        )

        if path.exists():

            self.official_box.insert(
                "1.0",
                path.read_text(
                    encoding="utf-8"
                )
            )

        self.official_box.configure(
            state="disabled"
        )

    def load_user(self, filename):

        self.user_box.delete(
            "1.0",
            "end"
        )

        path = (
            PathService.user_prompts()
            / filename
        )

        if path.exists():

            self.user_box.insert(
                "1.0",
                path.read_text(
                    encoding="utf-8"
                )
            )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        if self.current_file is None:
            return

        text = self.user_box.get(
            "1.0",
            "end"
        ).strip()

        (
            PathService.user_prompts()
            / self.current_file
        ).write_text(
            text,
            encoding="utf-8"
        )