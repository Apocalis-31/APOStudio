import os
import sys
import tempfile
import subprocess

import requests


class UpdateInstallService:

    @staticmethod
    def _download(url, dest, on_progress=None):

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if on_progress and total > 0:
                        on_progress(downloaded, total)

        return dest

    @staticmethod
    def install(update_info, on_progress=None):

        installer_path = os.path.join(
            tempfile.gettempdir(), "APOStudio_Setup.exe"
        )

        if os.path.exists(installer_path):
            os.remove(installer_path)

        UpdateInstallService._download(
            update_info.download_url, installer_path, on_progress
        )

        return installer_path

    @staticmethod
    def install_patch(update_info, on_progress=None):

        zip_path = os.path.join(
            tempfile.gettempdir(), "APOStudio_Patch.zip"
        )

        if os.path.exists(zip_path):
            os.remove(zip_path)

        UpdateInstallService._download(
            update_info.download_url, zip_path, on_progress
        )

        if getattr(sys, "frozen", False):
            app_dir = os.path.dirname(sys.executable)
            exe_name = os.path.basename(sys.executable)
        else:
            app_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..")
            )
            exe_name = "APO Studio.exe"

        updater_path = os.path.join(app_dir, "APOStudio_Updater.exe")

        if not os.path.exists(updater_path):
            raise RuntimeError("L'updater n'a pas été trouvé.")

        subprocess.Popen(
            [updater_path, zip_path, app_dir, exe_name],
            creationflags=subprocess.DETACHED_PROCESS,
        )

        return True
