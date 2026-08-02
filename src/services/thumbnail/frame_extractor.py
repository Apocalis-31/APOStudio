import cv2
import json
import shutil
import subprocess

from services.path_service import PathService


class FrameExtractor:

    TARGET_FRAMES = 300
    IGNORE_END = 120  # secondes
    MIN_FRAMES = 20

    def __init__(self, ui):

        self.ui = ui

    def extract(self, project):

        transcript = project.working_path / "transcript.json"

        if not transcript.exists():

            self.ui.log(
                "⚠️ Transcription absente, extraction sur toute la vidéo."
            )

            return self.extract_full_video(project)

        with open(transcript, "r", encoding="utf-8") as f:
            data = json.load(f)

        segments = data["segments"]

        frames = project.working_path / "frames"
        frames.mkdir(exist_ok=True)

        # Nettoyage du dossier
        for file in frames.glob("*.png"):
            file.unlink()

        cap = cv2.VideoCapture(str(project.video_path))

        # Durée de la vidéo
        video_duration = self._video_duration(cap)

        # Intervalle automatique
        frame_interval = min(
            20,
            max(
                8,
                video_duration / self.TARGET_FRAMES
            )
        )

        ignore_end = self._ignore_end(video_duration)

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

            if timestamp > video_duration - ignore_end:
                continue

            cap.set(
                cv2.CAP_PROP_POS_MSEC,
                timestamp * 1000
            )

            success, frame = cap.read()

            if not success:
                continue

            timestamp_ms = int(timestamp * 1000)

            output = frames / f"frame_{timestamp_ms}ms.png"

            cv2.imwrite(str(output), frame)
            count += 1

        cap.release()

        self.ui.log(f"📸 {count} captures extraites")

        # Peu de segments dans le transcript (ou transcript court)
        # -> complète avec une extraction régulière sur toute la vidéo
        if count < self.MIN_FRAMES:

            self.ui.log(
                f"⚠️ Trop peu de captures ({count}), extraction sur toute la vidéo..."
            )

            count = self.extract_full_video(project)

            if count < self.MIN_FRAMES:

                self.ui.log(
                    f"⚠️ Extraction vidéo insuffisante ({count}), extraction FFmpeg..."
                )

                count = self.extract_full_video_ffmpeg(project)

        return count

    def extract_full_video(self, project):

        frames = project.working_path / "frames"
        frames.mkdir(exist_ok=True)

        # Nettoyage du dossier
        for file in frames.glob("*.png"):
            file.unlink()

        cap = cv2.VideoCapture(str(project.video_path))

        video_duration = self._video_duration(cap)

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
        end_limit = video_duration - self._ignore_end(video_duration)
        timestamp = 0.0

        while timestamp < end_limit and frame_interval > 0:

            cap.set(
                cv2.CAP_PROP_POS_MSEC,
                timestamp * 1000
            )

            success, frame = cap.read()

            if success:

                timestamp_ms = int(timestamp * 1000)

                output = frames / f"frame_{timestamp_ms}ms.png"

                cv2.imwrite(str(output), frame)
                count += 1

            timestamp += frame_interval

        cap.release()

        self.ui.log(f"📸 {count} captures extraites")

        return count

    def extract_full_video_ffmpeg(self, project):

        frames = project.working_path / "frames"
        frames.mkdir(exist_ok=True)

        # Nettoyage du dossier
        for file in frames.glob("*.png"):
            file.unlink()

        ffmpeg = PathService.ffmpeg() / "ffmpeg.exe"

        if not ffmpeg.exists():

            self.ui.log("⚠️ FFmpeg introuvable, extraction impossible.")

            return 0

        cap = cv2.VideoCapture(str(project.video_path))

        video_duration = self._video_duration(cap)

        cap.release()

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

        end_limit = max(0, video_duration - self._ignore_end(video_duration))

        temp = frames / "_ffmpeg"
        temp.mkdir(exist_ok=True)

        for file in temp.glob("*.png"):
            file.unlink()

        command = [
            str(ffmpeg),
            "-y",
            "-ss", "0",
            "-i", str(project.video_path),
            "-t", str(end_limit),
            "-vf", f"fps=1/{frame_interval}",
            "-qscale:v", "2",
            str(temp / "frame_%d.png"),
        ]

        self.ui.log(f"FFmpeg : {ffmpeg}")

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        try:

            subprocess.run(
                command,
                check=True,
                capture_output=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

        except subprocess.CalledProcessError:

            self.ui.log("❌ L'extraction FFmpeg a échoué.")

            shutil.rmtree(temp, ignore_errors=True)

            return 0

        count = 0

        for i, image in enumerate(
            sorted(temp.glob("*.png")),
            start=1
        ):

            timestamp_ms = int(
                (i - 1) * frame_interval * 1000
            )

            image.replace(
                frames / f"frame_{timestamp_ms}ms.png"
            )

            count += 1

        shutil.rmtree(temp, ignore_errors=True)

        self.ui.log(f"📸 {count} captures extraites")

        return count

    def _ignore_end(self, video_duration):

        if video_duration <= 0:

            return self.IGNORE_END

        # Ne retire jamais plus de 20 % de la vidéo
        return min(
            self.IGNORE_END,
            max(5, video_duration * 0.2)
        )

    def _video_duration(self, cap):

        fps = cap.get(cv2.CAP_PROP_FPS)

        if not fps:

            return 0

        return (
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
            / fps
        )
