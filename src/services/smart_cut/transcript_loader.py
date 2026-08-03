import json

from services.smart_cut.models.transcript_segment import (
    TranscriptSegment
)


class TranscriptLoader:

    def load(
        self,
        project
    ) -> list[TranscriptSegment]:

        transcript = self._find_transcript(project)

        if transcript is None:

            raise FileNotFoundError(
                "Aucun transcript.json trouvé pour ce projet.\n\n"
                "Une transcription est nécessaire avant de pouvoir "
                "utiliser le découpage intelligent."
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

    # ==========================================

    def _find_transcript(self, project):

        candidates = []

        if project.project_path is not None:
            candidates.append(
                project.project_path / "transcript.json"
            )

        if project.working_path is not None:
            candidates.append(
                project.working_path / "transcript.json"
            )

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # Repli : recherche dans les dossiers "Episode N"
        if project.project_path is not None:

            for folder in sorted(
                project.project_path.glob("Episode *")
            ):

                candidate = folder / "transcript.json"

                if candidate.exists():
                    return candidate

        return None