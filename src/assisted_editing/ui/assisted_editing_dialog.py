from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from PySide6.QtCore import Qt


class AssistedEditingDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Montage Assisté")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)

        title = QLabel("🎬 Montage Assisté")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text = QLabel(
            "Bienvenue dans le moteur de montage\n"
            "d'APO Studio Pro.\n\n"
            "Cette interface sera enrichie\n"
            "au fil des prochaines versions."
        )
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        close = QPushButton("Fermer")
        close.clicked.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(text)
        layout.addStretch()
        layout.addWidget(close)