from services.smart_cut.models.cut_candidate import (
    CutCandidate
)

from services.smart_cut.models.transcript_segment import (
    TranscriptSegment
)
from services.smart_cut.models.cut_candidate import CutCandidate

class GapFinder:

    def find(
        self,
        segments: list[TranscriptSegment]
    ) -> list[CutCandidate]:

        candidates = []

        MIN_GAP = 4

        for current, nxt in zip(
            segments,
            segments[1:]
        ):

            gap = nxt.start - current.end

            if gap < MIN_GAP:
                continue

            candidates.append(

                CutCandidate(

                    timestamp=current.end,

                    silence_duration=gap,

                    score=gap,

                    reason="Gap détecté",

                    before_text=current.text,

                    after_text=nxt.text


                )

            )

        return candidates