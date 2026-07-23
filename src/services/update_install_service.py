import os
import tempfile

import requests


class UpdateInstallService:

    @staticmethod
    def install(update_info, on_progress=None):

        installer_path = os.path.join(
            tempfile.gettempdir(),
            "APOStudio_Setup.exe"
        )

        if os.path.exists(installer_path):
            os.remove(installer_path)

        response = requests.get(
            update_info.download_url,
            stream=True
        )

        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(installer_path, "wb") as installer:

            for chunk in response.iter_content(chunk_size=8192):

                if chunk:
                    installer.write(chunk)
                    downloaded += len(chunk)

                    if on_progress and total > 0:
                        on_progress(downloaded, total)

            if not os.path.exists(installer_path):
                raise RuntimeError("Le téléchargement de la mise à jour a échoué.")

            return installer_path
