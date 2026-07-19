import shutil


class ThumbnailRenderer:

    def __init__(self, ui):

        self.ui = ui

    def render(self, project, frame):

        output = project.project_path / "thumbnail.png"

        shutil.copy(
            frame,
            output
        )

        self.ui.log("💾 thumbnail.png créé")