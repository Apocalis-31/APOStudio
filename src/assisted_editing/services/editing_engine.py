from assisted_editing.models import timeline
from assisted_editing.models.video_settings import VideoSettings
from assisted_editing.models.audio_settings import AudioSettings
from assisted_editing.services.ffmpeg_executor import FFmpegExecutor
from assisted_editing.services.media_probe import MediaProbe
from assisted_editing.services.render_job_factory import RenderJobFactory
from assisted_editing.services.render_validator import RenderValidator
from assisted_editing.services.resource_preparer import ResourcePreparer
from assisted_editing.services.timeline_builder import TimelineBuilder
from assisted_editing.services.rendering_pipeline import (
    RenderingPipeline,
)


class EditingEngine:

    def __init__(self, ui):

        self.ui = ui

    # ==================================================

    def prepare(
        self,
        episode,

        intro=True,
        intro_path=None,

        outro=True,
        outro_path=None,

        logo=True,
        logo_path=None,

        overlay=True,

        music=True,
        music_path=None,

        intro_volume=1.0,
        vod_volume=0.10,
        fade_duration=1.5,

        video_fade_in=1.5,
        video_fade_out=1.5,
    ):

        # ==================================================
        # Informations
        # ==================================================

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🎬 Montage Assisté")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.ui.log(f"Série   : {episode.project_name}")
        self.ui.log(f"Episode : {episode.episode_number}")
        self.ui.log("")

        self.ui.log("📦 Ressources sélectionnées")

        self.ui.log(
            f"   {'✅' if intro else '❌'} Intro"
        )

        if intro and intro_path:
            self.ui.log(f"      ↳ {intro_path.name}")

        self.ui.log(
            f"   {'✅' if outro else '❌'} Outro"
        )

        if outro and outro_path:
            self.ui.log(f"      ↳ {outro_path.name}")

        self.ui.log(
            f"   {'✅' if logo else '❌'} Logo"
        )

        if logo and logo_path:
            self.ui.log(f"      ↳ {logo_path.name}")

        self.ui.log(
            f"   {'✅' if overlay else '❌'} Overlays"
        )

        self.ui.log(
            f"   {'✅' if music else '❌'} Musique"
        )

        if music and music_path:
            self.ui.log(f"      ↳ {music_path.name}")

        # ==================================================
        # Préparation des ressources
        # ==================================================

        self.ui.log("")

        ResourcePreparer(self.ui).prepare(

            episode,

            intro=intro,
            intro_path=intro_path,

            outro=outro,
            outro_path=outro_path,

            logo=logo,
            logo_path=logo_path,

            overlay=overlay,

            music=music,
            music_path=music_path,

        )

        self.ui.log("")
        self.ui.log("✅ Episode préparé")

        # ==================================================
        # RenderJob
        # ==================================================

        render_job = RenderJobFactory().build(
            episode
        )

        RenderValidator().validate(
            render_job
        )

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🎬 RenderJob")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.ui.log(
            f"Entrée  : {render_job.master_video.name}"
        )

        self.ui.log(
            f"Sortie  : {render_job.output_video.name}"
        )

        if render_job.introduction:

            self.ui.log(
                f"Intro   : {render_job.introduction.path.name}"
            )

        if render_job.ending:

            self.ui.log(
                f"Outro   : {render_job.ending.path.name}"
            )

        if render_job.music:

            self.ui.log(
                f"Musique : {render_job.music.path.name}"
            )

        self.ui.log("")
        self.ui.log("✅ RenderJob valide")

        # ==================================================
        # Paramètres audio
        # ==================================================

        audio_settings = AudioSettings(

            intro_volume=intro_volume,

            vod_volume=vod_volume,

            fade_duration=fade_duration,

        )

        video_settings = VideoSettings(

            fade_in=video_fade_in,
            fade_out=video_fade_out,

        )

        # ==================================================
        # Timeline
        # ==================================================

        timeline = TimelineBuilder(
            MediaProbe()
        ).build(

            render_job,

            audio_settings,
            video_settings,
        )

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🕒 Timeline")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.ui.log(
            f"Vidéo   : {timeline.master_video.name}"
        )

        self.ui.log(
            f"Sortie  : {timeline.output_video.name}"
        )

        if timeline.introduction:

            self.ui.log(
                f"Intro   : {timeline.introduction.path.name}"
            )

            self.ui.log(
                f"Durée   : {timeline.introduction_duration:.2f}s"
            )

        if timeline.ending:

            self.ui.log(
                f"Outro   : {timeline.ending.path.name}"
            )

        if timeline.music:

            self.ui.log(
                f"Musique : {timeline.music.path.name}"
            )

        self.ui.log("")
        self.ui.log("✅ Timeline construite")

        # ==================================================
        # Paramètres Audio
        # ==================================================

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🎵 Paramètres Audio")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.ui.log(
            f"Volume Intro : {timeline.audio.intro_volume * 100:.0f}%"
        )

        self.ui.log(
            f"Volume VOD   : {timeline.audio.vod_volume * 100:.0f}%"
        )

        self.ui.log(
            f"Fondu retour : {timeline.audio.fade_duration:.1f}s"
        )


        # ==================================================
        # Rendu
        # ==================================================
        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🎬 Paramètres Vidéo")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.ui.log(
            f"Fade In  : {timeline.video.fade_in:.1f}s"
        )

        self.ui.log(
            f"Fade Out : {timeline.video.fade_out:.1f}s"
        )

        RenderingPipeline(
            self.ui
        ).render(
            timeline
        )

