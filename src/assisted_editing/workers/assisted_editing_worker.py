from PySide6.QtCore import QObject, Signal, Slot
import traceback

from assisted_editing.services.editing_engine import EditingEngine


class AssistedEditingWorker(QObject):

    finished = Signal(bool)

    # ==================================================

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
        intro_volume,
        vod_volume,
        fade_duration,
        video_fade_in,
        video_fade_out,
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

        self.intro_volume = intro_volume
        self.vod_volume = vod_volume
        self.fade_duration = fade_duration

        self.video_fade_in = video_fade_in
        self.video_fade_out = video_fade_out

    # ==================================================

    @Slot()
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

                intro_volume=self.intro_volume,
                vod_volume=self.vod_volume,
                fade_duration=self.fade_duration,

                video_fade_in=self.video_fade_in,
                video_fade_out=self.video_fade_out,

            )

            success = True

        except Exception:

            traceback.print_exc()

            self.ui.log("")
            self.ui.log(
                "❌ Le montage assisté a échoué."
            )

        finally:

            print(
                f">>> Worker terminé - émission finished({success})"
            )

            self.finished.emit(success)

            print(
                ">>> Signal finished émis"
            )