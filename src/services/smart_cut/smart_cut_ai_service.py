from services.ai.ai_factory import AIFactory
from services.ai.prompt_builder import PromptBuilder
from services.smart_cut.gap_selector import GapSelector


class SmartCutAIService:

    # ==================================================

    def select(
        self,
        candidates,
        target,
        after_timestamp
    ):

        from services.smart_cut.gap_ranker import (
            GapRanker
        )

        # ==========================================
        # Sécurité : uniquement les candidats
        # après le dernier point de coupe
        # ==========================================

        valid_candidates = [
            candidate
            for candidate in candidates
            if candidate.timestamp > after_timestamp
        ]

        if not valid_candidates:
            return None

        # ==========================================
        # Sélection des meilleurs candidats
        # ==========================================

        best_candidates = GapRanker().rank(
            valid_candidates,
            target
        )

        if not best_candidates:
            return None

        # ==========================================
        # Construction du prompt
        # ==========================================

        prompt = PromptBuilder().build_smart_cut(
            best_candidates,
            target
        )

        # ==========================================
        # Décision de l'IA
        # ==========================================

        try:

            ai = AIFactory.create()

            response = ai.ask_json(
                prompt.system,
                prompt.user
            )

            index = response["candidate"] - 1

            # Vérification de la réponse

            if (
                index < 0
                or index >= len(best_candidates)
            ):

                raise ValueError(
                    f"Candidat invalide : "
                    f"{response['candidate']}"
                )

            selected = best_candidates[index]

            print(
                f"🤖 IA -> candidat "
                f"{response['candidate']} "
                f"({selected.timestamp:.1f}s)"
            )

            print(
                f"💬 {response['reason']}"
            )

            return selected

        # ==========================================
        # Fallback
        # ==========================================

        except Exception as e:

            print(
                f"⚠️ SmartCut IA : {e}"
            )

            print(
                "➡️ Utilisation du GapSelector"
            )

            return GapSelector().select(
                valid_candidates,
                target,
                tolerance=300,
                after_timestamp=after_timestamp
            )