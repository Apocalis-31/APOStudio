from threading import Thread

from services.update_install_service import UpdateInstallService


class UpdateDownloadWorker(Thread):

    def __init__(self, update_info):
        super().__init__(daemon=True)

        self.update_info = update_info

    def run(self):

        UpdateInstallService.install(self.update_info)