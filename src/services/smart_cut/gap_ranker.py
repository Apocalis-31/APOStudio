from services.smart_cut.models.cut_candidate import (
    CutCandidate
)


class GapRanker:

    def rank(
        self,
        candidates: list[CutCandidate],
        target: float,
        limit: int = 10
    ) -> list[CutCandidate]:

        ranked = sorted(

            candidates,

            key=lambda candidate: abs(
                candidate.timestamp - target
            )

        )

        return ranked[:limit]