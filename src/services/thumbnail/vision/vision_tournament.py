from services.thumbnail.vision.vision_service import VisionService


class VisionTournament:

    def __init__(self, ui):

        self.ui = ui
        self.vision = VisionService(ui)

    def select(self, project, images):

        current = images

        round_number = 1

        while len(current) > 1:

            self.ui.log(f"🏆 Tour {round_number}")

            size = self.group_size(len(current))

            self.ui.log(f"📦 Groupes de {size} images")

            groups = self.split_groups(
                current,
                size
            )

            winners = []

            for i, group in enumerate(groups):

                self.ui.log(
                    f"🥊 Match {i+1}/{len(groups)}"
                )

                winner = self.vision.select(
                    project,
                    group
                )

                winners.append(winner)

            current = winners

            round_number += 1

        return current[0]
    
    def split_groups(self, images, size=5):

        groups = []

        for i in range(0, len(images), size):

            groups.append(
                images[i:i + size]
            )

        return groups
    
    def group_size(self, count):

        if count > 500:
            return 10

        if count > 200:
            return 8

        return 5