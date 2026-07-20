import customtkinter as ctk

from services.path_service import PathService


class AIStyleWindow(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Style de l'IA")
        self.geometry("850x700")
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

        self.build()

        self.load_user_prompt()

    def build(self):

        self.build_header()

        self.build_official_prompt()

        self.build_user_prompt()

        self.build_footer()

    def build_header(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="🎭 Style des introductions",
            font=("Segoe UI", 24, "bold")
        )

        self.title_label.pack(
            pady=(20, 10)
        )

        self.description = ctk.CTkLabel(
            self,
            text=(
                "Les instructions ci-dessous sont ajoutées automatiquement "
                "au prompt officiel d'APO Studio afin de personnaliser "
                "les introductions générées par l'IA."
            ),
            justify="left",
            wraplength=760
        )

        self.description.pack(
            padx=25,
            pady=(0,20)
        )

    def build_official_prompt(self):

        label = ctk.CTkLabel(
            self,
            text="Prompt officiel",
            font=("Segoe UI",16,"bold")
        )

        label.pack(
            anchor="w",
            padx=25
        )

        self.official_box = ctk.CTkTextbox(
            self,
            height=220
        )

        self.official_box.pack(
            fill="x",
            padx=25,
            pady=(5,20)
        )

        prompt = (
            PathService.knowledge()
            / "intro_style.md"
        ).read_text(
            encoding="utf-8"
        )

        self.official_box.insert(
            "1.0",
            prompt
        )

        self.official_box.configure(
            state="disabled"
        )

    def build_user_prompt(self):

        label = ctk.CTkLabel(
            self,
            text="Vos préférences",
            font=("Segoe UI",16,"bold")
        )

        label.pack(
            anchor="w",
            padx=25
        )

        self.user_box = ctk.CTkTextbox(
            self,
            height=180
        )

        self.user_box.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5,20)
        )

    def build_footer(self):

        self.save_button = ctk.CTkButton(
            self,
            text="💾 Enregistrer",
            command=self.save
        )

        self.save_button.pack(
            pady=(0,20)
        )

    def save(self):

        path = (
            PathService.user_prompts()
            / "intro_user.md"
        )

        text = self.user_box.get(
            "1.0",
            "end"
        ).strip()


        path.write_text(
            text,
            encoding="utf-8"
        )

    def load_user_prompt(self):

        path = (
            PathService.user_prompts()
            / "intro_user.md"
        )

        if not path.exists():
            return

        self.user_box.delete("1.0", "end")

        self.user_box.insert(
            "1.0",
            path.read_text(
                encoding="utf-8"
            )
        )