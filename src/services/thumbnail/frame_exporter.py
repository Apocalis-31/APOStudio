import shutil


class FrameExporter:

    def __init__(self, ui):

        self.ui = ui

    def export(self, project, frames):

        destination = project.working_path / "selected_frames"

        destination.mkdir(exist_ok=True)

        # Nettoyage
        for file in destination.glob("*.png"):
            file.unlink()

        for frame in frames:

            shutil.copy(
                frame,
                destination / frame.name
            )

        self.ui.log(
            f"📁 {len(frames)} frames exportées"
        )