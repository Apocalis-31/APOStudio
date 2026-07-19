from dataclasses import dataclass

from services.smart_cut.models.cut_candidate import CutCandidate


@dataclass
class EpisodePlan:

    index: int
    start: float
    end: float
    target: float

    candidate: CutCandidate | None

    @property
    def duration(self):
        return self.end - self.start