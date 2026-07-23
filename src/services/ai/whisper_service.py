import json
import os
import sys
from pathlib import Path
from services.path_service import PathService

if getattr(sys, "frozen", False):
    _base = Path(sys.executable).parent / "_internal"
    cuda_dll_dirs = [
        _base / "nvidia/cublas/bin",
        _base / "nvidia/cudnn/bin",
        _base / "nvidia/cuda_runtime/bin",
        _base / "nvidia/cuda_nvrtc/bin",
    ]
else:
    _base = Path(__file__).resolve().parents[3] / ".venv" / "Lib/site-packages"
    cuda_dll_dirs = [
        _base / "nvidia/cuda_runtime/bin",
        _base / "nvidia/cuda_nvrtc/bin",
        _base / "nvidia/cublas/bin",
        _base / "nvidia/cudnn/bin",
    ]

for d in cuda_dll_dirs:
    if d.exists():
        os.add_dll_directory(str(d))
        os.environ["PATH"] = str(d) + os.pathsep + os.environ.get("PATH", "")


def _cuda_available() -> bool:
    for d in cuda_dll_dirs:
        if d.name == "bin" and d.exists():
            for dll in d.iterdir():
                if dll.name == "cublas64_12.dll":
                    return True
    return False


from faster_whisper import WhisperModel
from models.project import Project
import time
from services.video.video_info import VideoInfo


class WhisperService:

    def __init__(self, ui):

        self.ui = ui

        self.ui.log("Chargement du modele Whisper...")

        self.ui.log("Detection du mode Whisper...")

        if _cuda_available():

            self.ui.log("DLL CUDA detectees, tentative GPU...")

            try:

                self.model = WhisperModel(
                    "small",
                    device="cuda",
                    compute_type="float16"
                )

                self.ui.log("Whisper GPU (CUDA)")

            except Exception as e:

                self.ui.log(f"Erreur chargement GPU : {e}")

                message = str(e).lower()

                if "model.bin" in message or "unable to open file" in message:

                    cache = Path.home() / ".cache" / "huggingface"

                    raise RuntimeError(
                        "Le modele Whisper est incomplet ou corrompu.\n\n"
                        f"Supprimez le dossier :\n{cache}\n\n"
                        "Le modele sera telecharge automatiquement au prochain lancement."
                    ) from e

                self.ui.log("Bascule sur CPU...")
                self._load_cpu()

        else:

            self.ui.log("DLL CUDA manquantes, utilisation du CPU...")
            self._load_cpu()

    def _load_cpu(self):
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )
        self.ui.log("Whisper CPU (int8)")

    def transcribe(self, project: Project):



        start = time.perf_counter()

        video_info = VideoInfo()

        duration = video_info.get_duration(project.video_path)

        self.ui.log(f"Duree : {duration:.1f} secondes")

        self.ui.log("Debut de la transcription...")

        self.ui.log("Transcription en cours...")

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

        self.ui.log(f"Langue detectee : {info.language}")

        self.ui.log(f"Confiance : {info.language_probability:.2f}")

        self.ui.log("Sauvegarde du transcript...")

        project.transcription_done = True
        
        self.ui.log(f"Segments generes : {len(segments)}")

        self.ui.log("Transcription terminee !")

        self.ui.log("Transcript sauvegarde !")

        elapsed = time.perf_counter() - start

        self.ui.log(f"Temps : {elapsed:.1f} secondes")
