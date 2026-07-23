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
from ui.ui_scale import UI, px

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

        self.dashboard_center = ctk.CTkFrame(
            self.dashboard_frame,
            fg_color="transparent"
        )

        self.console_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.header_frame.pack(
            fill="x",
            padx=UI.PAD_WINDOW,
            pady=(15, 10)
        )

        self.dashboard_frame.pack(
            fill="x",
            padx=UI.PAD_WINDOW
        )

        self.dashboard_center.pack(
            anchor="center",
            fill="x"
        )

        self.console_frame.pack(
            fill="both",
            expand=True,
            padx=UI.PAD_WINDOW,
            pady=(15, 20)
        )

        # Dashboard

        self.actions_card = ctk.CTkFrame(
            self.dashboard_center,
            corner_radius=12,
            border_width=1,
            border_color="#3c3c3c"
        )

        self.status_card = ctk.CTkFrame(
            self.dashboard_center,
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
            font=("Segoe UI", UI.FONT_TITLE, "bold")
        )

        self.title_label.pack(
            pady=(20, 5)
        )

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Assistant de création YouTube",
            font=("Segoe UI", UI.FONT_SUBTITLE)
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
            font=("Segoe UI", UI.FONT_SECTION, "bold")
        )

        self.actions_row = ctk.CTkFrame(
            self.actions_card,
            fg_color="transparent"
        )

        self.new_project_button = ctk.CTkButton(
            self.actions_row,
            text="🎬 Nouveau Projet",
            height=UI.BUTTON_HEIGHT,
            fg_color="#8E1F45",
            hover_color="#6E1736",
            command=self.new_project
        )

        self.batch_button = ctk.CTkButton(
            self.actions_row,
            text="📚 Traitement par lot",
            fg_color="#8E1F45",
            hover_color="#6E1736",
            height=UI.BUTTON_HEIGHT,
            command=self.batch_project
        )

        self.stop_row = ctk.CTkFrame(
            self.actions_card,
            fg_color="transparent"
        )

        self.stop_button = ctk.CTkButton(
            self.stop_row,
            text="⏹ Stop",
            fg_color="#8E1F45",
            hover_color="#6E1736",
            height=UI.BUTTON_HEIGHT,
            command=self.stop_processing,
            state="disabled"
        )

        self.restart_button = ctk.CTkButton(
            self.stop_row,
            text="🔄 Relancer",
            fg_color="#8E1F45",
            hover_color="#6E1736",
            height=UI.BUTTON_HEIGHT,
            command=self.restart_processing
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
            font=("Segoe UI", UI.FONT_SECTION, "bold")
        )

        self.current_video = ctk.CTkLabel(
            self.status_card,
            text="En attente...",
            font=("Segoe UI", UI.FONT_TEXT)
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
            font=("Segoe UI", UI.FONT_SMALL)
        )

    # ==================================================

    def build_console(self):

        self.console_header = ctk.CTkFrame(
            self.console_card,
            fg_color="transparent"
        )

        self.console_header.pack(
            fill="x",
            padx=UI.PAD,
            pady=(20, 10)
        )

        self.console_title = ctk.CTkLabel(
            self.console_header,

            text="🖥 Console",

            font=("Segoe UI", UI.FONT_SECTION, "bold")

        )

        self.console_title.pack(
            side="left"
        )

        self._auto_scroll = True

        self.scroll_btn = ctk.CTkButton(
            self.console_header,
            text="⬇",
            width=UI.BUTTON_HEIGHT,
            height=UI.BUTTON_HEIGHT,
            font=("Segoe UI", 16),
            fg_color="#8E1F45",
            hover_color="#6E1736",
            corner_radius=10,
            command=self._scroll_to_bottom
        )

        self.log_box = ctk.CTkTextbox(
            self.console_card,

            font=("Consolas", 13)

        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=UI.PAD,
            pady=(0, 20)
        )

        self.log_box.insert(

            "end",

            "🚀 APO Studio prêt.\n"

        )

        self.log_box.configure(
            state="disabled"
        )

        self._bind_scroll_events()

        self.place_dashboard()

    # ==================================================
    # Scroll management
    # ==================================================

    def _bind_scroll_events(self):

        widget = self.log_box._textbox

        widget.bind("<MouseWheel>", self._on_scroll, add="+")
        widget.bind("<Button-4>", self._on_scroll, add="+")
        widget.bind("<Button-5>", self._on_scroll, add="+")

        self.log_box._y_scrollbar.configure(
            command=self._on_scrollbar
        )

    def _on_scroll(self, event):

        self.after(50, self._check_at_bottom)

    def _on_scrollbar(self, *args):

        self.log_box._textbox.yview(*args)
        self.after(50, self._check_at_bottom)

    def _check_at_bottom(self):

        view = self.log_box._textbox.yview()

        at_bottom = view[1] >= 0.999

        if at_bottom and not self._auto_scroll:
            self._auto_scroll = True
            self.scroll_btn.pack_forget()
        elif not at_bottom and self._auto_scroll:
            self._auto_scroll = False
            self.scroll_btn.pack(
                side="right",
                padx=(10, 0)
            )

    def _scroll_to_bottom(self):

        self._auto_scroll = True
        self.scroll_btn.pack_forget()
        self.log_box.configure(state="normal")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ==================================================

    def place_dashboard(self):

        # =====================================
        # Carte Actions
        # =====================================

        self.actions_title.pack(
            side="top",
            anchor="w",
            padx=UI.PAD,
            pady=(20, 15),
            expand=False
        )

        self.actions_row.pack(
            side="top",
            fill="x",
            padx=UI.PAD,
            pady=(0, 10),
            expand=False
        )

        self.new_project_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )

        self.batch_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 0)
        )

        self.stop_row.pack(
            side="top",
            fill="x",
            padx=UI.PAD,
            pady=(0, 10),
            expand=False
        )

        self.stop_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )

        self.separator.pack(
            side="top",
            fill="x",
            padx=UI.PAD,
            pady=(0, 20),
            expand=False
        )

        self.ai_status.pack(
            side="top",
            fill="x",
            padx=UI.PAD,
            pady=(0, 20),
            expand=False
        )

        self.separator_session.pack(
            side="top",
            fill="x",
            pady=UI.PAD,
            expand=False
        )

        self.session_status.pack(
            side="top",
            fill="x",
            expand=False
        )

        # =====================================
        # Carte Traitement
        # =====================================

        self.status_title.pack(
            side="top",
            anchor="w",
            padx=UI.PAD,
            pady=(20, 15)
        )

        self.current_video.pack(
            side="top",
            anchor="w",
            padx=UI.PAD,
            pady=(0, 25)
        )

        self.processing_status.pack(
            side="top",
            fill="x",
            padx=UI.PAD,
            pady=(0, 25)
        )

        self.separator2.pack(
            side="top",
            fill="x",
            padx=UI.PAD,
            pady=(0, 20)
        )

        self.queue_title.pack(
            side="top",
            anchor="w",
            padx=UI.PAD,
            pady=(0, 10)
        )

        self.queue_progress.pack(
            side="top",
            anchor="w",
            padx=UI.PAD
        )

        self.queue_label.pack(
            side="top",
            anchor="w",
            padx=UI.PAD,
            pady=(5, 20)
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

    def stop_processing(self):

        self.queue_manager.stop()

    def restart_processing(self):

        self.queue_manager.restart()

    def process_queue(self):

        while not self.ui_bridge.queue.empty():

            event, value = self.ui_bridge.queue.get()

            if event == "log":

                self.log_box.configure(state="normal")
                self.log_box.insert("end", value + "\n")

                if self._auto_scroll:
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

                self.stop_button.configure(state="normal")

                if self.session_start is None:

                    self.session_start = time.time()

                    self.update_session_timer()

            elif event == "session_finished":

                self.stop_button.configure(state="disabled")

                self.session_start = None

            elif event == "video_finished":

                self.statistics.finish_video()

                self.statistics.add_processing_time(value)

                self.refresh_session_statistics()

            elif event == "video_added":
                self.statistics.add_video()
                self.refresh_session_statistics()

            elif event == "queue_update_buttons":
                if value:
                    self.restart_button.pack(
                        side="left",
                        fill="x",
                        expand=True,
                        padx=(5, 0)
                    )
                else:
                    self.restart_button.pack_forget()

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
            self.restart_button.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(5, 0)
            )
        else:
            text = "✅ Aucune vidéo en attente"
            self.restart_button.pack_forget()

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
            padx=UI.PAD_WINDOW,
            pady=(0, 10),
            after=self.header_frame
        )

        self.update_banner = UpdateBanner(self.banner_frame)

        self.update_banner.set_update_info(info)

        self.update_banner.pack(fill="x")