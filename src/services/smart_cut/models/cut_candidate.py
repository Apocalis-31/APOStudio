from dataclasses import dataclass


@dataclass
class CutCandidate:

    timestamp: float

    score: float

    silence_duration: float

    reason: str

    before_text: str

    after_text: str