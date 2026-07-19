import customtkinter as ctk

from models.cut_settings import CutSettings
from services.smart_cut.smart_cut_service import SmartCutService
import json
import subprocess
from pathlib import Path
import math
import threading
from services.path_service import PathService

class SmartCutWindow(ctk.CTkToplevel):

    def __init__(
        self,
        master,
        project,
        ui
    ):

        super().__init__(master)

        self.project = project
        self.ui = ui

        self.title("Découpage intelligent")
        self.geometry("650x750")

        # ======================================
        # Variables
        # ======================================

        self.mode = ctk.StringVar(value="duration")

        self.target_duration = ctk.StringVar(value="60")

        self.target_duration.trace_add(
            "write",
            lambda *_: self.refresh_ui()
        )

        self.tolerance = ctk.StringVar(value="15")

        self.episode_count = ctk.StringVar(value="6")

        self.episode_count.trace_add(
            "write",
            lambda *_: self.refresh_ui()
        )

        self.series_name = ctk.StringVar(
            value=self.project.series
        )

        episode = self.project.episode or 0

        if self.project.episode is None:

            first_episode = 1

        else:

            first_episode = self.project.episode + 1

        self.first_episode = ctk.StringVar(
            value=str(first_episode)
        )

        self.rename = ctk.BooleanVar(value=True)

        self.use_ai = ctk.BooleanVar(value=True)

        self.video_duration = self.get_video_duration()

        self.overlap_seconds = ctk.StringVar(value="5")


        self.build()


    # ==================================================

    def build(self):

        self.build_info()

        self.build_mode()

        self.build_duration()

        self.build_episode_count()

        self.build_options()

        self.build_buttons()

    # ==================================================

    def build_info(self):

        frame = ctk.CTkFrame(self)

        frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            frame,
            text="🎬 Informations de la vidéo",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        ).pack(anchor="w", padx=10, pady=(8, 5))

        self.duration_label = ctk.CTkLabel(
            frame,
            text=(
                "Durée de la vidéo : "
                f"{self.format_duration(self.video_duration)}"
            )
        )

        self.duration_label.pack(anchor="w", padx=10)

        self.estimation_label = ctk.CTkLabel(
            frame,
            text=(
            "Découpage estimé : "
            f"{self.get_estimation()}"
            )
        )

        self.estimation_label.pack(
            anchor="w",
            padx=10,
            pady=(0, 8)
        )

# ==================================================

    def format_duration(self, seconds: float) -> str:

        seconds = int(round(seconds))

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        parts = []

        if hours:
            parts.append(f"{hours} h")

        if minutes:
            parts.append(f"{minutes} min")

        if seconds:
            parts.append(f"{seconds} s")

        if not parts:
            return "0 s"

        return " ".join(parts)

# ==================================================

    def get_estimation(self):

        try:

            if self.mode.get() == "count":

                episode_count = max(
                    1,
                    int(self.episode_count.get())
                )

                duration = (
                    self.video_duration
                    / episode_count
                )

                return (
                    f"{episode_count} épisode(s) "
                    f"d'environ {self.format_duration(duration)}"
                )

            target = max(
                60,
                int(self.target_duration.get()) * 60
            )

            episode_count = math.ceil(
                self.video_duration / target
            )

            return (
                f"≈ {episode_count} épisode(s)"
            )

        except ValueError:

            return "..."

# ==================================================

    def build_mode(self):

        frame = ctk.CTkFrame(self)

        frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            frame,
            text="Mode"
        ).pack(anchor="w")

        ctk.CTkRadioButton(
            frame,
            text="Durée cible",
            variable=self.mode,
            value="duration",
            command=self.refresh_mode
        ).pack(anchor="w")

        ctk.CTkRadioButton(
            frame,
            text="Nombre de vidéos",
            variable=self.mode,
            value="count",
            command=self.refresh_mode
        ).pack(anchor="w")

    # ==================================================

    def build_duration(self):

        frame = ctk.CTkFrame(self)

        frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            frame,
            text="Durée cible (minutes)"
        ).pack(anchor="w")

        ctk.CTkEntry(
            frame,
            textvariable=self.target_duration
        ).pack(
            fill="x",
            padx=5,
            pady=(0,10)
        )

        ctk.CTkLabel(
            frame,
            text="Tolérance (minutes)"
        ).pack(anchor="w")

        ctk.CTkEntry(
            frame,
            textvariable=self.tolerance
        ).pack(
            fill="x",
            padx=5
        )

        ctk.CTkLabel(
            frame,
            text="Chevauchement (secondes)"
        ).pack(anchor="w")

        ctk.CTkEntry(
            frame,
            textvariable=self.overlap_seconds
        ).pack(
            fill="x",
            padx=5
        )

    # ==================================================

    def build_episode_count(self):

        frame = ctk.CTkFrame(self)

        frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            frame,
            text="Nombre de vidéos"
        ).pack(anchor="w")

        ctk.CTkEntry(
            frame,
            textvariable=self.episode_count
        ).pack(
            fill="x",
            padx=5
        )

    # ==================================================

    def build_options(self):

        frame = ctk.CTkFrame(self)

        frame.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            frame,
            text="Nom de la série"
        ).pack(anchor="w")

        ctk.CTkEntry(
            frame,
            textvariable=self.series_name
        ).pack(
            fill="x",
            padx=5,
            pady=(0,10)
        )

        ctk.CTkLabel(
            frame,
            text="Premier épisode"
        ).pack(anchor="w")

        ctk.CTkEntry(
            frame,
            textvariable=self.first_episode
        ).pack(
            fill="x",
            padx=5,
            pady=(0,10)
        )

        ctk.CTkCheckBox(
            frame,
            text="Renommer automatiquement",
            variable=self.rename
        ).pack(anchor="w")

        ctk.CTkCheckBox(
            frame,
            text="Utiliser l'IA",
            variable=self.use_ai
        ).pack(anchor="w")

    # ==================================================

    def build_buttons(self):

        ctk.CTkButton(

            self,

            text="✂️ Découpage intelligent",

            command=self.start

        ).pack(
            pady=20
        )

    # ==================================================

    def refresh_mode(self):

        self.refresh_ui()

    # ==================================================

    def start(self):

        settings = CutSettings(

            mode=self.mode.get(),

            target_duration=int(
                self.target_duration.get()
            ),

            tolerance=int(
                self.tolerance.get()
            ),

            episode_count=int(
                self.episode_count.get()
            ),

            rename=self.rename.get(),

            series_name=self.series_name.get(),

            first_episode=int(
                self.first_episode.get()
            ),

            use_ai=self.use_ai.get(),

            overlap_seconds=int(
                self.overlap_seconds.get()
            ),

        )

        threading.Thread(

            target=SmartCutService(
                self.ui
            ).generate,

            args=(
                self.project,
                settings
            ),

            daemon=True

        ).start()

    # ==================================================

    def get_video_duration(self) -> float:

        ffprobe = (
            PathService.ffmpeg()
            / "ffprobe.exe"
        )

        command = [
            str(ffprobe),
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(self.project.video_path)
        ]

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

        except subprocess.CalledProcessError as e:

            print("===== FFPROBE ERROR =====")
            print("COMMAND :", command)
            print("STDOUT :", e.stdout)
            print("STDERR :", e.stderr)
            print("=========================")
            raise

        data = json.loads(result.stdout)

        return float(data["format"]["duration"])
    # ==================================================

    def refresh_ui(self):
        self.estimation_label.configure(
        text=(
            "Découpage estimé : "
            f"{self.get_estimation()}"
        )
    )