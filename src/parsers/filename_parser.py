from pathlib import Path
import re


class FilenameParser:

    KEYWORDS = [
        "episode",
        "épisode",
        "part",
        "partie",
        "chapitre",
    ]

    def parse(self, video_path: str):

        filename = Path(video_path).stem
        filename_lower = filename.lower()

        for keyword in self.KEYWORDS:

            if keyword in filename_lower:

                index = filename_lower.index(keyword)

                series = filename[:index].strip()
                episode_text = filename[
                    index + len(keyword):
                ].strip()

                match = re.search(
                    r"\d+",
                    episode_text
                )

                if match:

                    episode = int(
                        match.group()
                    )

                else:

                    episode = None

                return {
                    "series": series,
                    "episode": episode
                }

        return {
            "series": filename,
            "episode": None
        }