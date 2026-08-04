from PySide6.QtCore import QObject, Signal
import threading
import traceback

from assisted_editing.services.editing_engine import EditingEngine


class AssistedEditingWorker(QObject):

    finished = Signal(bool)

    def __init__(
        self,
        ui,
        episode,
        intro,
        intro_path,
        outro,
        outro_path,
        logo,
        logo_path,
        overlay,
        music,
        music_path,
    ):
        super().__init__()

        self.ui = ui
        self.episode = episode

        self.intro = intro
        self.intro_path = intro_path

        self.outro = outro
        self.outro_path = outro_path

        self.logo = logo
        self.logo_path = logo_path

        self.overlay = overlay

        self.music = music
        self.music_path = music_path

    # ==================================================

    def start(self):

        threading.Thread(

            target=self.run,

            daemon=True,

        ).start()

    # ==================================================

    def run(self):

        success = False

        try:

            EditingEngine(
                self.ui
            ).prepare(

                self.episode,

                intro=self.intro,
                intro_path=self.intro_path,

                outro=self.outro,
                outro_path=self.outro_path,

                logo=self.logo,
                logo_path=self.logo_path,

                overlay=self.overlay,

                music=self.music,
                music_path=self.music_path,

            )

            success = True

        except Exception:

            traceback.print_exc()

            self.ui.log("")
            self.ui.log("❌ Le montage assisté a échoué.")

        finally:

            self.finished.emit(success)