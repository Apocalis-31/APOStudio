import json
import os
from pathlib import Path
from services.path_service import PathService

venv = PathService.ffmpeg() / ".venv"

cuda_runtime = (
    venv / "Lib/site-packages/nvidia/cuda_runtime/bin"
)

cuda_nvrtc = (
    venv / "Lib/site-packages/nvidia/cuda_nvrtc/bin"
)

if cuda_runtime.exists():
    os.add_dll_directory(str(cuda_runtime))

if cuda_nvrtc.exists():
    os.add_dll_directory(str(cuda_nvrtc))


from faster_whisper import WhisperModel
from models.project import Project
import time
from services.video.video_info import VideoInfo


class WhisperService:

    def __init__(self, ui):

        self.ui = ui

        self.ui.log("🎙️ Chargement du modèle Whisper...")

        self.ui.log("🔍 Détection du mode Whisper...")

        try:

            self.model = WhisperModel(
                "small",
                device="cuda",
                compute_type="float16"
            )

            self.ui.log("🚀 Whisper GPU (CUDA)")

        except Exception as e:

            self.ui.log(f"⚠️ CUDA indisponible : {e}")

            message = str(e).lower()

            if "model.bin" in message or "unable to open file" in message:

                cache = Path.home() / ".cache" / "huggingface"

                raise RuntimeError(
                    "Le modèle Whisper est incomplet ou corrompu.\n\n"
                    f"Supprimez le dossier :\n{cache}\n\n"
                    "Le modèle sera téléchargé automatiquement au prochain lancement."
                ) from e

            self.ui.log("💻 CUDA indisponible, utilisation du CPU...")

            self.model = WhisperModel(
                "small",
                device="cpu",
                compute_type="int8"
            )

    def transcribe(self, project: Project):



        start = time.perf_counter()

        video_info = VideoInfo()

        duration = video_info.get_duration(project.video_path)

        self.ui.log(f"🎬 Durée : {duration:.1f} secondes")

        self.ui.log("🎙️ Début de la transcription...")

        self.ui.log("📝 Transcription en cours...")

        segments, info = self.model.transcribe(
            str(project.video_path),
            language="fr"
        )

        segments = list(segments)

        txt_output = project.project_path / "transcript.txt"
        json_output = project.project_path / "transcript.json"

        with open(txt_output, "w", encoding="utf-8") as f:

            for segment in segments:
                f.write(segment.text + "\n")

        with open(json_output, "w", encoding="utf-8") as f:

            json.dump(
                {
                    "language": info.language,
                    "duration": duration,
                    "segments": [
                        {
                            "start": segment.start,
                            "end": segment.end,
                            "text": segment.text
                        }
                        for segment in segments
                    ]
                },
                f,
                indent=4,
                ensure_ascii=False
            )

        self.ui.log(f"🌍 Langue détectée : {info.language}")

        self.ui.log(f"🎯 Confiance : {info.language_probability:.2f}")

        self.ui.log("💾 Sauvegarde du transcript...")

        project.transcription_done = True
        
        self.ui.log(f"📄 Segments générés : {len(segments)}")

        self.ui.log("✅ Transcription terminée !")

        self.ui.log("💾 Transcript sauvegardé !")

        elapsed = time.perf_counter() - start

        self.ui.log(f"⏱ Temps : {elapsed:.1f} secondes")

