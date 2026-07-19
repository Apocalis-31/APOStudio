import json

from services.smart_cut.models.transcript_segment import (
    TranscriptSegment
)


class TranscriptLoader:

    def load(
        self,
        project
    ) -> list[TranscriptSegment]:

        transcript = (
            project.project_path
            / "transcript.json"
        )

        with open(
            transcript,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        segments = []

        for segment in data["segments"]:

            segments.append(

                TranscriptSegment(

                    start=segment["start"],

                    end=segment["end"],

                    text=segment["text"]

                )

            )

        return segments