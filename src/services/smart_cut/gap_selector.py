from services.smart_cut.models.cut_candidate import CutCandidate


class GapSelector:

    def select(
        self,
        candidates: list[CutCandidate],
        target: float,
        tolerance: float,
        after_timestamp: float
    ) -> CutCandidate | None:

        best = None
        best_distance = None

        for candidate in candidates:

            # Ignorer les gaps déjà utilisés
            if candidate.timestamp <= after_timestamp:
                continue

            distance = abs(
                candidate.timestamp - target
            )

            if distance > tolerance:
                continue

            if (
                best is None
                or distance < best_distance
            ):

                best = candidate
                best_distance = distance

        return best