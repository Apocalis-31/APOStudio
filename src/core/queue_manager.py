from collections import deque
from workers.transcription_worker import TranscriptionWorker
from pathlib import Path
import threading
import time


class VideoEntry:

    def __init__(self, path):

        self.path = path
        self.name = Path(path).stem
        self.status = "pending"
        self.start_time = None
        self.end_time = None
        self.duration = None

    def start(self):

        self.status = "processing"
        self.start_time = time.time()

    def finish(self):

        self.status = "done"
        self.end_time = time.time()

        if self.start_time:
            self.duration = self.end_time - self.start_time

    def fail(self):

        self.status = "error"
        self.end_time = time.time()

        if self.start_time:
            self.duration = self.end_time - self.start_time

    def elapsed(self):

        if self.start_time is None:
            return 0

        if self.end_time:
            return self.duration or 0

        return time.time() - self.start_time

    def to_dict(self):

        return {
            "name": self.name,
            "path": self.path,
            "status": self.status,
            "elapsed": self.elapsed(),
            "duration": self.duration
        }


class QueueManager:

    def __init__(self, ui):

        self.ui = ui
        self.queue = deque()
        self.running = False
        self.current_video = None
        self.current_entry = None
        self.current_worker = None
        self.cancel_event = threading.Event()
        self.failed_videos = []
        self.entries = []
        self.total_added = 0
        self.total_done = 0

    def add(self, video_path):

        entry = VideoEntry(video_path)

        self.entries.append(entry)

        self.queue.append(entry)

        self.total_added += 1

        self.ui.video_added()

        self.update_ui()

        self.ui.log(
            f"➕ Ajout à la file ({len(self.queue)})"
        )

        if not self.running:

            self.failed_videos.clear()

            self.ui.session_started()

            self.start_next()

    def start_next(self):

        self.running = True

        if not self.queue:

            self.running = False
            self.current_video = None
            self.current_entry = None

            self.update_ui()
            self.ui.queue_update_buttons(
                has_pending=len(self.failed_videos) > 0
            )

            self.ui.session_finished()

            return

        entry = self.queue.popleft()

        entry.start()

        self.current_video = entry.path

        self.current_entry = entry

        self.update_ui()

        self.current_worker = TranscriptionWorker(
            entry.path,
            ui=self.ui,
            cancel_event=self.cancel_event,
            on_finished=self.on_video_finished
        )

        self.current_worker.start()

    def update_ui(self):

        if self.current_entry is not None:

            current = self.current_entry.name

        else:

            current = "En attente..."

        self.ui.queue_update(
            current=current,
            waiting=[
                e.name
                for e in self.queue
            ]
        )

    def on_video_finished(self, cancelled=False):

        self.current_worker = None
        self.cancel_event.clear()

        if self.current_entry:

            if cancelled:
                self.current_entry.fail()
                self.failed_videos.append(self.current_entry.path)
            else:
                self.current_entry.finish()
                self.total_done += 1
                duration = self.current_entry.duration or 0
                self.ui.video_finished(duration)

        self.start_next()

    def stop(self):

        if not self.running:
            return

        self.cancel_event.set()

        if self.current_entry:
            self.current_entry.fail()
            self.failed_videos.append(self.current_entry.path)

        for entry in self.queue:
            entry.fail()
            self.failed_videos.append(entry.path)

        self.queue.clear()

        self.ui.log("⏹ Arrêt du traitement...")
        self.ui.log(
            f"🔄 {len(self.failed_videos)} vidéo(s) en attente de relance"
        )

        self.update_ui()

    def restart(self):

        if not self.failed_videos:
            return

        self.ui.log(f"🔄 Relance de {len(self.failed_videos)} vidéo(s)...")

        for path in self.failed_videos:
            entry = VideoEntry(path)
            self.entries.append(entry)
            self.queue.append(entry)

        self.total_added += len(self.failed_videos)

        self.failed_videos.clear()

        self.ui.session_started()

        if not self.running:
            self.start_next()

    def clear_waiting(self):

        if not self.running:
            return

        self.queue.clear()

        self.ui.log("🗑️ File vidée, traitement en cours conservé")

        self.update_ui()
