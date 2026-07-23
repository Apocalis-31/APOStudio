from models.project import Project

from services.thumbnail.frame_extractor import FrameExtractor
from services.thumbnail.frame_filter import FrameFilter
from services.thumbnail.frame_selector import FrameSelector
from services.thumbnail.frame_exporter import FrameExporter
from services.thumbnail.frame_vision import FrameVision

from services.workflow.workflow_manager import WorkflowManager


class ThumbnailService:

    def __init__(self, ui, cancel_event=None):

        self.ui = ui
        self.cancel_event = cancel_event

    def generate(self, project: Project):

        self.ui.log("🖼️ Génération proposition de miniature...")

        self.ui.log("🎞️ Extraction des captures...")

        # ==========================
        # Extraction
        # ==========================

        FrameExtractor(self.ui).extract(project)

        # ==========================
        # Filtrage
        # ==========================

        self.ui.log("🧹 Filtrage des captures...")

        FrameFilter(self.ui).filter(project)

        # ==========================
        # Sélection
        # ==========================

        self.ui.log("🎯 Sélection des captures...")

        frames = FrameSelector(self.ui).extract(project)

        # ==========================
        # Vision (optionnel)
        # ==========================

        workflow = WorkflowManager()

        if workflow.enabled("vision"):

            self.ui.log("🧠 Sélection IA des captures...")

            try:

                frames = FrameVision(self.ui, cancel_event=self.cancel_event).rank(
                    project,
                    frames
                )

            except Exception as e:

                self.ui.log("")

                self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                self.ui.log("❌ Sélection IA des miniatures impossible")

                self.ui.log(str(e))

                self.ui.log(
                    "⚠️ Les miniatures n'ont pas pu être sélectionnées automatiquement."
                )

                self.ui.log(
                    "ℹ️ Le reste du projet a été traité correctement."
                )

                self.ui.log(
                    "🔄 Vous pourrez relancer la sélection plus tard."
                )

                self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

                self.ui.log("")

        # ==========================
        # Export
        # ==========================

        self.ui.log(f"DEBUG : {len(frames)} capture(s) à exporter")

        FrameExporter(self.ui).export(
            project,
            frames
        )

        self.ui.log(
            f"📁 {len(frames)} captures exportées"
        )

        self.ui.log(
            "✅ Sélection des miniatures terminée"
        )