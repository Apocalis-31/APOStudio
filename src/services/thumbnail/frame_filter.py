from pathlib import Path
import shutil

from services.thumbnail.filters.dark_filter import DarkFilter
from services.thumbnail.filters.duplicate_filter import DuplicateFilter


class FrameFilter:

    def __init__(self, ui):

        self.ui = ui

        self.dark_filter = DarkFilter()
        self.duplicate_filter = DuplicateFilter()

    def filter(self, project):

        source = project.project_path / "frames"

        destination = project.project_path / "frames_filtered"

        destination.mkdir(exist_ok=True)

        # Nettoyage si le dossier existe déjà
        for file in destination.glob("*.png"):
            file.unlink()

        kept = 0
        dark_removed = 0
        duplicate_removed = 0

        last_kept = None

        images = sorted(source.glob("*.png"))

        for image in images:

            # -------- Dark Filter --------

            if not self.dark_filter.keep(image):

                dark_removed += 1
                continue

            # -------- Duplicate Filter --------

            if last_kept is not None:

                if not self.duplicate_filter.keep(
                    last_kept,
                    image
                ):

                    duplicate_removed += 1
                    continue


            shutil.copy(
                image,
                destination / image.name
            )

            last_kept = image

            kept += 1

        self.ui.log(f"🌑 {dark_removed} captures sombres supprimées")
        self.ui.log(f"🪞 {duplicate_removed} doublons supprimés")
        self.ui.log(f"🖼️ {kept} captures conservées")

