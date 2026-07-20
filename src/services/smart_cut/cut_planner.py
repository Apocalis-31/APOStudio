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

        current_start = 0

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

        next_cut = target_duration

        tolerance = settings.tolerance * 60

        # -----------------------------------------
        # Recherche des points de coupe
        # -----------------------------------------

        while next_cut < duration:

            if settings.use_ai:

                candidate = SmartCutAIService().select(
                    candidates,
                    next_cut
                )

            else:


                candidate = GapSelector().select(
                    candidates,
                    next_cut,
                    tolerance,
                    current_start
                )


            if candidate is None:
                break

            plans.append(

                EpisodePlan(

                    index=episode,

                    start=current_start,

                    end=(
                        candidate.timestamp
                        + candidate.silence_duration
                    ),

                    target=next_cut,

                    candidate=candidate

                )

            )

            current_start = candidate.timestamp

            episode += 1

            next_cut += target_duration

        # -----------------------------------------
        # Dernier épisode
        # -----------------------------------------

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