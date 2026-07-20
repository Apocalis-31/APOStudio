from pathlib import Path
import sys
import os


class PathService:

    # =====================================================
    # Racine de l'application
    # =====================================================

    @staticmethod
    def root() -> Path:
        """
        Racine des ressources de l'application.
        Compatible développement et PyInstaller.
        """

        if getattr(sys, "frozen", False):

            root = Path(sys.executable).parent

            internal = root / "_internal"

            if internal.exists():
                return internal

            return root

        return Path(__file__).resolve().parents[2]

    # =====================================================
    # Données utilisateur (AppData)
    # =====================================================

    @staticmethod
    def appdata() -> Path:

        path = Path(os.getenv("LOCALAPPDATA")) / "APO Studio"
        path.mkdir(parents=True, exist_ok=True)

        return path

    @staticmethod
    def config() -> Path:

        path = PathService.appdata() / "config"
        path.mkdir(parents=True, exist_ok=True)

        return path
    

    @staticmethod
    def user_prompts() -> Path:

        path = PathService.appdata() / "prompts"
        path.mkdir(
            parents=True,
            exist_ok=True
        )

        return path

    @staticmethod
    def projects() -> Path:

        from services.config_service import ConfigService

        config = ConfigService()

        custom_path = config.get("paths.projects")

        if custom_path:
            path = Path(custom_path)
        else:
            path = PathService.appdata() / "projects"

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        return path

    @staticmethod
    def logs() -> Path:

        path = PathService.appdata() / "logs"
        path.mkdir(parents=True, exist_ok=True)

        return path

    @staticmethod
    def cache() -> Path:

        path = PathService.appdata() / "cache"
        path.mkdir(parents=True, exist_ok=True)

        return path

    # =====================================================
    # Ressources de l'application
    # =====================================================

    @staticmethod
    def assets() -> Path:
        return PathService.root() / "assets"

    @staticmethod
    def ffmpeg() -> Path:
        return PathService.root() / "ffmpeg"

    @staticmethod
    def prompts() -> Path:

        if getattr(sys, "frozen", False):
            return PathService.root() / "prompts"

        return PathService.root() / "src" / "prompts"

    @staticmethod
    def knowledge() -> Path:

        if getattr(sys, "frozen", False):
            return PathService.root() / "knowledge"

        return PathService.root() / "src" / "knowledge"

    @staticmethod
    def docs() -> Path:

        return PathService.root() / "docs"