import requests

from app_info import VERSION, GITHUB_OWNER, GITHUB_REPOSITORY
from models.update_info import UpdateInfo


class UpdateService:

    @staticmethod
    def check() -> UpdateInfo:

        url = (
            f"https://api.github.com/repos/"
            f"{GITHUB_OWNER}/{GITHUB_REPOSITORY}/releases/latest"
        )

        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as e:
            raise RuntimeError(f"Impossible de contacter GitHub : {e}")

        print(response.status_code)

        if response.status_code == 404:

            return UpdateInfo(
                current_version=VERSION,
                latest_version=VERSION,
                has_update=False
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"GitHub a répondu avec le code {response.status_code}"
            )
        data = response.json()

        latest_version = data["tag_name"].lstrip("v")
        release_name = data["name"]
        release_notes = data["body"]

        if not data["assets"]:
            raise RuntimeError("La Release ne contient aucun installateur.")

        asset = data["assets"][0]
        download_url = asset["browser_download_url"]

        has_update = latest_version != VERSION

        return UpdateInfo(
            current_version=VERSION,
            latest_version=latest_version,
            has_update=has_update,
            release_name=release_name,
            download_url=download_url,
            release_notes=release_notes
        )