from threading import Thread
import subprocess

from services.update_install_service import UpdateInstallService


class UpdateDownloadWorker(Thread):

    def __init__(self, update_info, on_finished=None, on_progress=None):
        super().__init__(daemon=True)

        self.update_info = update_info
        self.on_finished = on_finished
        self.on_progress = on_progress

    def run(self):

        try:

            installer_path = UpdateInstallService.install(
                self.update_info,
                on_progress=self.on_progress
            )

            subprocess.Popen([installer_path])

            if self.on_finished:
                self.on_finished()

        except Exception as e:

            print(f"Erreur mise à jour : {e}")
