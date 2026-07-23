import customtkinter as ctk
from services.update_install_service import UpdateInstallService
from workers.update_download_worker import UpdateDownloadWorker


class UpdateBanner(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(parent, corner_radius=12)

        self.info = None

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text="🚀 Nouvelle version disponible",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        self.info_label = ctk.CTkLabel(
            self,
            text="",
            justify="left"
        )
        self.info_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))

        self.update_button = ctk.CTkButton(
            self,
            text="Mettre à jour",
            width=150,
            command=self.on_update
        )
        self.update_button.grid(row=0, column=1, rowspan=2, padx=20, pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self, width=150, height=8)
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11)
        )

    def on_update(self):

        if self.info is None:
            return

        try:

            root = self.winfo_toplevel()

            self.update_button.configure(state="disabled", text="Téléchargement…")
            self.progress_bar.grid(row=2, column=1, padx=20, pady=(0, 5))
            self.progress_label.grid(row=3, column=1, padx=20, pady=(0, 15))
            self.progress_bar.set(0)

            def on_progress(downloaded, total):
                pct = downloaded / total
                mb_done = downloaded / (1024 * 1024)
                mb_total = total / (1024 * 1024)
                root.after(0, lambda: self.progress_bar.set(pct))
                root.after(0, lambda: self.progress_label.configure(
                    text=f"{mb_done:.1f} / {mb_total:.1f} Mo"
                ))

            UpdateDownloadWorker(
                self.info,
                lambda: root.after(0, root.destroy),
                on_progress=on_progress
            ).start()

        except Exception as e:
            print(e)

    def set_update_info(self, info):

        self.update_button.configure(state="normal")

        self.info = info

        variant = "CPU (léger)" if info.is_gpu else "GPU (complet)"

        self.info_label.configure(
            text=(
                f"Version actuelle : {info.current_version}\n"
                f"Dernière version : {info.latest_version} — {variant}"
            )
        )
