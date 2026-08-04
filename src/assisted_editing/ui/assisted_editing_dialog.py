from pathlib import Path

from PySide6.QtCore import Qt
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
)

from assisted_editing.services.editing_engine import EditingEngine
from assisted_editing.services.episode_repository import EpisodeRepository
from assisted_editing.workers.assisted_editing_worker import AssistedEditingWorker


class AssistedEditingDialog(QDialog):

    def __init__(
        self,
        ui,
        parent=None,
    ):
        super().__init__(parent)

        self.ui = ui

        self.intro_path = None
        self.outro_path = None
        self.logo_path = None
        self.music_path = None

        self.setObjectName("Dialog")
        self.setWindowTitle("Montage Assisté")
        self.setMinimumWidth(700)
        self.setMinimumHeight(760)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

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
        # Episodes
        # ==================================================

        section = QLabel("📺 EPISODES À PRÉPARER")
        section.setObjectName("DialogSection")
        layout.addWidget(section)

        self.episode_tree = QTreeWidget()

        self.episode_tree.setHeaderHidden(True)

        self.episode_tree.setMinimumHeight(260)

        self.episode_tree.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        layout.addWidget(self.episode_tree)

        self._load_episodes()

        # ==================================================
        # Ressources
        # ==================================================

        section = QLabel("⚙ RESSOURCES")
        section.setObjectName("DialogSection")
        layout.addWidget(section)

        resources_layout = QVBoxLayout()
        resources_layout.setSpacing(10)

        # ==================================================
        # Intro
        # ==================================================

        self.intro = QCheckBox("Ajouter une introduction audio")
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

        self.outro = QCheckBox("Ajouter un ending audio")
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

        self.logo = QCheckBox("Ajouter un logo")
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
                "Médias (*.png *.gif *.webm *.mov)",
                "logo",
            )
        )

        resources_layout.addWidget(logo_button)

        # ==================================================
        # Overlay
        # ==================================================

        self.overlay = QCheckBox(
            "Ajouter les overlays (bientôt)"
        )
        self.overlay.setChecked(False)
        self.overlay.setEnabled(False)

        resources_layout.addWidget(self.overlay)

        # ==================================================
        # Musique
        # ==================================================

        self.music = QCheckBox("Ajouter une musique")
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

        layout.addLayout(resources_layout)

        layout.addStretch()

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

        item = self.episode_tree.currentItem()

        if item is None:
            return

        episode = item.data(
            0,
            Qt.ItemDataRole.UserRole,
        )

        if episode is None:
            return

        self.prepare_button.setEnabled(False)
        self.prepare_button.setText("Préparation...")

        self.worker = AssistedEditingWorker(

            ui=self.ui,

            episode=episode,

            intro=self.intro.isChecked(),
            intro_path=self.intro_path,

            outro=self.outro.isChecked(),
            outro_path=self.outro_path,

            logo=self.logo.isChecked(),
            logo_path=self.logo_path,

            overlay=self.overlay.isChecked(),

            music=self.music.isChecked(),
            music_path=self.music_path,

        )

        self.worker.finished.connect(
            self._prepare_finished
        )

        self.worker.start()

    # ==================================================

    def _prepare_finished(
        self,
        success: bool,
    ):

        self.prepare_button.setEnabled(True)

        self.prepare_button.setText(
            "Préparer"
        )

        if success:

            self.accept()