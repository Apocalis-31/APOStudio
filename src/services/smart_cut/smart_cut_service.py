from services.smart_cut.transcript_loader import TranscriptLoader
from services.smart_cut.gap_finder import GapFinder
from services.smart_cut.cut_planner import CutPlanner
from services.smart_cut.report_writer import ReportWriter
from services.smart_cut.ffmpeg_runner import FFmpegRunner



class SmartCutService:

    def __init__(self, ui, cancel_event=None):

        self.ui = ui
        self.cancel_event = cancel_event

    # ==================================================

    def _check_cancel(self):

        if self.cancel_event and self.cancel_event.is_set():
            from workers.transcription_worker import Cancelled
            raise Cancelled()

    # ==================================================

    def generate(
        self,
        project,
        settings
    ):

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("✂️ Découpage intelligent")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.ui.log(f"Mode : {settings.mode}")

        if settings.mode == "duration":

            self.ui.log(
                f"Durée cible : {settings.target_duration} min"
            )

            self.ui.log(
                f"Tolérance : ±{settings.tolerance} min"
            )

        else:

            self.ui.log(
                f"Nombre d'épisodes : {settings.episode_count}"
            )

        self.ui.log(
            f"Série : {settings.series_name}"
        )

        self.ui.log(
            f"Premier épisode : {settings.first_episode}"
        )

        self.ui.log(
            f"Renommage : {'Oui' if settings.rename else 'Non'}"
        )

        self.ui.log(
            f"IA : {'Activée' if settings.use_ai else 'Désactivée'}"
        )

        self._check_cancel()

        # ==========================================
        # Chargement du transcript
        # ==========================================

        segments = TranscriptLoader().load(project)

        self.ui.log(
            f"📄 {len(segments)} segments chargés"
        )

        self._check_cancel()

        # ==========================================
        # Recherche des gaps
        # ==========================================

        candidates = GapFinder().find(
            segments
        )

        self.ui.log(
            f"🔍 {len(candidates)} gaps détectés"
        )

        self._check_cancel()

        # ==========================================
        # Planification
        # ==========================================

        duration = segments[-1].end

        plans = CutPlanner().plan(
            candidates,
            duration,
            settings
        )

        ReportWriter().write(
            project,
            plans
        )
        self.ui.log(
            "📄 Rapport généré"
        )

        self._check_cancel()

        # ==========================================
        # EXECUTION DECOUPAGE
        # ==========================================

        self.ui.progress(75, 100)

        FFmpegRunner(
            self.ui,
            cancel_event=self.cancel_event
        ).run(
            project,
            plans,
            settings
        )

        self.ui.log(
            "🎬 Préparation du découpage..."
        )

        self.ui.log(
            f"📑 {len(plans)} épisode(s) planifié(s)"
        )

        for plan in plans:

            self.ui.log("")

            self.ui.log(
                f"📺 Episode {plan.index}"
            )

            self.ui.log(
                f"Début : {plan.start:.1f}s"
            )

            self.ui.log(
                f"Fin : {plan.end:.1f}s"
            )

            self.ui.log(
                f"Durée : {plan.end - plan.start:.1f}s"
            )

        if plans:

            plan = plans[0]

        self.ui.progress(100, 100)

        return plans