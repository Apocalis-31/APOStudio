import cv2
import json


class FrameExtractor:

    TARGET_FRAMES = 300
    IGNORE_END = 120  # secondes

    

    def __init__(self, ui):

        self.ui = ui

    def extract(self, project):

        transcript = project.project_path / "transcript.json"

        if not transcript.exists():

            self.ui.log(
                "⚠️ Transcription absente, extraction sur toute la vidéo."
            )

            # Extraction classique
            return self.extract_full_video(project)

        with open(transcript, "r", encoding="utf-8") as f:
            data = json.load(f)

        segments = data["segments"]

        frames = project.project_path / "frames"
        frames.mkdir(exist_ok=True)

        # Nettoyage du dossier
        for file in frames.glob("*.png"):
            file.unlink()

        cap = cv2.VideoCapture(str(project.video_path))

        # Durée de la vidéo
        video_duration = (
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
            / cap.get(cv2.CAP_PROP_FPS)
        )

        # Intervalle automatique
        frame_interval = min(
            20,
            max(
                8,
                video_duration / self.TARGET_FRAMES
            )
        )

        self.ui.log(f"🎬 Durée : {video_duration/60:.1f} min")
        self.ui.log(f"🎯 Objectif : {self.TARGET_FRAMES} captures")
        self.ui.log(f"⏱ Intervalle : {frame_interval:.1f} sec")

        count = 0
        last_timestamp = -999

        for segment in segments:

            timestamp = (
                segment["start"] + segment["end"]
            ) / 2

            if timestamp - last_timestamp < frame_interval:
                continue

            last_timestamp = timestamp

            cap.set(
                cv2.CAP_PROP_POS_MSEC,
                timestamp * 1000
            )

            if timestamp > video_duration - self.IGNORE_END:
                continue

            success, frame = cap.read()

            if not success:
                continue

            timestamp_ms = int(timestamp * 1000)

            output = frames / f"frame_{timestamp_ms}ms.png"

            cv2.imwrite(str(output), frame)
            count += 1

        cap.release()

        self.ui.log(f"📸 {count} captures extraites")