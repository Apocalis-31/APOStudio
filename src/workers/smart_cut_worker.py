import threading
import traceback

from core.ProjectManager import ProjectManager
from services.smart_cut.smart_cut_service import SmartCutService
from services.ai.glm_service import _translate_error


class Cancelled(Exception):
    pass


class SmartCutWorker:

    def __init__(
        self,
        ui,
        cancel_event,
        project,
        settings,
        on_finished=None
    ):

        self.ui = ui
        self.cancel_event = cancel_event
        self.project = project
        self.settings = settings
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

    def run(self, on_finished=None):

        success = False

        try:

            self.check_cancelled()

            self.ui.log("")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.ui.log("✂️ Découpage intelligent")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.ui.log(f"Mode : {self.settings.mode}")

            if self.settings.mode == "duration":

                self.ui.log(
                    f"Durée cible : {self.settings.target_duration} min"
                )

                self.ui.log(
                    f"Tolérance : ±{self.settings.tolerance} min"
                )

            else:

                self.ui.log(
                    f"Nombre d'épisodes : {self.settings.episode_count}"
                )

            self.ui.log(
                f"Série : {self.settings.series_name}"
            )

            self.ui.log(
                f"Premier épisode : {self.settings.first_episode}"
            )

            self.ui.log(
                f"Renommage : {'Oui' if self.settings.rename else 'Non'}"
            )

            self.ui.log(
                f"IA : {'Activée' if self.settings.use_ai else 'Désactivée'}"
            )

            SmartCutService(self.ui).generate(
                self.project,
                self.settings
            )

            success = True

        except Cancelled:

            self.ui.log("")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.ui.log("⏹ Découpage intelligent annulé")
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

                self.on_finished(cancelled=not success)

            self.ui.log("")
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.ui.log("❌ Une erreur est survenue")
            self.ui.log(_translate_error(str(e)))
            self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            self.ui.error(_translate_error(str(e)))

            traceback.print_exc()

        finally:

            if self.on_finished:

                self.on_finished(cancelled=not success)
