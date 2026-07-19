import customtkinter as ctk
from tkinter import filedialog
from workers.transcription_worker import TranscriptionWorker
from ui.bridge.ui_bridge import UiBridge
from core.queue_manager import QueueManager
from ui.widgets.processing_status import ProcessingStatus
from ui.widgets.top_bar import TopBar
from ui.widgets.ai_status import AIStatus
from ui.windows.tools_window import ToolsWindow
from ui.widgets.session_status import SessionStatus
from core.session_statistics import SessionStatistics
from pathlib import Path
import os
from services.path_service import PathService
from ui.widgets.update_banner import UpdateBanner
from services.update_service import UpdateService

import time

class HomePage(ctk.CTkFrame):

    # ==================================================

    def __init__(self, master):

        super().__init__(master)

        # Services

        self.ui_bridge = UiBridge()

        self.queue_manager = QueueManager(
            ui=self.ui_bridge
        )

        self.statistics = SessionStatistics()

        # Construction de l'interface

        self.build()

        # Boucle UI

        self.after(
            100,
            self.process_queue
        )

    # ==================================================

    def build(self):

        self.build_layout()

        self.build_header()

        self.build_banner()

        self.build_dashboard()

        self.build_console()

        self.session_start = None

    # ==================================================

    def build_layout(self):

        # Fenêtre

        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.banner_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.dashboard_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.console_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.header_frame.pack(
            fill="x",
            padx=25,
            pady=(15, 10)
        )

        self.dashboard_frame.pack(
            fill="x",
            padx=25
        )

        self.console_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(15, 20)
        )

        # Dashboard

        self.actions_card = ctk.CTkFrame(
            self.dashboard_frame,
            corner_radius=12,
            border_width=1,
            border_color="#3c3c3c"
        )

        self.status_card = ctk.CTkFrame(
            self.dashboard_frame,
            corner_radius=12,
            border_width=1,
            border_color="#3c3c3c"
        )

        self.actions_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.status_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        self.console_card = ctk.CTkFrame(
            self.console_frame,
            corner_radius=12,
            border_width=1,
            border_color="#3c3c3c"
        )

        self.console_card.pack(
            fill="both",
            expand=True
        )

    # ==================================================

    def build_header(self):

        self.top_bar = TopBar(
            self.header_frame,
            home=self
        )

        self.top_bar.pack(
            anchor="e",
            padx=15,
            pady=(10, 0)
        )

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="APO Studio",
            font=("Segoe UI", 30, "bold")
        )

        self.title_label.pack(
            pady=(35, 10)
        )

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Assistant de création YouTube",
            font=("Segoe UI", 18)
        )

        self.subtitle_label.pack(
            pady=(0, 15)
        )

    # ==================================================

    def build_dashboard(self):

        # ==================================================
        # Carte Actions
        # ==================================================

        self.actions_title = ctk.CTkLabel(
            self.actions_card,
            text="🎬 Actions",
            font=("Segoe UI", 18, "bold")
        )

        self.new_project_button = ctk.CTkButton(
            self.actions_card,
            text="🎬 Nouveau Projet",
            height=45,
            fg_color="#8E1F45",
            hover_color="#6E1736",
            command=self.new_project
        )

        self.batch_button = ctk.CTkButton(
            self.actions_card,
            text="📚 Traitement par lot",
            fg_color="#8E1F45",
            hover_color="#6E1736",
            height=45,
            command=self.batch_project
        )

        self.separator = ctk.CTkFrame(
            self.actions_card,
            height=2
        )

        # ==================================================
        # IA
        # ==================================================

        self.ai_status = AIStatus(
            self.actions_card
        )

        self.separator_session = ctk.CTkFrame(
            self.actions_card,
            height=2
        )

        # ==================================================
        # Session
        # ==================================================

        self.session_status = SessionStatus(
            self.actions_card
        )

        # ==================================================
        # Carte Traitement
        # ==================================================

        self.status_title = ctk.CTkLabel(
            self.status_card,
            text="🎬 Traitement",
            font=("Segoe UI", 18, "bold")
        )

        self.current_video = ctk.CTkLabel(
            self.status_card,
            text="En attente...",
            font=("Segoe UI", 15)
        )

        self.processing_status = ProcessingStatus(
            self.status_card
        )

        self.separator2 = ctk.CTkFrame(
            self.status_card,
            height=2
        )

        self.queue_title = ctk.CTkLabel(
            self.status_card,
            text="📚 File d'attente",
            font=("Segoe UI", 16, "bold")
        )

        self.queue_progress = ctk.CTkLabel(
            self.status_card,
            text="En attente : 0 vidéo",
            font=("Segoe UI", 12)
        )

        self.queue_label = ctk.CTkLabel(
            self.status_card,
            text="Aucune vidéo",
            justify="left",
            font=("Segoe UI", 13)
        )

    # ==================================================

    def build_console(self):

        self.console_title = ctk.CTkLabel(
            self.console_card,

            text="🖥 Console",

            font=("Segoe UI", 18, "bold")

        )

        self.console_title.pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        self.log_box = ctk.CTkTextbox(
            self.console_card,

            font=("Consolas", 13)

        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.log_box.insert(

            "end",

            "🚀 APO Studio prêt.\n"

        )

        self.log_box.configure(
            state="disabled"
        )

        self.place_dashboard()

    # ==================================================

    def place_dashboard(self):

        # =====================================
        # Carte Actions
        # =====================================

        self.actions_title.pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        self.new_project_button.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )

        self.batch_button.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        self.separator.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        self.ai_status.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # =====================================
        # Carte Traitement
        # =====================================

        self.status_title.pack(
            anchor="w",
            padx=20,
            pady=(20, 15)
        )

        self.current_video.pack(
            anchor="w",
            padx=20,
            pady=(0, 25)
        )

        self.processing_status.pack(
            fill="x",
            padx=20,
            pady=(0, 25)
        )

        self.separator2.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        self.queue_title.pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        self.queue_progress.pack(
            anchor="w",
            padx=20
        )

        self.queue_label.pack(
            anchor="w",
            padx=20,
            pady=(5, 20)
        )

        self.separator_session.pack(
            fill="x",
            pady=20
        )

        self.session_status.pack(
            fill="x"
        )



    def batch_project(self):

        filenames = filedialog.askopenfilenames(
            title="Choisir les vidéos",
            filetypes=[
                ("Vidéos", "*.mp4 *.mkv *.mov"),
                ("Tous les fichiers", "*.*")
            ]
        )

        if not filenames:
            return

        self.log(f"📚 {len(filenames)} vidéo(s) sélectionnée(s)")

        for video in filenames:

            self.queue_manager.add(video)

    def set_progress(self, value):
        pass

    def new_project(self):

        self.set_progress(0)

        self.log("📂 Sélection d'une vidéo...")

        filename = filedialog.askopenfilename(

            title="Choisir une vidéo",

            filetypes=[
                ("Vidéos", "*.mp4 *.mkv *.mov"),
                ("Tous les fichiers", "*.*")
            ]

        )

        if filename:
            self.log("✅ Vidéo sélectionnée")
            self.log(filename)

            self.queue_manager.add(filename)

            if self.session_start is None:

                self.session_start = time.time()

                self.update_session_timer()


        

    def log(self, message):

        self.ui_bridge.log(message)

    def process_queue(self):

        while not self.ui_bridge.queue.empty():

            event, value = self.ui_bridge.queue.get()

            if event == "log":

                self.log_box.configure(state="normal")
                self.log_box.insert("end", value + "\n")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")

            elif event == "progress":

                pass

            elif event == "current_video":

                self.set_current_video(value)

            elif event == "queue_update":

                self.update_queue(value)

            elif event == "step":

                self.processing_status.set_step(value)

            elif event == "session_started":


                if self.session_start is None:

                    self.session_start = time.time()

                    self.update_session_timer()

            elif event == "session_finished":

                self.session_start = None

            elif event == "video_finished":

                self.statistics.finish_video()

                self.statistics.add_processing_time(value)

                self.refresh_session_statistics()

            elif event == "video_added":
                self.statistics.add_video()
                self.refresh_session_statistics()

        self.after(100, self.process_queue)

        

    def set_current_video(self, name):

        self.current_video.configure(
            text=name
        )
    
        
    def update_queue(self, data):

        self.current_video.configure(
            text=data["current"]
        )

        waiting = data["waiting"]

        if waiting:

            text = "\n".join(
                f"⏳ {video}"
                for video in waiting
            )

        else:

            text = "✅ Aucune vidéo en attente"

        self.queue_label.configure(
            text=text
        )

        count = len(waiting)

        self.queue_progress.configure(
            text=f"En attente : {count} vidéo(s)"
        )

    def open_projects_folder(self):

        projects = PathService.projects()

        projects.mkdir(exist_ok=True)

        os.startfile(projects.resolve())

    def refresh_ai_status(self):
        self.ai_status.refresh()


    def update_session_timer(self):


        if self.session_start is None:
            return


        self.after(1000, self.update_session_timer)

    def refresh_session_statistics(self):

        self.session_status.set_progress(
            self.statistics.finished_videos,
            self.statistics.total_videos
        )

        self.session_status.set_queue(
            self.statistics.waiting_videos
        )

        self.session_status.set_remaining(
            self.statistics.remaining_processing_time
        )

        self.session_status.set_end(
            self.statistics.estimated_end_time
        )

    def update_session_timer(self):

        if self.session_start is None:
            return

        elapsed = time.time() - self.session_start

        self.session_status.set_elapsed(
            elapsed
        )

        self.after(
            1000,
            self.update_session_timer
        )

    def build_banner(self):

        info = UpdateService.check()

        if not info.has_update:
            return

        self.banner_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 10),
            after=self.header_frame
        )

        self.update_banner = UpdateBanner(self.banner_frame)

        self.update_banner.set_update_info(info)

        self.update_banner.pack(fill="x")