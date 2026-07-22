import customtkinter as ctk
from pathlib import Path
from ui.home_page import HomePage
from services.path_service import PathService
from app_info import VERSION
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
    "ApoStudio.APOStudio"
)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ApoStudio(ctk.CTk):

    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 850

    def __init__(self):

        super().__init__()

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # ======================================
        # Scaling automatique
        # ======================================

        if screen_w >= 3840:
            scale = 1.10      # 4K
        elif screen_w >= 2560:
            scale = 1.00      # 2K
        else:
            scale = 0.90      # Full HD

        ctk.set_widget_scaling(scale)
        ctk.set_window_scaling(scale)

        print(f"Résolution : {screen_w}x{screen_h} | Scale : {scale}")

        # ======================================

        self.title(f"APO Studio {VERSION}")

        width = min(self.WINDOW_WIDTH, int(screen_w * 0.5))
        height = min(self.WINDOW_HEIGHT, int(screen_h * 0.5))

        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

        # Taille minimale raisonnable
        self.minsize(900, 700)

        self.resizable(True, True)

        self.configure(
            fg_color="#2b2b2b"
        )

        icon_path = (
            PathService.assets()
            / "branding"
            / "logo_transparence_AS.ico"
        )

        self.iconbitmap(icon_path)

        self.home = HomePage(self)

        self.home.pack(
            fill="both",
            expand=True
        )

