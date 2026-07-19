import customtkinter as ctk
from services.update_install_service import UpdateInstallService
from workers.update_download_worker import UpdateDownloadWorker


class UpdateBanner(ctk.CTkFrame):
    
    def __init__(self, parent):

        super().__init__(parent, corner_radius=12)

        self.info = None

        self.grid_columnconfigure(0, weight=1)

        # Titre
        self.title_label = ctk.CTkLabel(
            self,
            text="🚀 Nouvelle version disponible",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        # Description
        self.info_label = ctk.CTkLabel(
            self,
            text="Vous utilisez la version 1.0.1\nLa version 1.0.2 est disponible.",
            justify="left"
        )
        self.info_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))

        # Bouton
        self.update_button = ctk.CTkButton(
            self,
            text="Mettre à jour",
            width=150,
            command=self.on_update
        )
        self.update_button.grid(row=0, column=1, rowspan=2, padx=20, pady=20)

    def on_update(self):

        if self.info is None:
            return

        try:

            root = self.winfo_toplevel()

            UpdateDownloadWorker(
                self.info,
                lambda: root.after(0, root.destroy)
            ).start()

        except Exception as e:
            print(e)

    def set_update_info(self, info):

        self.update_button.configure(state="normal")

        self.info = info

        self.info_label.configure(
            text=(
                f"Version actuelle : {info.current_version}\n"
                f"Dernière version : {info.latest_version}"
            )
        )