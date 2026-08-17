from PySide6.QtCore import QObject, Signal, QThread

from assisted_editing.models.editing_queue_item import (
    EditingQueueItem,
)
from assisted_editing.services.editing_queue import EditingQueue
from assisted_editing.workers.assisted_editing_worker import (
    AssistedEditingWorker,
)
import time


class AssistedEditingManager(QObject):
    """
    Gestionnaire global des montages assistés.

    Le traitement ne dépend pas d'une fenêtre.
    """

    # ==================================================
    # Signaux
    # ==================================================

    episode_started = Signal(object)
    episode_finished = Signal(object, bool)

    queue_changed = Signal(int)
    processing_changed = Signal(bool)

    all_finished = Signal()

    # ==================================================

    def __init__(
        self,
        ui,
        parent=None,
    ):
        super().__init__(parent)

        self.ui = ui

        self.queue = EditingQueue()

        self.processing = False

        self.worker = None
        self.worker_thread = None

        self.current_item = None
        self.last_success = False

        self.current_started_at = None
        self.completed_durations = []

    # ==================================================
    # Ajout dans la queue
    # ==================================================

    def enqueue(
        self,
        item: EditingQueueItem,
    ):

        self.queue.add(item)

        print(
            "==================================="
        )

        print(
            f"Queue : "
            f"{self.queue.count()} élément(s)"
        )

        for job in self.queue.items():

            print(
                job.episode.project_name
            )

            print(
                job.episode.episode_number
            )

            print(
                job.intro_path
            )

            print(
                job.logo_path
            )

        print(
            "==================================="
        )

        self.queue_changed.emit(
            self.queue.count()
        )

        if not self.processing:

            self._start_next()

    # ==================================================
    # Démarrage épisode suivant
    # ==================================================

    def _start_next(self):

        if self.processing:
            return

        item = self.queue.pop()

        if item is None:

            self.processing_changed.emit(
                False
            )

            return

        self.processing = True
        self.current_item = item
        self.current_started_at = time.time()

        self.processing_changed.emit(
            True
        )

        self.queue_changed.emit(
            self.queue.count()
        )

        print(
            f">>> Démarrage épisode : "
            f"{item.episode.project_name} "
            f"{item.episode.episode_number}"
        )

        self.episode_started.emit(
            item
        )

        # ==================================================
        # Worker
        # ==================================================

        self.worker = AssistedEditingWorker(

            ui=self.ui,

            episode=item.episode,

            intro=item.intro,
            intro_path=item.intro_path,

            outro=item.outro,
            outro_path=item.outro_path,

            logo=item.logo,
            logo_path=item.logo_path,

            overlay=item.overlay,

            music=item.music,
            music_path=item.music_path,

            intro_volume=item.intro_volume,
            vod_volume=item.vod_volume,
            fade_duration=item.fade_duration,

            video_fade_in=item.video_fade_in,
            video_fade_out=item.video_fade_out,

        )

        # ==================================================
        # Thread
        # ==================================================

        self.worker_thread = QThread()

        self.worker.moveToThread(
            self.worker_thread
        )

        # Le thread démarre le Worker
        self.worker_thread.started.connect(
            self.worker.run
        )

        # Le Worker termine
        self.worker.finished.connect(
            self._on_worker_finished
        )

        # Arrêt propre du thread
        self.worker.finished.connect(
            self.worker_thread.quit
        )

        # Nettoyage du Worker
        self.worker_thread.finished.connect(
            self.worker.deleteLater
        )

        # Thread complètement terminé
        self.worker_thread.finished.connect(
            self._on_thread_finished
        )

        self.worker_thread.finished.connect(
            self.worker_thread.deleteLater
        )

        print(
            ">>> Démarrage du thread Qt"
        )

        self.worker_thread.start()

    # ==================================================
    # Worker terminé
    # ==================================================

    def _on_worker_finished(
        self,
        success: bool,
    ):

        print(
            f">>> Manager : "
            f"worker terminé ({success})"
        )

        self.last_success = success

        if self.current_item is not None:

            self.episode_finished.emit(
                self.current_item,
                success,
            )

    # ==================================================
    # Thread complètement terminé
    # ==================================================

    def _on_thread_finished(self):

        print(
            ">>> Manager : QThread terminé"
        )

        self.processing = False

        self.processing_changed.emit(
            False
        )

        if self.current_started_at is not None:

            duration = (
                time.time()
                - self.current_started_at
            )

            if duration > 0:
                self.completed_durations.append(
                    duration
                )

        self.current_started_at = None

        self.worker = None
        self.worker_thread = None

        self.current_item = None

        # ==================================================
        # Épisode suivant
        # ==================================================

        if not self.queue.empty():

            print(
                f">>> Épisode suivant : "
                f"{self.queue.count()} restant(s)"
            )

            self._start_next()

            return

        print(
            ">>> Queue terminée"
        )

        self.queue_changed.emit(0)

        self.all_finished.emit()

    # ==================================================
    # État
    # ==================================================

    def is_processing(self) -> bool:

        return self.processing

    # ==================================================

    def pending_count(self) -> int:

        return self.queue.count()

    # ==================================================

    def current_episode(self):

        if self.current_item is None:
            return None

        return self.current_item.episode

    # ==================================================
    # Informations de progression
    # ==================================================

    def remaining_count(self) -> int:

        if not self.processing:
            return 0

        return self.queue.count() + 1


    def elapsed_current(self) -> float:

        if self.current_started_at is None:
            return 0.0

        return max(
            0.0,
            time.time() - self.current_started_at,
        )


    def estimated_remaining(self) -> float | None:

        if not self.processing:
            return 0.0

        if not self.completed_durations:
            return None

        average = (
            sum(self.completed_durations)
            / len(self.completed_durations)
        )

        current_elapsed = self.elapsed_current()

        remaining_episodes = self.queue.count()

        current_estimate = max(
            average - current_elapsed,
            0.0,
        )

        return (
            current_estimate
            + remaining_episodes * average
        )