from pathlib import Path


class FrameSelector:

    MIN_DISTANCE = 60  # secondes
    MAX_SELECTED = 30
    

    def __init__(self, ui):

        self.ui = ui

    def extract(self, project):

        frames = project.project_path / "frames_filtered"

        images = sorted(frames.glob("*.png"))

        self.ui.log(f"📂 FrameSelector : {frames}")

        self.ui.log(f"📸 {len(images)} captures reçues")

        if not images:

            raise Exception(
                "Aucune image disponible après filtrage."
            )

        
        selected = []

        last_timestamp = -999

        for image in images:

            timestamp = self.get_timestamp(image)

            if timestamp - last_timestamp < self.MIN_DISTANCE:
                continue

            selected.append(image)

            last_timestamp = timestamp

            if len(selected) == self.MAX_SELECTED:
                break

        self.ui.log(f"🖼️ {len(selected)} captures retenues")

        return selected    
    
    def get_timestamp(self, image):

        name = image.stem

        ms = int(
            name.replace("frame_", "")
                .replace("ms", "")
        )

        return ms / 1000