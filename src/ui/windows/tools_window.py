import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
from services.smart_cut.video_resolver import VideoResolver
from ui.windows.smart_cut_window import SmartCutWindow
from workers.transcription_worker import TranscriptionWorker

class ToolsWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        ui
    ):

        super().__init__(master)

        self.home = master

        self.ui = ui

        self.title("Outils")

        self.geometry("550x400")

        self.resizable(False, False)

        self.build()

    # ======================================

    def build(self):

        self.build_header()

        self.build_tool_card(

            title="✂️ Découpage de VOD",

            description=(
                "Découpe intelligemment une VOD complète\n"
                "en plusieurs épisodes prêts à être montés."
            ),

            command=self.open_smart_cut

        )

        self.build_footer()

    # ======================================

    def build_header(self):

        ctk.CTkLabel(

            self,

            text="🧰 Outils",

            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )

        ).pack(
            pady=(20, 5)
        )

        ctk.CTkLabel(

            self,

            text="Outils complémentaires d'APO Studio"

        ).pack()

    # ======================================

    def build_footer(self):

        ctk.CTkLabel(

            self,

            text="🚧 D'autres outils arriveront bientôt."

        ).pack(
            side="bottom",
            pady=20
        )

    # ======================================

    def build_tool_card(
        self,
        title,
        description,
        command
    ):
        frame = ctk.CTkFrame(self)

        frame.pack(
            fill="x",
            padx=20,
            pady=20
        )

        ctk.CTkLabel(

        frame,

        text=title,

        font=ctk.CTkFont(
            size=18,
            weight="bold"
        )

        ).pack(
            anchor="w",
            padx=15,
            pady=(15,5)
        )

        ctk.CTkLabel(

            frame,

            text=description,

            justify="left"

        ).pack(
            anchor="w",
            padx=15
        )

        ctk.CTkButton(

            frame,

            text="Lancer",

            command=command

        ).pack(

            anchor="e",

            padx=15,

            pady=15
        )

    # ======================================

    def open_smart_cut(self):

        video = filedialog.askopenfilename(
            title="Choisir une VOD",
            filetypes=[
                ("Vidéo MP4", "*.mp4")
            ]
        )

        if not video:
            return

        project = VideoResolver(
            self.ui.ui_bridge
        ).resolve(video)

        if project:

            SmartCutWindow(
                self.home,
                project,
                self.ui
            )

        else:

            prepare = messagebox.askyesno(

                title="Préparer la VOD",

                message=(
                    "Cette VOD n'a jamais été préparée.\n\n"
                    "Une transcription est nécessaire avant "
                    "de pouvoir utiliser le découpage intelligent.\n\n"
                    "Voulez-vous préparer cette VOD ?"
                )

            )

            if not prepare:
                return

            self.ui.log("")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.ui.log("🎬 Préparation de la VOD")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            TranscriptionWorker(

                video,

                self.ui.ui_bridge,

                forced_modules=[
                    "transcription"
                ],

                on_finished=lambda: self.after(
                    0,
                    lambda: self.smart_cut_ready(video)
                )

            ).start()

    # ======================================
    
    def smart_cut_ready(
            self,
            video
        ):

            project = VideoResolver(
                self.ui.ui_bridge
            ).resolve(video)

            if project is None:

                self.ui.log(
                    "❌ Impossible de charger le projet."
                )

                return

            SmartCutWindow(
                self,
                project,
                self.ui
            )