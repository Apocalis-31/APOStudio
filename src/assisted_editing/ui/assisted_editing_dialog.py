from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QFrame,
    QSlider,
)

from assisted_editing.models.editing_queue_item import EditingQueueItem
from assisted_editing.services.episode_repository import EpisodeRepository
from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt


class AssistedEditingDialog(QDialog):

    def __init__(
        self,
        ui,
        manager,
        parent=None,
    ):
        super().__init__(parent)

        self.ui = ui
        self.manager = manager
        self.manager.all_finished.connect(
            self._on_all_finished
        )
        self.intro_path = None
        self.outro_path = None
        self.logo_path = None
        self.music_path = None
        

        self.setObjectName("Dialog")
        self.setWindowTitle("Montage Assisté")
        self.setMinimumWidth(1150)
        self.setMinimumHeight(760)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        layout.setSpacing(15)

        # ==================================================
        # Titre
        # ==================================================

        title = QLabel("🎬 Montage Assisté")
        title.setObjectName("DialogTitle")

        layout.addWidget(title)

        subtitle = QLabel(
            "Prépare automatiquement un épisode avant le montage."
        )

        subtitle.setObjectName("HelpText")
        subtitle.setWordWrap(True)

        layout.addWidget(subtitle)

        # ==================================================
        # Zone principale
        # ==================================================

        content = QHBoxLayout()
        content.setSpacing(15)

        layout.addLayout(
            content,
            1,
        )

        # ==================================================
        # Panel Ressources
        # ==================================================

        resources_frame = QFrame()
        resources_frame.setObjectName(
            "Panel"
        )
        resources_frame.setFixedWidth(250)

        resources_layout = QVBoxLayout(
            resources_frame
        )

        resources_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )

        resources_layout.setSpacing(12)

        content.addWidget(
            resources_frame
        )

        # ==================================================
        # Panel Paramètres
        # ==================================================

        settings_frame = QFrame()
        settings_frame.setObjectName(
            "Panel"
        )
        settings_frame.setFixedWidth(260)

        settings_layout = QVBoxLayout(
            settings_frame
        )

        settings_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )

        settings_layout.setSpacing(12)

        content.addWidget(
            settings_frame
        )

        # ==================================================
        # Panel Episodes
        # ==================================================

        episodes_frame = QFrame()
        episodes_frame.setObjectName(
            "Panel"
        )

        episodes_layout = QVBoxLayout(
            episodes_frame
        )

        episodes_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )

        episodes_layout.setSpacing(12)

        content.addWidget(
            episodes_frame,
            1,
        )
        # ==================================================
        # Episodes
        # ==================================================

        section = QLabel("📺 EPISODES À PRÉPARER")
        section.setObjectName("DialogSection")

        episodes_layout.addWidget(section)

        self.episode_tree = QTreeWidget()

        self.episode_tree.setHeaderHidden(True)

        self.episode_tree.setMinimumWidth(650)
        self.episode_tree.setMinimumHeight(520)

        self.episode_tree.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        episodes_layout.addWidget(
            self.episode_tree,
            1,
        )

        self._load_episodes()
        # ==================================================
        # Ressources
        # ==================================================

        section = QLabel("📦 RESSOURCES")
        section.setObjectName("DialogSection")

        resources_layout.addWidget(section)


        # ==================================================
        # Audio
        # ==================================================

        section = QLabel("🎵 AUDIO")
        section.setObjectName("DialogSection")

        settings_layout.addWidget(section)

        audio_layout = QVBoxLayout()

        audio_layout.setSpacing(12)

        settings_layout.addLayout(audio_layout)

        # ==================================================
        # Volume Intro
        # ==================================================

        self.intro_volume_title = QLabel(
            "Volume de l'introduction"
        )

        audio_layout.addWidget(
            self.intro_volume_title
        )

        self.intro_volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.intro_volume_slider.setRange(
            0,
            100,
        )

        self.intro_volume_slider.setValue(
            100,
        )

        audio_layout.addWidget(
            self.intro_volume_slider
        )

        self.intro_volume_value = QLabel(
            "100 %"
        )

        self.intro_volume_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        audio_layout.addWidget(
            self.intro_volume_value
        )

        # ==================================================
        # Volume VOD
        # ==================================================

        self.vod_volume_title = QLabel(
            "Volume de la vidéo"
        )

        audio_layout.addWidget(
            self.vod_volume_title
        )

        self.vod_volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.vod_volume_slider.setRange(
            0,
            100,
        )

        self.vod_volume_slider.setValue(
            10,
        )

        audio_layout.addWidget(
            self.vod_volume_slider
        )

        self.vod_volume_value = QLabel(
            "10 %"
        )

        self.vod_volume_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        audio_layout.addWidget(
            self.vod_volume_value
        )

        # ==================================================
        # Fondu retour
        # ==================================================

        self.fade_title = QLabel(
            "Durée du fondu"
        )

        audio_layout.addWidget(
            self.fade_title
        )

        self.fade_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.fade_slider.setRange(
            5,
            50,
        )

        self.fade_slider.setValue(
            15,
        )

        audio_layout.addWidget(
            self.fade_slider
        )

        self.fade_value = QLabel(
            "1.5 s"
        )

        self.fade_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        audio_layout.addWidget(
            self.fade_value)

        # ==================================================
        # Vidéo
        # ==================================================

        section = QLabel("🎬 VIDÉO")
        section.setObjectName("DialogSection")

        settings_layout.addWidget(section)

        video_layout = QVBoxLayout()

        settings_layout.addLayout(video_layout)

        # ==================================================
        # Fade In
        # ==================================================

        self.video_fade_in_title = QLabel(
            "Fondu d'entrée"
        )

        video_layout.addWidget(
            self.video_fade_in_title
        )

        self.video_fade_in_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.video_fade_in_slider.setRange(
            0,
            150,
        )

        self.video_fade_in_slider.setValue(
            20,
        )

        video_layout.addWidget(
            self.video_fade_in_slider
        )

        self.video_fade_in_value = QLabel(
            "2.0 s"
        )

        self.video_fade_in_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        video_layout.addWidget(
            self.video_fade_in_value)

        # ==================================================
        # Fade Out
        # ==================================================

        self.video_fade_out_title = QLabel(
            "Fondu de sortie"
        )

        video_layout.addWidget(
            self.video_fade_out_title
        )

        self.video_fade_out_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.video_fade_out_slider.setRange(
            0,
            50,
        )

        self.video_fade_out_slider.setValue(
            25,
        )

        video_layout.addWidget(
            self.video_fade_out_slider
        )

        self.video_fade_out_value = QLabel(
            "2.5 s"
        )

        self.video_fade_out_value.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        video_layout.addWidget(
            self.video_fade_out_value)

        # ==================================================
        # Mise à jour des labels
        # ==================================================

        self.intro_volume_slider.valueChanged.connect(

            lambda value:
            self.intro_volume_value.setText(
                f"{value} %"
            )

        )

        self.vod_volume_slider.valueChanged.connect(

            lambda value:
            self.vod_volume_value.setText(
                f"{value} %"
            )

        )

        self.fade_slider.valueChanged.connect(

            lambda value:
            self.fade_value.setText(
                f"{value / 10:.1f} s"
            )

        )

        self.video_fade_in_slider.valueChanged.connect(

            lambda value:
            self.video_fade_in_value.setText(
                f"{value / 10:.1f} s"
            )

        )

        self.video_fade_out_slider.valueChanged.connect(

            lambda value:
            self.video_fade_out_value.setText(
                f"{value / 10:.1f} s"
            )

        )

        # ==================================================
        # Intro
        # ==================================================

        self.intro = QCheckBox("Introduction audio")
        self.intro.setChecked(True)
        self.intro.setCursor(Qt.CursorShape.PointingHandCursor)

        resources_layout.addWidget(self.intro)

        self.intro_label = QLabel("Aucun fichier sélectionné")
        self.intro_label.setObjectName("HelpText")

        resources_layout.addWidget(self.intro_label)

        intro_button = QPushButton("Parcourir...")

        intro_button.clicked.connect(

            lambda: self._select_resource(

                "Choisir une introduction",

                "Audio (*.mp3 *.wav)",

                "intro",

            )

        )

        resources_layout.addWidget(intro_button)

        # ==================================================
        # Outro
        # ==================================================

        self.outro = QCheckBox("Ending audio")
        self.outro.setChecked(True)
        self.outro.setCursor(Qt.CursorShape.PointingHandCursor)

        resources_layout.addWidget(self.outro)

        self.outro_label = QLabel("Aucun fichier sélectionné")
        self.outro_label.setObjectName("HelpText")

        resources_layout.addWidget(self.outro_label)

        outro_button = QPushButton("Parcourir...")

        outro_button.clicked.connect(

            lambda: self._select_resource(

                "Choisir un ending",

                "Audio (*.mp3 *.wav)",

                "outro",

            )

        )

        resources_layout.addWidget(outro_button)

        # ==================================================
        # Logo
        # ==================================================

        self.logo = QCheckBox("Logo animé")
        self.logo.setChecked(True)
        self.logo.setCursor(Qt.CursorShape.PointingHandCursor)

        resources_layout.addWidget(self.logo)

        self.logo_label = QLabel("Aucun fichier sélectionné")
        self.logo_label.setObjectName("HelpText")

        resources_layout.addWidget(self.logo_label)

        logo_button = QPushButton("Parcourir...")

        logo_button.clicked.connect(

            lambda: self._select_resource(

                "Choisir un logo",

                "Médias (*.mov *.webm *.png)",

                "logo",

            )

        )

        resources_layout.addWidget(logo_button)

        # ==================================================
        # Musique
        # ==================================================

        self.music = QCheckBox("Musique de fond")
        self.music.setChecked(False)
        self.music.setCursor(Qt.CursorShape.PointingHandCursor)

        resources_layout.addWidget(self.music)

        self.music_label = QLabel("Aucun fichier sélectionné")
        self.music_label.setObjectName("HelpText")

        resources_layout.addWidget(self.music_label)

        music_button = QPushButton("Parcourir...")

        music_button.clicked.connect(

            lambda: self._select_resource(

                "Choisir une musique",

                "Audio (*.mp3 *.wav)",

                "music",

            )

        )

        resources_layout.addWidget(music_button)

        # ==================================================
        # Overlay
        # ==================================================

        self.overlay = QCheckBox("Overlays (bientôt)")
        self.overlay.setChecked(False)
        self.overlay.setEnabled(False)

        resources_layout.addWidget(self.overlay)

        resources_layout.addStretch()

        # ==================================================
        # Boutons
        # ==================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        cancel = QPushButton("Annuler")
        cancel.setObjectName("DialogButton")
        cancel.clicked.connect(self.reject)

        self.prepare_button = QPushButton("Préparer")
        self.prepare_button.setObjectName("PrimaryButton")
        self.prepare_button.setEnabled(False)

        self.prepare_button.clicked.connect(
            self._prepare_episode
        )

        buttons.addWidget(cancel)
        buttons.addWidget(self.prepare_button)

        layout.addLayout(buttons)

        # ==================================================

        self.episode_tree.itemSelectionChanged.connect(
            self._update_prepare_button
        )

    # ==================================================

    def _load_episodes(self):

        self.episode_tree.clear()

        repository = EpisodeRepository()

        episodes = repository.get_pending()

        if not episodes:

            empty = QTreeWidgetItem(
                ["Aucun épisode à préparer."]
            )

            empty.setFlags(
                empty.flags()
                & ~Qt.ItemFlag.ItemIsSelectable
            )

            self.episode_tree.addTopLevelItem(empty)

            return

        series_nodes = {}

        for episode in episodes:

            if episode.project_name not in series_nodes:

                node = QTreeWidgetItem(
                    [f"📁 {episode.project_name}"]
                )

                node.setFlags(
                    node.flags()
                    & ~Qt.ItemFlag.ItemIsSelectable
                )

                node.setExpanded(True)

                self.episode_tree.addTopLevelItem(node)

                series_nodes[
                    episode.project_name
                ] = node

            parent = series_nodes[
                episode.project_name
            ]

            item = QTreeWidgetItem(
                [
                    f"🎬 Episode {episode.episode_number}"
                ]
            )

            item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                episode,
            )

            parent.addChild(item)

    # ==================================================

    def _update_prepare_button(self):

        items = self.episode_tree.selectedItems()

        if not items:

            self.prepare_button.setEnabled(False)
            self.prepare_button.setText("Préparer")

            return

        episode = items[0].data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if episode is None:

            self.prepare_button.setEnabled(False)
            self.prepare_button.setText("Préparer")

            return

        self.prepare_button.setEnabled(True)

        self.prepare_button.setText(
            f"Préparer Episode {episode.episode_number}"
        )

    # ==================================================

    def _select_resource(
        self,
        title,
        file_filter,
        target,
    ):

        filename, _ = QFileDialog.getOpenFileName(

            self,

            title,

            "",

            file_filter,

        )

        if not filename:
            return

        path = Path(filename)

        setattr(
            self,
            f"{target}_path",
            path,
        )

        label = getattr(
            self,
            f"{target}_label",
        )

        label.setText(path.name)

    # ==================================================

    def _prepare_episode(self):

        queue_item = self._create_queue_item()

        if queue_item is None:
            return

        self.manager.enqueue(
            queue_item
        )

        self.prepare_button.setEnabled(True)
        self.prepare_button.setText(
            "Ajouter un épisode"
        )


    # ==================================================

    def _create_queue_item(self):

        item = self.episode_tree.currentItem()

        if item is None:
            return None

        episode = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if episode is None:
            return None

        if episode is None:
            return None

        return EditingQueueItem(

            # ==========================================
            # Episode
            # ==========================================

            episode=episode,

            # ==========================================
            # Ressources
            # ==========================================

            intro=self.intro.isChecked(),
            intro_path=self.intro_path,

            outro=self.outro.isChecked(),
            outro_path=self.outro_path,

            logo=self.logo.isChecked(),
            logo_path=self.logo_path,

            overlay=self.overlay.isChecked(),

            music=self.music.isChecked(),
            music_path=self.music_path,

            # ==========================================
            # Audio
            # ==========================================

            intro_volume=(
                self.intro_volume_slider.value() / 100
            ),

            vod_volume=(
                self.vod_volume_slider.value() / 100
            ),

            fade_duration=(
                self.fade_slider.value() / 10
            ),

            # ==========================================
            # Vidéo
            # ==========================================

            video_fade_in=(
                self.video_fade_in_slider.value() / 10
            ),

            video_fade_out=(
                self.video_fade_out_slider.value() / 10
            ),

        )


    def _on_all_finished(self):

        self.prepare_button.setEnabled(True)
        self.prepare_button.setText(
            "Préparer"
        )