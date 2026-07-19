from threading import Thread
import subprocess

from services.update_install_service import UpdateInstallService


class UpdateDownloadWorker(Thread):

    def __init__(self, update_info, on_finished=None):
        super().__init__(daemon=True)

        self.update_info = update_info
        self.on_finished = on_finished

    def run(self):

        try:

            installer_path = UpdateInstallService.install(self.update_info)

            subprocess.Popen([installer_path])

            if self.on_finished:
                self.on_finished()

        except Exception as e:

            print(f"Erreur mise à jour : {e}")