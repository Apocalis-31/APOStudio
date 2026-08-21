from services.smart_cut.models.cut_candidate import CutCandidate
from services.smart_cut.models.episode_plan import EpisodePlan
from services.smart_cut.gap_selector import GapSelector
from services.smart_cut.smart_cut_ai_service import SmartCutAIService


class CutPlanner:

    def plan(
        self,
        candidates: list[CutCandidate],
        duration: float,
        settings
    ) -> list[EpisodePlan]:

        plans = []

        current_start = 0.0

        episode = settings.first_episode

        # -----------------------------------------
        # Durée cible
        # -----------------------------------------

        if settings.mode == "count":

            target_duration = (
                duration
                / settings.episode_count
            )

        else:

            target_duration = (
                settings.target_duration
                * 60
            )

        tolerance = settings.tolerance * 60

        # Copie de travail :
        # les candidats utilisés sont retirés au fur et à mesure.
        remaining_candidates = list(candidates)

        next_cut = target_duration

        # -----------------------------------------
        # Recherche des points de coupe
        # -----------------------------------------

        while next_cut < duration:

            # -------------------------------------
            # Candidats encore exploitables
            # -------------------------------------

            valid_candidates = [
                candidate
                for candidate in remaining_candidates
                if candidate.timestamp > current_start
                and (
                    candidate.timestamp
                    + candidate.silence_duration
                ) <= duration
            ]

            if not valid_candidates:
                break

            # -------------------------------------
            # Sélection du candidat
            # -------------------------------------

            if settings.use_ai:

                candidate = SmartCutAIService().select(
                    valid_candidates,
                    next_cut,
                    current_start
                )

            else:

                candidate = GapSelector().select(
                    valid_candidates,
                    next_cut,
                    tolerance,
                    current_start
                )

            if candidate is None:
                break

            # -------------------------------------
            # Calcul de la fin
            # -------------------------------------

            end = (
                candidate.timestamp
                + candidate.silence_duration
            )

            # -------------------------------------
            # Sécurité
            # -------------------------------------

            if end <= current_start:
                break

            if end > duration:
                end = duration

            # -------------------------------------
            # Création de l'épisode
            # -------------------------------------

            plans.append(

                EpisodePlan(

                    index=episode,

                    start=current_start,

                    end=end,

                    target=next_cut,

                    candidate=candidate

                )

            )

            # -------------------------------------
            # Candidat consommé
            # -------------------------------------

            remaining_candidates.remove(candidate)

            # Le prochain épisode commence après
            # le silence utilisé comme point de coupe.
            current_start = end

            episode += 1

            next_cut += target_duration

        # -----------------------------------------
        # Dernier épisode
        # -----------------------------------------

        if current_start < duration:

            plans.append(

                EpisodePlan(

                    index=episode,

                    start=current_start,

                    end=duration,

                    target=duration,

                    candidate=None

                )

            )

        return plans