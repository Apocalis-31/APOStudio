from collections import deque
from workers.transcription_worker import TranscriptionWorker
from pathlib import Path
import time



class QueueManager:

    def __init__(self, ui):

        self.ui = ui
        self.queue = deque()
        self.running = False
        self.current_video = None
        self.current_video_start = None

    def add(self, video_path):

        self.queue.append(video_path)
        self.ui.video_added()
        self.update_ui()

        self.ui.log(
            f"➕ Ajout à la file ({len(self.queue)})"
        )

        if not self.running:

            self.ui.session_started()

            self.start_next()

 
    def start_next(self):

        self.running = True

        if not self.queue:

            self.running = False
            self.current_video = None

            self.update_ui()

            self.ui.session_finished()

            return

        video = self.queue.popleft()

        self.current_video = video

        self.current_video_start = time.time()

        self.update_ui()

        worker = TranscriptionWorker(
            video,
            ui=self.ui,
            on_finished=self.on_video_finished
        )

        worker.start()

    def update_ui(self):

        if self.current_video is not None:

            current = Path(self.current_video).stem

        else:

            current = "En attente..."

        self.ui.queue_update(
            current=current,
            waiting=[
                Path(v).stem
                for v in self.queue
            ]
        )

    def on_video_finished(self):

        duration = time.time() - self.current_video_start

        self.ui.video_finished(duration)

        self.start_next()