import os
import tempfile

import requests


class UpdateInstallService:

    @staticmethod
    def install(update_info):

        installer_path = os.path.join(
            tempfile.gettempdir(),
            "APOStudio_Setup.exe"
        )

        print(installer_path)

        response = requests.get(
            update_info.download_url,
            stream=True
        )

        response.raise_for_status()

        with open(installer_path, "wb") as installer:

            for chunk in response.iter_content(chunk_size=8192):

                if chunk:

                    installer.write(chunk)

            if not os.path.exists(installer_path):
                raise RuntimeError("Le téléchargement de la mise à jour a échoué.")

            print("Téléchargement terminé !")

            return installer_path