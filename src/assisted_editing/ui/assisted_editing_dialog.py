from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from assisted_editing.services.episode_repository import EpisodeRepository
from assisted_editing.services.editing_engine import EditingEngine


class AssistedEditingDialog(QDialog):

    def __init__(
        self,
        ui,
        parent=None,
    ):
        super().__init__(parent)

        self.ui = ui

        self.setObjectName("Dialog")
        self.setWindowTitle("Montage Assisté")
        self.setMinimumWidth(650)
        self.setMinimumHeight(650)

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

        section = QLabel("📺 EPISODE À PRÉPARER")
        section.setObjectName("DialogSection")
        layout.addWidget(section)

        self.episode_tree = QTreeWidget()
        self.episode_tree.setHeaderHidden(True)
        self.episode_tree.setMinimumHeight(320)

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
        resources_layout.setSpacing(4)

        self.intro = QCheckBox("Ajouter l'intro")
        self.intro.setChecked(True)

        self.outro = QCheckBox("Ajouter l'outro")
        self.outro.setChecked(True)

        self.logo = QCheckBox("Ajouter le logo")
        self.logo.setChecked(True)

        self.overlay = QCheckBox("Ajouter les overlays")
        self.overlay.setChecked(True)

        self.music = QCheckBox("Ajouter la musique")
        self.music.setChecked(True)

        for widget in (
            self.intro,
            self.outro,
            self.logo,
            self.overlay,
            self.music,
        ):
            widget.setCursor(Qt.CursorShape.PointingHandCursor)
            resources_layout.addWidget(widget)

        layout.addLayout(resources_layout)

        help_text = QLabel(
            "Les ressources sont automatiquement récupérées "
            "depuis la configuration d'APO Studio."
        )

        help_text.setObjectName("HelpText")
        help_text.setWordWrap(True)

        layout.addWidget(help_text)

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
        self.prepare_button.clicked.connect(
            self._prepare_episode
        )
        self.prepare_button.setObjectName("PrimaryButton")
        self.prepare_button.setEnabled(False)

        buttons.addWidget(cancel)
        buttons.addWidget(self.prepare_button)

        layout.addLayout(buttons)

        # ==================================================
        # Signaux
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
                empty.flags() & ~Qt.ItemFlag.ItemIsSelectable
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
                    node.flags() & ~Qt.ItemFlag.ItemIsSelectable
                )

                self.episode_tree.addTopLevelItem(node)

                node.setExpanded(True)

                series_nodes[
                    episode.project_name
                ] = node

            parent = series_nodes[
                episode.project_name
            ]

            item = QTreeWidgetItem(
                [f"🎬 Episode {episode.episode_number}"]
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
            Qt.ItemDataRole.UserRole
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

    def _prepare_episode(self):


        item = self.episode_tree.currentItem()

        if item is None:
            return

        episode = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if episode is None:
            return

        engine = EditingEngine(self.ui)

        print(">>> engine créé")

        engine.prepare(

            episode,

            intro=self.intro.isChecked(),

            outro=self.outro.isChecked(),

            logo=self.logo.isChecked(),

            overlay=self.overlay.isChecked(),

            music=self.music.isChecked(),

        )

        print(">>> prepare terminé")