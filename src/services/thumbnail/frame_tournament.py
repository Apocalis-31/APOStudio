from services.ai.glm_parser import GLMParser
from services.ai.glm_service import GLMService

class FrameTournament:

    GROUP_SIZE = 5
    MAX_GROUPS = 6

    def __init__(self, ui):

        self.ui = ui

    def split(self, images):

        groups = []

        for i in range(0, len(images), self.GROUP_SIZE):

            groups.append(
                images[i:i + self.GROUP_SIZE]
            )

        groups = groups[:self.MAX_GROUPS]

        self.ui.log("🏆 Tournoi IA")
        self.ui.log(f"📦 {len(groups)} groupes créés")

        return groups
    
    def run(
        self,
        prompt,
        images
    ):

        groups = self.split(images)

        winners = []

        glm = GLMService()

        for index, group in enumerate(groups, start=1):

            response = glm.ask_vision(
                prompt,
                group
            )

            ranking = response["ranking"]

            winner_index = (
                    GLMParser.parse_index(
                        ranking[0]
                    ) - 1
                )

            winner = group[winner_index]

            winners.append(winner)

            self.ui.log(
                f"🏆 Groupe {index} terminé"
            )

        self.ui.log("🥇 Finale...")

        final = glm.ask_vision(
            prompt,
            winners
        )

        self.ui.log("🥇 Finale terminée")

        return final, winners