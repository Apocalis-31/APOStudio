import threading
import traceback

from core.ProjectManager import ProjectManager
from services.ai.glm_service import _translate_error


class Cancelled(Exception):
    pass


class TranscriptionWorker:

    def __init__(
        self,
        video_path,
        ui,
        cancel_event=None,
        forced_modules=None,
        on_finished=None
    ):

        self.video_path = video_path
        self.ui = ui
        self.cancel_event = cancel_event
        self.forced_modules = forced_modules
        self.on_finished = on_finished

        self.manager = ProjectManager()

    # ==========================================

    def check_cancelled(self):

        if self.cancel_event and self.cancel_event.is_set():
            raise Cancelled()

    # ==========================================

    def start(self):

        thread = threading.Thread(
            target=self.run,
            daemon=True
        )

        thread.start()

    # ==========================================

    def run(self):
        success = False

        try:
            print("DEBUG 2 : avant create_project")
            self.manager.create_project(
                self.video_path,
                ui=self.ui,
                cancel_event=self.cancel_event,
                forced_modules=self.forced_modules
            )
            success = True

        except Cancelled:

            self.ui.log("")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.ui.log("⏹ Traitement annulé")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        except Exception as e:

            self.ui.log("")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.ui.log("❌ Une erreur est survenue")
            self.ui.log(_translate_error(str(e)))
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            self.ui.error(_translate_error(str(e)))

            traceback.print_exc()

        finally:

            if self.on_finished:
                print("DEBUG 6 : on_finished")
                self.on_finished(cancelled=not success)

            print("DEBUG 7 : fin")