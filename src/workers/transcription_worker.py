import threading
import traceback
from core.ProjectManager import ProjectManager


class TranscriptionWorker:

    def __init__(
        self,
        video_path,
        ui,
        forced_modules=None,
        on_finished=None
    ):

        self.forced_modules = forced_modules
        self.video_path = video_path
        self.ui = ui
        self.on_finished = on_finished

        self.manager = ProjectManager()

    def start(self):

        thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        thread.start()

    def run(self):

        try:

            self.manager.create_project(
                self.video_path,
                ui=self.ui,
                forced_modules=self.forced_modules
            )

        except Exception as e:

            self.ui.log("")

            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            self.ui.log("❌ Une erreur est survenue")

            self.ui.log(str(e))

            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            traceback.print_exc()
            
        finally:

            if self.on_finished:

                self.on_finished()