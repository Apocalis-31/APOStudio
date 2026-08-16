import os
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import math
import traceback


if getattr(sys, "frozen", False):
    _exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    _internal = os.path.join(_exe_dir, "_internal")
    BASE_DIR = _internal if os.path.isdir(_internal) else _exe_dir
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from app_info import VERSION

from PySide6.QtCore import QObject, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from core.queue_manager import QueueManager
    from core.session_statistics import SessionStatistics
    from models.cut_settings import CutSettings
    from services.config_service import ConfigService
    from services.path_service import PathService
    from services.smart_cut.smart_cut_service import SmartCutService
    from services.smart_cut.video_resolver import VideoResolver
    from services.workflow.workflow_config import WorkflowConfig
    from workers.transcription_worker import TranscriptionWorker
    from assisted_editing.ui.assisted_editing_dialog import AssistedEditingDialog
    from services.smart_cut.transcript_loader import TranscriptLoader

    PIPELINE_OK = True
    PIPELINE_ERROR = None
except Exception as _exc:  # pragma: no cover
    PIPELINE_OK = False
    PIPELINE_ERROR = _exc
    traceback.print_exc()

# ============================================================
# Palette
# ============================================================

BG = "#2b2b2b"
CARD = "#212121"
BORDER = "#333333"
ACCENT = "#8e1f45"
ACCENT_HOVER = "#a82752"
ACTION_BG = "#262626"
GREEN = "#22c55e"
AMBER = "#f59e0b"
GRAY = "#7c8494"
TEXT = "#ffffff"
TEXT_SECONDARY = "#9aa2b4"
ICON_COLOR = "#e8e8e8"

# ============================================================
# Icônes SVG
# ============================================================


def _svg(svg_body, color):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{svg_body}</svg>'
    )


SVG_FOLDER = _svg(
    '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "COLOR",
)
SVG_FOLDER_PLUS = _svg(
    '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
    '<line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/>',
    "COLOR",
)
SVG_COPY = _svg(
    '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    "COLOR",
)
SVG_DIAMOND = _svg(
    '<path d="M6 3h12l4 6-10 12L2 9z"/><path d="M2 9h20"/>',
    "COLOR",
)
SVG_STOP = _svg(
    '<rect x="5" y="5" width="14" height="14" rx="2"/>',
    "COLOR",
)
SVG_PLAY = _svg(
    '<path d="M6 5l13 7-13 7z"/>',
    "COLOR",
)


def _svg_pixmap(svg_body, color, size):
    svg_data = svg_body.replace("COLOR", color).encode("utf-8")
    renderer = None
    try:
        from PySide6.QtSvg import QSvgRenderer

        renderer = QSvgRenderer(svg_data)
    except Exception:
        pass
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    if renderer is not None:
        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()
    return pix


# ============================================================
# UiBridge : protocole ui.* attendu par le pipeline
# ============================================================


class UiBridge(QObject):

    log_signal = Signal(str)
    progress_signal = Signal(float, int)
    step_signal = Signal(str)
    current_video_signal = Signal(str)
    queue_update_signal = Signal(dict)
    queue_update_buttons_signal = Signal(dict)
    finish_signal = Signal()
    error_signal = Signal(str)
    session_started_signal = Signal()
    session_finished_signal = Signal()
    video_added_signal = Signal()
    video_finished_signal = Signal(float)
    update_info_signal = Signal(object)
    update_progress_signal = Signal(int)
    update_progress_text_signal = Signal(str)
    update_done_signal = Signal(object)
    smart_cut_started_signal = Signal()
    smart_cut_finished_signal = Signal()

    def __init__(self):
        super().__init__()
        self.log = self.log_signal.emit
        self.progress = self.progress_signal.emit
        self.step = self.step_signal.emit
        self.current_video = self.current_video_signal.emit
        self.finish = self.finish_signal.emit
        self.error = self.error_signal.emit
        self.session_started = self.session_started_signal.emit
        self.session_finished = self.session_finished_signal.emit
        self.video_added = self.video_added_signal.emit
        self.video_finished = self.video_finished_signal.emit

        # État du découpage intelligent (VOD)
        self.smart_cut_active = False
        self.smart_cut_cancel_event = None

    def queue_update(self, **kwargs):
        self.queue_update_signal.emit(kwargs)

    def queue_update_buttons(self, **kwargs):
        self.queue_update_buttons_signal.emit(kwargs)


# ============================================================
# Widgets
# ============================================================


class ProgressRing(QWidget):

    def __init__(self):
        super().__init__()
        self._progress = 0
        self._time_text = ""
        self.setMinimumSize(150, 150)
        self.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Expanding,
        )

    def set_progress(self, value):
        value = max(0.0, min(100.0, float(value)))
        if abs(value - self._progress) > 0.1:
            self._progress = value
            self.update()

    def set_time(self, elapsed="", total=""):
        if total:
            text = f"{elapsed} / {total}"
        else:
            text = elapsed
        if text != self._time_text:
            self._time_text = text
            self.update()

    def progress(self):
        return self._progress

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height())
        margin = max(14, int(size * 0.08))
        diameter = size - margin * 2
        pen_width = max(8, int(diameter * 0.055))

        rect = QRectF(
            (self.width() - diameter) / 2,
            (self.height() - diameter) / 2,
            diameter,
            diameter,
        )

        pen = QPen(QColor(GRAY), pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -360 * 16)

        if self._progress > 0:
            pen = QPen(QColor(ACCENT), pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, 90 * 16, int(-360 * 16 * self._progress / 100.0))

        percent_font = painter.font()
        percent_font.setPixelSize(max(20, int(size * 0.15)))
        percent_font.setBold(True)
        painter.setFont(percent_font)
        fm = painter.fontMetrics()
        percent_text = f"{self._progress:.0f}%"
        percent_height = fm.height()

        if self._time_text:
            time_font = painter.font()
            time_font.setPixelSize(max(12, int(size * 0.052)))
            time_font.setBold(False)
            painter.setFont(time_font)
            fm2 = painter.fontMetrics()
            time_height = fm2.height()
            block_height = percent_height + 6 + time_height
        else:
            time_height = 0
            block_height = percent_height

        start_y = rect.center().y() - block_height / 2

        painter.setFont(percent_font)
        painter.setPen(QColor(TEXT))
        painter.drawText(
            QRectF(rect.left(), start_y, rect.width(), percent_height),
            Qt.AlignmentFlag.AlignHCenter,
            percent_text,
        )

        if self._time_text:
            painter.setFont(time_font)
            painter.setPen(QColor(TEXT_SECONDARY))
            painter.drawText(
                QRectF(rect.left(), start_y + percent_height + 6, rect.width(), time_height),
                Qt.AlignmentFlag.AlignHCenter,
                self._time_text,
            )


class ActionButton(QFrame):

    clicked = Signal()

    def __init__(self, svg_body, title, subtitle="", size=32, accent=False):
        super().__init__()
        self.setObjectName("ActionButton")
        self.setProperty("accent", accent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if subtitle:
            self.setToolTip(f"{title}\n{subtitle}")
        else:
            self.setToolTip(title)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        self._icon = QLabel()
        icon_size = max(16, size - 6)
        self._icon.setPixmap(_svg_pixmap(svg_body, "#e8e8e8", icon_size))
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._icon)

        self._title = QLabel(title)
        self._title.setObjectName("ActionTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title)

        if subtitle:
            self._sub = QLabel(subtitle)
            self._sub.setObjectName("ActionSub")
            self._sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._sub)

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit()
        super().mouseReleaseEvent(event)


def _card():
    frame = QFrame()
    frame.setObjectName("Card")
    return frame, QVBoxLayout(frame)


def _fmt_dur(seconds):
    seconds = max(0, int(seconds or 0))
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def _screen_scale():
    app = QApplication.instance()
    screen = app.primaryScreen() if app else None
    if screen is None:
        return 1.0
    geo = screen.availableGeometry()
    scale = min(geo.width() / 1280, geo.height() / 720)
    return min(max(scale, 0.75), 1.4)


# ============================================================
# Fenêtre principale
# ============================================================


STEPS = ["project", "whisper", "youtube", "thumbnail", "save"]
STEP_LABELS = {
    "project": "Création du projet",
    "whisper": "Transcription Whisper",
    "youtube": "Génération YouTube",
    "thumbnail": "Génération miniature",
    "save": "Sauvegarde",
}
STEP_FRACTIONS = {
    "project": 0.05,
    "whisper": 0.60,
    "youtube": 0.78,
    "thumbnail": 0.95,
    "save": 1.0,
}


class ConsoleWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Console - APO Studio")
        self.resize(760, 420)

        icon_path = Path(BASE_DIR) / "assets" / "branding" / "logo_transparence_AS.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.log_box = QPlainTextEdit()
        self.log_box.setObjectName("Console")
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumBlockCount(5000)
        self.setCentralWidget(self.log_box)

    def closeEvent(self, event):
        event.ignore()
        self.hide()


class MainWindow(QMainWindow):

    def __init__(self, scale=None):
        super().__init__()
        self._scale = scale if scale is not None else _screen_scale()
        self.setWindowTitle(f"APO Studio {VERSION}")
        # Taille par défaut précédente (rollback) : 800 x 520, mise à l'échelle.
        self._rollback_size = QSize(
            int(800 * self._scale),
            int(520 * self._scale),
        )
        # Taille cible en test : 780 x 560.
        self._normal_size = QSize(780, 560)
        self.setMinimumSize(QSize(720, 400))
        self.resize(self._normal_size)

        self._size_timer = QTimer(self)
        self._size_timer.setSingleShot(True)
        self._size_timer.setInterval(400)
        self._size_timer.timeout.connect(self._persist_window_size)

        saved = self._load_window_size()
        if saved is not None:
            self.resize(saved)

        icon_path = Path(BASE_DIR) / "assets" / "branding" / "logo_transparence_AS.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.bridge = UiBridge()
        self.statistics = SessionStatistics()
        self.queue_manager = QueueManager(self.bridge) if PIPELINE_OK else None
        self.config = ConfigService() if PIPELINE_OK else None

        self._session_start = None
        self._step_state = {key: "wait" for key in STEPS}
        self._waiting_count = 0
        self._update_info = None
        self._update_running = False
        self._smart_cut_active = False

        self.console_window = ConsoleWindow()

        self._build_ui()
        self._connect_signals()
        self._reset_session_display()

    # --------------------------------------------------
    # Construction
    # --------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("Central")
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 12, 14, 14)
        root.setSpacing(12)

        root.addWidget(self._build_header())

        separator = QFrame()
        separator.setObjectName("HeaderLine")
        separator.setFixedHeight(1)
        root.addWidget(separator)

        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        self.grid.addWidget(self._build_left_column(), 0, 0)
        self.grid.addWidget(self._build_main_column(), 0, 1)
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)
        root.addLayout(self.grid, 1)

        self.setCentralWidget(central)

    def _build_header(self):
        header = QFrame()
        header.setObjectName("Header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(10)

        logo = QLabel()
        icon_path = Path(BASE_DIR) / "assets" / "branding" / "logo_transparence_AS.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            pixmap = pixmap.scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("APO Studio")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Assistant de création YouTube")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box)

        layout.addStretch(1)

        self.projects_button = self._emoji_button("📁", "Ouvrir le dossier des projets")
        self.workflow_button = self._emoji_button("🔀", "Workflow")
        self.ai_style_button = self._emoji_button("🎭", "Préférences IA")
        self.tools_button = self._emoji_button("🛠", "Outils")
        self.settings_button = self._emoji_button("⚙️", "Réglages")
        self.help_button = self._emoji_button("❓", "Aide")
        self.console_button = self._emoji_button("🖥️", "Ouvrir la Console")

        layout.addWidget(self.projects_button)
        layout.addWidget(self.workflow_button)
        layout.addWidget(self.ai_style_button)
        layout.addWidget(self.tools_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.help_button)
        layout.addWidget(self.console_button)

        return header

    @staticmethod
    def _emoji_button(emoji, tooltip):
        button = QPushButton(emoji)
        button.setObjectName("RoundIconButton")
        button.setFixedSize(36, 36)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    def _build_left_column(self):
        column = QWidget()
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # --- Mise à jour ---
        self.update_card, update_layout = _card()
        update_title = QLabel("🚀 Nouvelle version")
        update_title.setObjectName("CardTitle")
        update_layout.addWidget(update_title)

        self.update_info_label = QLabel()
        self.update_info_label.setObjectName("SessionValue")
        update_layout.addWidget(self.update_info_label)

        self.update_button = QPushButton("Mettre à jour")
        self.update_button.setObjectName("PrimaryButton")
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button.clicked.connect(self._start_update)
        update_layout.addWidget(self.update_button)

        self.update_progress = QProgressBar()
        self.update_progress.setTextVisible(False)
        self.update_progress.setFixedHeight(8)
        update_layout.addWidget(self.update_progress)
        self.update_progress.hide()

        self.update_progress_label = QLabel()
        self.update_progress_label.setObjectName("SessionValue")
        update_layout.addWidget(self.update_progress_label)
        self.update_progress_label.hide()

        self.update_card.hide()
        layout.addWidget(self.update_card)

        # --- Actions rapides ---
        card, card_layout = _card()
        title = QLabel("Actions rapides")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        actions = QGridLayout()
        actions.setSpacing(10)
        self.new_project_button = ActionButton(
            SVG_FOLDER_PLUS, "Nouveau Projet", "Vidéo à analyser", accent=True
        )
        self.batch_button = ActionButton(
            SVG_COPY, "Traitement par Lot", "Plusieurs vidéos", accent=True
        )
        actions.addWidget(self.new_project_button, 0, 0)
        actions.addWidget(self.batch_button, 0, 1)
        actions.setColumnStretch(0, 1)
        actions.setColumnStretch(1, 1)
        card_layout.addLayout(actions)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("StopButton")
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setFixedHeight(46)
        self.stop_button.setIcon(QIcon(_svg_pixmap(SVG_STOP, "#ffffff", 16)))
        self.stop_button.hide()
        card_layout.addSpacing(14)
        card_layout.addWidget(self.stop_button)
        layout.addWidget(card)

        # --- Modèle GLM ---
        card_model, model_layout = _card()
        model_title = QLabel("Modèle GLM")
        model_title.setObjectName("CardTitle")
        model_layout.addWidget(model_title)

        self.model_provider_label = QLabel()
        self.model_provider_label.setObjectName("ModelProvider")
        model_layout.addWidget(self.model_provider_label)

        self.model_name_label = QLabel()
        self.model_name_label.setObjectName("ModelName")
        model_layout.addWidget(self.model_name_label)

        layout.addWidget(card_model)
        layout.addStretch(1)

        return column

    def _build_main_column(self):
        column = QWidget()
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._session_row = QWidget()
        self._session_row_layout = None
        self._session_row_wide = False

        # --- Progression ---
        self.ring_card, ring_layout = _card()
        ring_title = QLabel("Progression")
        ring_title.setObjectName("CardTitle")
        ring_layout.addWidget(ring_title)

        self.ring = ProgressRing()
        self.ring.setMinimumHeight(150)
        self.ring.setMaximumHeight(240)
        ring_layout.addWidget(self.ring)

        # --- Session ---
        self.session_card, session_layout = _card()
        session_title = QLabel("Session")
        session_title.setObjectName("CardTitle")
        session_layout.addWidget(session_title)

        self.session_values = {}
        for key, icon in [
            ("Temps", "⏱ Temps"),
            ("Restant", "⏳ Restant"),
            ("Progression", "🚩 Progression"),
            ("Attente", "👥 En attente"),
            ("Fin", "🏁 Fin"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(8)
            key_label = QLabel(icon)
            key_label.setObjectName("SessionKey")
            value_label = QLabel("—")
            value_label.setObjectName("SessionValue")
            row.addWidget(key_label)
            row.addWidget(value_label)
            row.addStretch(1)
            session_layout.addLayout(row)
            self.session_values[key] = value_label

        self._rebuild_session_row()
        layout.addWidget(self._session_row)

        # --- Onglets ---
        tab_bar = QFrame()
        tab_bar.setObjectName("TabBar")
        tabs = QHBoxLayout(tab_bar)
        tabs.setContentsMargins(0, 0, 0, 0)
        tabs.setSpacing(0)

        self.tab_traitement = QPushButton("Traitement")
        self.tab_traitement.setObjectName("Tab")
        self.tab_traitement.setCheckable(True)
        self.tab_traitement.setChecked(True)
        self.tab_queue = QPushButton("File d'attente")
        self.tab_queue.setObjectName("Tab")
        self.tab_queue.setCheckable(True)

        tabs.addWidget(self.tab_traitement)
        tabs.addWidget(self.tab_queue)
        layout.addWidget(tab_bar)

        self.tab_traitement.setProperty("active", True)
        self.tab_queue.setProperty("active", False)

        # --- Contenu des onglets ---
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_task_page())
        self.stack.addWidget(self._build_queue_page())
        layout.addWidget(self.stack, 1)

        return column

    def _rebuild_session_row(self):
        if not hasattr(self, "_session_row"):
            return
        wide = self.width() >= 720
        if wide == self._session_row_wide and self._session_row_layout is not None:
            return
        self._session_row_wide = wide

        old = self._session_row.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            old.deleteLater()

        self._session_row_layout = (
            QHBoxLayout(self._session_row)
            if wide
            else QVBoxLayout(self._session_row)
        )
        self._session_row_layout.setSpacing(12)

        if wide:
            self._session_row_layout.setAlignment(
                Qt.AlignmentFlag.AlignTop
            )
            self.ring.setMinimumHeight(150)
            self.ring.setMaximumHeight(220)
            self._session_row_layout.addWidget(self.ring_card)
            self._session_row_layout.addWidget(self.session_card, 1)
        else:
            self.ring.setMinimumHeight(150)
            self.ring.setMaximumHeight(240)
            self._session_row_layout.addWidget(self.ring_card)
            self._session_row_layout.addWidget(self.session_card)

    def resizeEvent(self, event):
        self._rebuild_session_row()
        if hasattr(self, "_size_timer"):
            self._size_timer.start()
        super().resizeEvent(event)

    def _load_window_size(self):
        config = getattr(self, "config", None)
        if config is None:
            return None
        width = config.get("window.width")
        height = config.get("window.height")
        if not isinstance(width, int) or not isinstance(height, int):
            return None
        size = QSize(width, height)
        if size.width() < self.minimumWidth() or size.height() < self.minimumHeight():
            return None
        return size

    def _persist_window_size(self):
        if self.config is None:
            return
        if self.isMaximized() or self.isFullScreen():
            return
        self.config.set("window.width", self.width())
        self.config.set("window.height", self.height())
        self.config.save()

    def closeEvent(self, event):
        self._size_timer.stop()
        self._persist_window_size()
        super().closeEvent(event)

    def _build_task_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        card, card_layout = _card()
        card.setObjectName("CardFill")

        self.task_list = QLabel()
        self.task_list.setObjectName("TaskList")
        self.task_list.setTextFormat(Qt.TextFormat.RichText)
        self.task_list.setWordWrap(True)
        self.task_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        card_layout.addWidget(self.task_list)
        card_layout.addStretch(1)
        page_layout.addWidget(card)
        return page

    def _build_queue_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        card, card_layout = _card()
        card.setObjectName("CardFill")

        self.queue_progress = QLabel("En attente : 0 vidéo(s)")
        self.queue_progress.setObjectName("QueueProgress")
        card_layout.addWidget(self.queue_progress)

        self.queue_list = QLabel()
        self.queue_list.setObjectName("QueueList")
        self.queue_list.setTextFormat(Qt.TextFormat.RichText)
        self.queue_list.setWordWrap(True)
        self.queue_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        card_layout.addWidget(self.queue_list)

        self.empty_box = QFrame()
        self.empty_box.setObjectName("EmptyBox")
        empty_layout = QVBoxLayout(self.empty_box)
        empty_layout.setContentsMargins(16, 16, 16, 16)
        empty_layout.setSpacing(6)
        diamond = QLabel()
        diamond.setPixmap(_svg_pixmap(SVG_DIAMOND, GRAY, 30))
        diamond.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_text = QLabel("Aucune vidéo")
        empty_text.setObjectName("EmptyText")
        empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(diamond)
        empty_layout.addWidget(empty_text)
        card_layout.addWidget(self.empty_box)
        card_layout.addStretch(1)

        page_layout.addWidget(card)
        return page

    # --------------------------------------------------
    # Connexions
    # --------------------------------------------------

    def _connect_signals(self):
        self.new_project_button.clicked.connect(self._pick_single_video)
        self.batch_button.clicked.connect(self._pick_multiple_videos)
        self.stop_button.clicked.connect(self._toggle_run)
        self.console_button.clicked.connect(self._toggle_console)
        self.projects_button.clicked.connect(self._open_projects_folder)
        self.workflow_button.clicked.connect(self._open_workflow)
        self.ai_style_button.clicked.connect(self._open_ai_style)
        self.tools_button.clicked.connect(self._open_tools)
        self.settings_button.clicked.connect(self._open_settings)
        self.help_button.clicked.connect(self._open_help)

        self.tab_traitement.clicked.connect(self._switch_tab)
        self.tab_queue.clicked.connect(self._switch_tab)

        bridge = self.bridge
        bridge.log_signal.connect(self._on_log)
        bridge.step_signal.connect(self._on_step)
        bridge.progress_signal.connect(self._on_progress)
        bridge.session_started_signal.connect(self._on_session_started)
        bridge.session_finished_signal.connect(self._on_session_finished)
        bridge.video_added_signal.connect(self._on_video_added)
        bridge.video_finished_signal.connect(self._on_video_finished)
        bridge.queue_update_signal.connect(self._on_queue_update)
        bridge.current_video_signal.connect(self._on_current_video)
        bridge.finish_signal.connect(self._on_session_finished)
        bridge.error_signal.connect(self._on_error)
        bridge.update_info_signal.connect(self._on_update_info)
        bridge.update_progress_signal.connect(self._on_update_progress)
        bridge.update_progress_text_signal.connect(self._on_update_progress_text)
        bridge.update_done_signal.connect(self._on_update_done)
        bridge.smart_cut_started_signal.connect(self._on_smart_cut_started)
        bridge.smart_cut_finished_signal.connect(self._on_smart_cut_finished)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(1000)

        if not PIPELINE_OK:
            self._log(f"⚠️ Pipeline non disponible : {PIPELINE_ERROR}")

    # --------------------------------------------------
    # Actions réelles
    # --------------------------------------------------

    def _pick_single_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une vidéo",
            "",
            "Fichiers vidéo (*.mp4 *.mkv *.avi *.mov *.webm);;Tous les fichiers (*.*)",
        )
        if path:
            self.queue_manager.add(path)

    def _pick_multiple_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Choisir plusieurs vidéos",
            "",
            "Fichiers vidéo (*.mp4 *.mkv *.avi *.mov *.webm);;Tous les fichiers (*.*)",
        )
        for path in paths:
            self.queue_manager.add(path)

    def _toggle_run(self):
        if getattr(self.bridge, "smart_cut_active", False):
            cancel_event = getattr(
                self.bridge, "smart_cut_cancel_event", None
            )
            if cancel_event is not None:
                cancel_event.set()
            self._log("🛑 Arrêt du découpage demandé...")
            return
        if self.queue_manager is None:
            return
        if self.queue_manager.running:
            self.queue_manager.stop()
        elif self.queue_manager.failed_videos:
            self.queue_manager.restart()
        else:
            self._log("ℹ️ Aucune vidéo en file d'attente. Utilisez « Nouveau Projet » ou « Traitement par Lot ».")

    def _toggle_console(self):
        if self.console_window.isVisible():
            self.console_window.hide()
            self.console_button.setToolTip("Ouvrir la Console")
        else:
            self.console_window.show()
            self.console_window.raise_()
            self.console_window.activateWindow()
            self.console_button.setToolTip("Fermer la Console")

    def _open_projects_folder(self):
        try:
            projects = PathService.projects()
            projects.mkdir(exist_ok=True)
            os.startfile(projects.resolve())
        except Exception as exc:
            self._log(f"❌ Impossible d'ouvrir le dossier projets : {exc}")

    def _open_settings(self):
        dialog = SettingsDialog(self.config, self)
        dialog.saved.connect(self._refresh_model_card)
        dialog.exec()

    def _open_workflow(self):
        dialog = WorkflowDialog(self)
        dialog.exec()

    def _open_ai_style(self):
        dialog = AIStyleDialog(self)
        dialog.exec()

    def _open_tools(self):
        dialog = ToolsDialog(
            self.bridge,
            self,
        )        
        dialog.exec()

    def _open_help(self):
        dialog = HelpDialog(self)
        dialog.exec()

    # --------------------------------------------------
    # Signaux du pipeline
    # --------------------------------------------------

    def _on_log(self, message):
        self._log(message)

    def _log(self, message):
        self.console_window.log_box.appendPlainText(str(message))
        self.console_window.log_box.verticalScrollBar().setValue(
            self.console_window.log_box.verticalScrollBar().maximum()
        )

    def _on_progress(self, value, total):
        if self._smart_cut_active and total and total > 0:
            self.ring.set_progress(
                min(100.0, float(value) * 100.0 / float(total))
            )

    def _on_step(self, key):
        if key not in STEPS:
            return
        if key == "project":
            for other in STEPS:
                self._step_state[other] = "wait"
        self._step_state[key] = "pending"
        for other in STEPS:
            if other != key and self._step_state[other] == "pending":
                self._step_state[other] = "done"
        self._render_tasks()
        if self._smart_cut_active and key in STEP_FRACTIONS:
            self.ring.set_progress(min(70.0, STEP_FRACTIONS[key] * 70.0))
        self._update_ring_progress()

    def _on_current_video(self, name):
        self._log(f"▶ Vidéo en cours : {name}")

    def _on_video_added(self):
        self.statistics.add_video()
        self._refresh_session_statistics()

    def _on_video_finished(self, duration):
        self.statistics.finish_video()
        self.statistics.add_processing_time(duration)
        for key in STEPS:
            self._step_state[key] = "done"
        self._render_tasks()
        self._refresh_session_statistics()

    def _on_session_started(self):
        if self._session_start is None:
            self._session_start = time.time()
        self._step_state = {key: "wait" for key in STEPS}
        self._render_tasks()
        self._set_running(True)
        self._refresh_session_statistics()
        self._log("🚀 Session démarrée")

    def _on_session_finished(self):
        self._session_start = None
        if not self._smart_cut_active:
            self._set_running(False)
        self._reset_session_display()
        self._log("🏁 Session terminée")

    def _on_error(self, message):
        self._log(f"❌ {message}")
        if not getattr(self, "_error_box_open", False):
            self._error_box_open = True
            box = QMessageBox(self)
            box.setWindowTitle("Erreur lors du traitement")
            box.setIcon(QMessageBox.Icon.Warning)
            box.setText("Une erreur est survenue pendant le traitement.")
            box.setInformativeText(str(message))
            box.setStandardButtons(QMessageBox.StandardButton.Ok)
            box.finished.connect(lambda _: setattr(self, "_error_box_open", False))
            box.show()

    # --------------------------------------------------
    # Mise à jour
    # --------------------------------------------------

    def _check_update(self):
        if not PIPELINE_OK:
            return
        try:
            from services.update_service import UpdateService
            info = UpdateService.check()
        except Exception as exc:
            self.bridge.log_signal.emit(f"ℹ️ Vérification de mise à jour impossible : {exc}")
            return
        self.bridge.update_info_signal.emit(info)

    def _on_update_info(self, info):
        if info is None or not getattr(info, "has_update", False):
            self.update_card.hide()
            return
        self._update_info = info
        kind = (
            "Patch (zip)"
            if info.is_patch
            else ("Installeur léger" if info.is_gpu else "Installeur complet")
        )
        self.update_info_label.setText(
            f"APO Studio {info.current_version} → {info.latest_version}\n{kind}"
        )
        self.update_card.show()

    def _start_update(self):
        info = self._update_info
        if info is None or self._update_running:
            return
        self._update_running = True
        self.update_button.setEnabled(False)
        self.update_button.setText("Téléchargement…")
        self.update_progress.setValue(0)
        self.update_progress.show()
        self.update_progress_label.setText("0 / 0 Mo")
        self.update_progress_label.show()
        threading.Thread(
            target=self._download_update, args=(info,), daemon=True
        ).start()

    def _download_update(self, info):
        def on_progress(done, total):
            if total > 0:
                self.bridge.update_progress_signal.emit(int(done * 100 / total))
                self.bridge.update_progress_text_signal.emit(
                    f"{done / (1024 * 1024):.1f} / {total / (1024 * 1024):.1f} Mo"
                )

        try:
            import subprocess
            from services.update_install_service import UpdateInstallService
            if info.is_patch:
                UpdateInstallService.install_patch(info, on_progress=on_progress)
            else:
                installer_path = UpdateInstallService.install(
                    info, on_progress=on_progress
                )
                subprocess.Popen([installer_path])
        except Exception as exc:
            self.bridge.update_done_signal.emit(str(exc))
            return
        self.bridge.update_done_signal.emit(True)

    def _on_update_progress(self, pct):
        self.update_progress.setValue(pct)

    def _on_update_progress_text(self, text):
        self.update_progress_label.setText(text)

    def _on_update_done(self, result):
        self._update_running = False
        self.update_button.setEnabled(True)
        self.update_button.setText("Mettre à jour")
        if result is True:
            if self._update_info and self._update_info.is_patch:
                self._log("✅ Mise à jour téléchargée — redémarrage en cours…")
                QTimer.singleShot(800, QApplication.instance().quit)
            else:
                self._log("✅ Mise à jour téléchargée — l'installeur démarre.")
        else:
            self._log(f"❌ Mise à jour impossible : {result}")

    def _on_queue_update(self, data):
        waiting = data.get("waiting", [])
        self._waiting_count = len(waiting)
        self.queue_progress.setText(f"En attente : {len(waiting)} vidéo(s)")
        self._refresh_session_statistics()
        if waiting:
            lines = "".join(
                f'<div style="color:{TEXT_SECONDARY}">⏳ {name}</div>'
                for name in waiting
            )
            self.queue_list.setText(lines)
            self.queue_list.show()
            self.empty_box.hide()
        else:
            self.queue_list.hide()
            self.empty_box.show()

    # --------------------------------------------------
    # État UI
    # --------------------------------------------------

    def _set_running(self, running):
        self.stop_button.setVisible(running)
        if running:
            self.stop_button.setText("Stop")
            self.stop_button.setIcon(QIcon(_svg_pixmap(SVG_STOP, "#ffffff", 16)))
            self.stop_button.setProperty("running", True)
        else:
            self.stop_button.setProperty("running", False)
        self.stop_button.style().unpolish(self.stop_button)
        self.stop_button.style().polish(self.stop_button)

    def _on_smart_cut_started(self):
        self._smart_cut_active = True
        if self._session_start is None:
            self._session_start = time.time()
        self._set_running(True)
        self._log("✂️ Découpage intelligent démarré")

    def _on_smart_cut_finished(self):
        self._smart_cut_active = False
        if self.queue_manager is None or not self.queue_manager.running:
            self._session_start = None
            self._set_running(False)
            self.ring.set_progress(0)
            self.ring.set_time("--:--", "--:--")
            self.session_values["Temps"].setText("—")

    def _refresh_model_card(self):
        if self.config is None:
            return
        try:
            provider = self.config.get("ai.provider", "glm")
            model = self.config.get(f"{provider}.model", None) or self.config.get("glm.model", "—")
            self.model_provider_label.setText(f"Fournisseur : {str(provider).upper()}")
            self.model_name_label.setText(f"Modèle : {model}")
        except Exception:
            self.model_provider_label.setText("Fournisseur : —")
            self.model_name_label.setText("Modèle : —")

    def _render_tasks(self):
        rows = []
        for key in STEPS:
            label = STEP_LABELS[key]
            state = self._step_state.get(key, "wait")
            if state == "done":
                status_html = f'<span style="color:{GREEN}">✓ Complété</span>'
                dot = f'<span style="color:{GREEN}">●</span>'
                name_color = TEXT_SECONDARY
            elif state == "pending":
                status_html = f'<span style="color:{AMBER}">En cours...</span>'
                dot = f'<span style="color:{AMBER}">●</span>'
                name_color = TEXT
            else:
                status_html = f'<span style="color:{GRAY}">En attente...</span>'
                dot = f'<span style="color:{GRAY}">●</span>'
                name_color = TEXT_SECONDARY
            rows.append(
                f'<tr><td style="color:{name_color};padding:3px 6px 3px 0">{dot} {label}</td>'
                f'<td style="text-align:right;padding:3px 0 3px 6px">{status_html}</td></tr>'
            )
        self.task_list.setText(
            f'<table style="border-collapse:collapse;width:100%">{"".join(rows)}</table>'
        )

    def _estimated_remaining(self):
        if self._smart_cut_active:
            progress = self.ring.progress()
            if progress <= 0 or self._session_start is None:
                return 0
            elapsed = time.time() - self._session_start
            total_est = elapsed * 100.0 / progress
            return max(total_est - elapsed, 0)
        if self._session_start is None:
            return 0
        elapsed = time.time() - self._session_start
        frac = self._current_step_fraction()
        current_remaining = 0
        if frac > 0:
            current_remaining = max(elapsed * (1 - frac) / frac, 0)
        queued = max(self.statistics.waiting_videos - 1, 0)
        return current_remaining + queued * self.statistics.average_processing_time

    def _current_step_fraction(self):
        best = 0.0
        for key, frac in STEP_FRACTIONS.items():
            if self._step_state.get(key) in ("done", "pending"):
                best = max(best, frac)
        return best

    def _update_ring_progress(self):
        if self._smart_cut_active:
            return
        total = self.statistics.total_videos
        if total == 0:
            self.ring.set_progress(0)
            return
        share = 100.0 / total
        base = self.statistics.finished_videos * share
        frac = self._current_step_fraction()
        self.ring.set_progress(base + share * frac)

    def _refresh_session_statistics(self):
        self.session_values["Attente"].setText(str(self._waiting_count))
        self.session_values["Progression"].setText(
            f"{self.statistics.finished_videos}/{self.statistics.total_videos}"
        )
        remaining = self._estimated_remaining()
        end = datetime.now() + timedelta(seconds=remaining) if remaining > 0 else None
        self.session_values["Restant"].setText(
            _fmt_dur(remaining) if remaining > 0 else "—"
        )
        self.session_values["Fin"].setText(
            end.strftime("%H:%M") if end else "—"
        )

    def _reset_session_display(self):
        for key in self.session_values:
            self.session_values[key].setText("—")
        self._waiting_count = 0
        self.ring.set_progress(0)
        self.ring.set_time("--:--", "--:--")
        self._step_state = {key: "wait" for key in STEPS}
        self._render_tasks()

    def _on_timer(self):
        if self._session_start is None:
            return
        elapsed = time.time() - self._session_start
        self.session_values["Temps"].setText(_fmt_dur(elapsed))
        remaining = self._estimated_remaining()
        total_est = (elapsed + remaining) if remaining > 0 else None
        self.ring.set_time(
            _fmt_dur(elapsed),
            _fmt_dur(total_est) if total_est else "--:--",
        )
        self._update_ring_progress()
        self._refresh_session_statistics()

    def _switch_tab(self):
        to_traitement = self.sender() is self.tab_traitement
        self.tab_traitement.setChecked(to_traitement)
        self.tab_queue.setChecked(not to_traitement)
        self.tab_traitement.setProperty("active", to_traitement)
        self.tab_queue.setProperty("active", not to_traitement)
        self.tab_traitement.style().unpolish(self.tab_traitement)
        self.tab_traitement.style().polish(self.tab_traitement)
        self.tab_queue.style().unpolish(self.tab_queue)
        self.tab_queue.style().polish(self.tab_queue)
        self.stack.setCurrentIndex(0 if to_traitement else 1)

    def closeEvent(self, event):
        if self.queue_manager is not None and self.queue_manager.running:
            self.queue_manager.stop()
        self.console_window.close()
        app = QApplication.instance()
        if app is not None:
            QTimer.singleShot(0, app.quit)
        super().closeEvent(event)


# ============================================================
# Dialogues
# ============================================================


class SettingsDialog(QDialog):

    saved = Signal()

    MODEL_SUGGESTIONS = {
        "openai": ["gpt-5.5"],
        "claude": ["claude-sonnet-4"],
        "glm": ["glm-4.7-flash", "glm-4.6v-flash"],
        "nvidia": ["deepseek-ai/deepseek-v4-flash"],
        "gemini": ["gemini-2.5-flash"],
        "ollama": ["llama3.2"],
        "lmstudio": [],
    }

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setObjectName("Dialog")
        self.setWindowTitle("Réglages")
        self.setMinimumWidth(440)
        self.config = config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Réglages du modèle IA")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        layout.addWidget(self._section("FOURNISSEUR"))

        self.provider_combo = QComboBox()
        self.provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        providers = ["openai", "claude", "glm", "nvidia", "gemini", "ollama", "lmstudio"]
        for provider in providers:
            self.provider_combo.addItem(provider.capitalize(), provider)
        layout.addWidget(self.provider_combo)

        layout.addWidget(self._section("CLÉ API"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Votre clé API")
        layout.addWidget(self.api_key_input)

        layout.addWidget(self._section("MODÈLE"))
        self.model_input = QComboBox()
        self.model_input.setEditable(True)
        self.model_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.model_input.setPlaceholderText("Ex. : glm-4.7-flash")
        layout.addWidget(self.model_input)

        layout.addWidget(self._section("URL DE L'API"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Optionnel — pour Ollama / LM Studio")
        layout.addWidget(self.url_input)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("DialogButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn = QPushButton("Enregistrer")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons.addStretch(1)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._save)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)

        self._load_current()

    @staticmethod
    def _section(text):
        label = QLabel(text)
        label.setObjectName("DialogSection")
        return label

    def _fill_model_suggestions(self, provider):
        self.model_input.clear()
        for model in self.MODEL_SUGGESTIONS.get(provider, []):
            self.model_input.addItem(model)

    def _load_current(self):
        if self.config is None:
            return
        try:
            provider = self.config.get("ai.provider", "glm")
            index = self.provider_combo.findData(provider)
            if index >= 0:
                self.provider_combo.setCurrentIndex(index)
            provider_cfg = self.config.get(provider, {}) or {}
            self.api_key_input.setText(provider_cfg.get("api_key", ""))
            self._fill_model_suggestions(provider)
            self.model_input.setCurrentText(provider_cfg.get("model", ""))
            self.url_input.setText(provider_cfg.get("base_url", ""))
        except Exception:
            pass

    def _on_provider_changed(self, _index):
        if self.config is None:
            return
        provider = self.provider_combo.currentData()
        provider_cfg = self.config.get(provider, {}) or {}
        self.api_key_input.setText(provider_cfg.get("api_key", ""))
        self._fill_model_suggestions(provider)
        self.model_input.setCurrentText(provider_cfg.get("model", ""))
        self.url_input.setText(provider_cfg.get("base_url", ""))

    def _save(self):
        if self.config is None:
            self.accept()
            return
        provider = self.provider_combo.currentData()
        self.config.set("ai.provider", provider)
        self.config.set(f"{provider}.api_key", self.api_key_input.text().strip())
        self.config.set(f"{provider}.model", self.model_input.currentText().strip())
        base_url = self.url_input.text().strip()
        if base_url:
            self.config.set(f"{provider}.base_url", base_url)
        self.config.save()
        self.saved.emit()
        self.accept()


class HelpDialog(QDialog):

    PAGES = [
        ("🏠 Guide de démarrage", "index.md"),
        ("📂 Gestion des projets", "project.md"),
        ("🎤 Transcription", "transcription.md"),
        ("🤖 Génération IA", "ai.md"),
        ("✂️ SmartCut", "smart_cut.md"),
        ("🖼️ Miniatures", "thumbnail.md"),
        ("⚙️ Paramètres", "settings.md"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dialog")
        self.setWindowTitle("Documentation - APO Studio")
        self.resize(1000, 700)
        self.setMinimumSize(860, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("📖 Documentation APO Studio")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        body = QHBoxLayout()
        body.setSpacing(10)

        self.navigation = QListWidget()
        self.navigation.setObjectName("DocNav")
        self.navigation.setMinimumWidth(220)
        self.navigation.setMaximumWidth(280)
        self.navigation.setCursor(Qt.CursorShape.PointingHandCursor)
        for label, filename in self.PAGES:
            self.navigation.addItem(label)
            self.navigation.item(self.navigation.count() - 1).setData(
                Qt.ItemDataRole.UserRole, filename
            )
        body.addWidget(self.navigation)

        self.content = QTextBrowser()
        self.content.setObjectName("DocContent")
        self.content.setOpenExternalLinks(True)
        body.addWidget(self.content, 1)

        layout.addLayout(body, 1)

        close_btn = QPushButton("Fermer")
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)
        close_btn.clicked.connect(self.accept)

        self.navigation.currentRowChanged.connect(self._load_page)
        self.navigation.setCurrentRow(0)

    def _load_page(self, row):
        item = self.navigation.item(row)
        if item is None:
            return
        filename = item.data(Qt.ItemDataRole.UserRole)
        path = PathService.docs() / filename
        if path.exists():
            self.content.setMarkdown(path.read_text(encoding="utf-8"))
        else:
            self.content.setPlainText(f"Impossible de trouver : {filename}")
        self.content.verticalScrollBar().setValue(0)


class WorkflowDialog(QDialog):

    MODULES = [
        ("transcription", "Transcription Whisper",
         "Génère le texte de la vidéo, indispensable pour la suite du workflow."),
        ("youtube", "Génération YouTube",
         "Rédige automatiquement la description, les titres et les tags."),
        ("thumbnail", "Génération miniature",
         "Crée une miniature automatique à partir d'une image extraite."),
        ("vision", "Sélection IA des miniatures",
         "L'IA choisit la meilleure miniature parmi plusieurs extraits."),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dialog")
        self.setWindowTitle("Workflow")
        self.setMinimumWidth(480)
        self.workflow_config = WorkflowConfig()
        workflow = self.workflow_config.load()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Workflow")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        desc = QLabel("Modules exécutés pour chaque vidéo, dans l'ordre.")
        desc.setObjectName("DialogSection")
        layout.addWidget(desc)

        self.checkboxes = {}
        for key, label, hint in self.MODULES:
            box = QCheckBox(label)
            box.setChecked(key in workflow.enabled)
            box.setCursor(Qt.CursorShape.PointingHandCursor)
            box.setToolTip(hint)
            self.checkboxes[key] = box
            layout.addWidget(box)
            if hint:
                hint_label = QLabel(hint)
                hint_label.setObjectName("WorkflowHint")
                hint_label.setWordWrap(True)
                hint_label.setIndent(24)
                layout.addWidget(hint_label)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("DialogButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn = QPushButton("Enregistrer")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons.addStretch(1)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._save)

    def _save(self):
        enabled = [
            key for key, box in self.checkboxes.items()
            if box.isChecked()
        ]
        workflow = self.workflow_config.load()
        workflow.enabled = enabled
        self.workflow_config.save(workflow)
        self.accept()


class AIStyleDialog(QDialog):

    FILES = [
        ("Profil", "creator.md"),
        ("Introduction", "intro.md"),
        ("Miniature", "thumbnail.md"),
        ("Hook", "hook.md"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Dialog")
        self.setWindowTitle("Préférences IA")
        self.resize(680, 620)
        self.current_file = self.FILES[0][1]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🤖 Préférences de l'IA")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        bar = QHBoxLayout()
        bar.setSpacing(0)
        self.tabs = {}
        for label, filename in self.FILES:
            btn = QPushButton(label)
            btn.setObjectName("SegTab")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, f=filename: self._select(f))
            self.tabs[filename] = btn
            bar.addWidget(btn)
        layout.addLayout(bar)

        layout.addWidget(self._sec("RÈGLES D'APO STUDIO"))
        self.official_box = QPlainTextEdit()
        self.official_box.setObjectName("Editor")
        self.official_box.setReadOnly(True)
        self.official_box.setMaximumHeight(170)
        layout.addWidget(self.official_box)

        layout.addWidget(self._sec("PERSONNALISATION"))
        self.user_box = QPlainTextEdit()
        self.user_box.setObjectName("Editor")
        layout.addWidget(self.user_box, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("DialogButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn = QPushButton("💾 Enregistrer les préférences")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons.addStretch(1)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._save)

        self.tabs[self.current_file].setChecked(True)
        self._load()

    @staticmethod
    def _sec(text):
        label = QLabel(text)
        label.setObjectName("DialogSection")
        return label

    def _select(self, filename):
        self.current_file = filename
        for name, btn in self.tabs.items():
            btn.setChecked(name == filename)
        self._load()

    def _load(self):
        official = PathService.knowledge() / self.current_file
        self.official_box.setPlainText(
            official.read_text(encoding="utf-8") if official.exists() else ""
        )
        user = PathService.user_prompts() / self.current_file
        self.user_box.setPlainText(
            user.read_text(encoding="utf-8") if user.exists() else ""
        )

    def _save(self):
        target = PathService.user_prompts() / self.current_file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.user_box.toPlainText().strip(), encoding="utf-8")
        self.accept()


class SmartCutDialog(QDialog):

    def __init__(self, project, ui, parent=None):
        super().__init__(parent)
        self.setObjectName("Dialog")
        self.setWindowTitle("Découpage intelligent")
        self.setMinimumWidth(460)
        self.project = project
        self.ui = ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("✂️ Découpage intelligent")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        info = QLabel(
            f"Vidéo : {Path(project.video_path).name}\nSérie : {project.series}"
        )
        
        segments = TranscriptLoader().load(project)
        self.total_duration = segments[-1].end
        info.setObjectName("HelpText")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addWidget(self._field_label("MODE"))
        self.mode_duration = QRadioButton("Durée cible")
        self.mode_duration.setChecked(True)
        self.mode_count = QRadioButton("Nombre de vidéos")
        for radio in (self.mode_duration, self.mode_count):
            radio.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(radio)

        self.estimation = QLabel()
        self.estimation.setObjectName("HelpText")
        self.estimation.setWordWrap(True)
        layout.addWidget(self.estimation)

        layout.addWidget(self._field_label("DURÉE CIBLE (MINUTES)"))
        self.target_duration = QLineEdit("60")
        layout.addWidget(self.target_duration)

        layout.addWidget(self._field_label("TOLÉRANCE (MINUTES)"))
        self.tolerance = QLineEdit("15")
        layout.addWidget(self.tolerance)

        layout.addWidget(self._field_label("CHEVAUCHEMENT (SECONDES)"))
        self.overlap_seconds = QLineEdit("5")
        layout.addWidget(self.overlap_seconds)

        layout.addWidget(self._field_label("NOMBRE DE VIDÉOS"))
        self.episode_count = QLineEdit("6")
        layout.addWidget(self.episode_count)



        layout.addWidget(self._field_label("NOM DE LA SÉRIE"))
        self.series_name = QLineEdit(project.series)
        layout.addWidget(self.series_name)

        layout.addWidget(self._field_label("PREMIER ÉPISODE"))
        next_episode = project.next_episode
        self.first_episode = QLineEdit(str((next_episode or 0) + 1))
        layout.addWidget(self.first_episode)

        self.rename = QCheckBox("Renommer automatiquement")
        self.rename.setChecked(True)
        self.use_ai = QCheckBox("Utiliser l'IA")
        self.use_ai.setChecked(True)
        for box in (self.rename, self.use_ai):
            box.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(box)

        self.mode_duration.toggled.connect(self._update_estimation)
        self.mode_count.toggled.connect(self._update_estimation)

        self.target_duration.textChanged.connect(self._update_estimation)
        self.episode_count.textChanged.connect(self._update_estimation)

        self._update_estimation()
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("DialogButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        start_btn = QPushButton("✂️ Découper")
        start_btn.setObjectName("PrimaryButton")
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons.addStretch(1)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(start_btn)
        layout.addLayout(buttons)

        cancel_btn.clicked.connect(self.reject)
        start_btn.clicked.connect(self._start)

    @staticmethod
    def _field_label(text):
        label = QLabel(text)
        label.setObjectName("DialogSection")
        return label

    def _update_estimation(self):

        try:

            if self.mode_duration.isChecked():

                target = max(
                    1,
                    int(self.target_duration.text() or 60)
                )

                episodes = math.ceil(
                    self.total_duration /
                    (target * 60)
                )

                total_h = int(self.total_duration // 3600)
                total_m = int((self.total_duration % 3600) // 60)

                self.estimation.setText(

                    f"⏱ Durée totale : {total_h} h {total_m} min\n"
                    f"📺 Environ {episodes} épisode(s) de {target} minutes"

                )

            else:

                count = max(
                    1,
                    int(self.episode_count.text() or 1)
                )

                average = self.total_duration / count

                minutes = int(average // 60)

                total_h = int(self.total_duration // 3600)
                total_m = int((self.total_duration % 3600) // 60)

                self.estimation.setText(

                    f"⏱ Durée totale : {total_h} h {total_m} min\n"
                    f"📺 {count} épisode(s) d'environ {minutes} minutes"

                )

        except Exception:

            self.estimation.setText("")

    def _start(self):
        try:
            settings = CutSettings(
                mode="duration" if self.mode_duration.isChecked() else "count",
                target_duration=int(self.target_duration.text() or 0),
                tolerance=int(self.tolerance.text() or 0),
                episode_count=int(self.episode_count.text() or 0),
                overlap_seconds=int(self.overlap_seconds.text() or 0),
                rename=self.rename.isChecked(),
                series_name=self.series_name.text().strip(),
                first_episode=int(self.first_episode.text() or 1),
                use_ai=self.use_ai.isChecked(),
            )
        except ValueError:
            QMessageBox.warning(self, "Découpage", "Valeurs numériques invalides.")
            return

        from workers.transcription_worker import Cancelled

        bridge = self.ui
        cancel_event = threading.Event()
        bridge.smart_cut_cancel_event = cancel_event

        def run_cut():
            bridge.smart_cut_active = True
            bridge.smart_cut_started_signal.emit()
            try:
                SmartCutService(
                    bridge,
                    cancel_event=cancel_event,
                ).generate(self.project, settings)
            except Cancelled:
                bridge.log("🛑 Découpage annulé.")
            except Exception as exc:
                bridge.log(f"❌ Erreur lors du découpage : {exc}")
            finally:
                bridge.smart_cut_active = False
                bridge.smart_cut_cancel_event = None
                bridge.smart_cut_finished_signal.emit()

        threading.Thread(target=run_cut, daemon=True).start()
        self.accept()


class ToolsDialog(QDialog):

    prepared = Signal(object, bool)


    def __init__(
        self,
        ui,
        parent=None,
    ):        
        super().__init__(parent)
        self.setObjectName("Dialog")
        self.setWindowTitle("Outils - APO Studio")
        self.setMinimumWidth(480)
        self.ui = ui

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # ==================================================
        # Titre
        # ==================================================

        title = QLabel("🧰 Outils")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        subtitle = QLabel("Outils complémentaires d'APO Studio")
        subtitle.setObjectName("DialogSection")
        layout.addWidget(subtitle)

        # ==================================================
        # Découpage de VOD
        # ==================================================

        card, card_layout = _card()

        card_title = QLabel("✂️ Découpage de VOD")
        card_title.setObjectName("CardTitle")
        card_layout.addWidget(card_title)

        desc = QLabel(
            "Découpe intelligemment une VOD complète\n"
            "en plusieurs épisodes prêts à être montés."
        )
        desc.setObjectName("HelpText")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        self.launch_button = QPushButton("Lancer")
        self.launch_button.setObjectName("PrimaryButton")
        self.launch_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.launch_button.clicked.connect(self._launch_smart_cut)

        card_layout.addWidget(
            self.launch_button,
            0,
            Qt.AlignmentFlag.AlignRight,
        )

        layout.addWidget(card)

        # ==================================================
        # Montage Assisté
        # ==================================================

        card2, card2_layout = _card()

        card2_title = QLabel("🎬 Montage Assisté")
        card2_title.setObjectName("CardTitle")
        card2_layout.addWidget(card2_title)

        desc2 = QLabel(
            "Assemble automatiquement une VOD\n"
            "avec introduction, overlays\n"
            "et autres ressources."
        )
        desc2.setObjectName("HelpText")
        desc2.setWordWrap(True)
        card2_layout.addWidget(desc2)

        self.assisted_button = QPushButton("Lancer")
        self.assisted_button.setObjectName("PrimaryButton")
        self.assisted_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.assisted_button.clicked.connect(
            self._launch_assisted_editing
        )

        card2_layout.addWidget(
            self.assisted_button,
            0,
            Qt.AlignmentFlag.AlignRight,
        )

        layout.addWidget(card2)

        # ==================================================

        self.status = QLabel("")
        self.status.setObjectName("DialogSection")
        layout.addWidget(self.status)

        close_btn = QPushButton("Fermer")
        close_btn.setObjectName("DialogButton")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        layout.addWidget(
            close_btn,
            0,
            Qt.AlignmentFlag.AlignRight,
        )

        self.prepared.connect(self._on_prepared)

    # ==================================================

    def _launch_smart_cut(self):

        video, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir une VOD",
            "",
            "Vidéo MP4 (*.mp4);;Tous les fichiers (*.*)",
        )

        if not video:
            return

        self.ui.log("")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.ui.log("🎬 Découpage de VOD")
        self.ui.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        bridge = self.ui
        cancel_event = threading.Event()

        bridge.smart_cut_active = True
        bridge.smart_cut_cancel_event = cancel_event
        bridge.smart_cut_started_signal.emit()

        self.launch_button.setEnabled(False)
        self.status.setText("⏳ Préparation de la VOD en cours...")

        def finished(cancelled=False):

            bridge.smart_cut_active = False
            bridge.smart_cut_cancel_event = None
            bridge.smart_cut_finished_signal.emit()

            if cancelled:
                self.prepared.emit(None, True)
                return

            project = VideoResolver(bridge).resolve(video)

            self.prepared.emit(project, False)

        TranscriptionWorker(
            video,
            bridge,
            forced_modules=["transcription"],
            cancel_event=cancel_event,
            on_finished=finished,
        ).start()


    def _on_prepared(self, project, cancelled):

        self.launch_button.setEnabled(True)
        self.status.setText("")

        if cancelled:
            QMessageBox.information(
                self,
                "Découpage",
                "Préparation annulée."
            )
            return

        if project is None:
            QMessageBox.warning(
                self,
                "Découpage",
                "Impossible de charger le projet."
            )
            return

        SmartCutDialog(
            project,
            self.ui,
            self,
        ).exec()

    # ==================================================

    def _launch_assisted_editing(self):

        AssistedEditingDialog(
            self.ui,
            self,
        ).exec()
# ============================================================
# Démarrage
# ============================================================


def main():
    app = QApplication(sys.argv)

    scale = _screen_scale()

    if scale != 1.0:
        font = app.font()
        font.setPointSizeF(
            font.pointSizeF() * min(max(scale, 0.9), 1.2)
        )
        app.setFont(font)

    style_path = Path(BASE_DIR) / "style.qss"
    if style_path.exists():
        qss = style_path.read_text(encoding="utf-8")
        assets_dir = (Path(BASE_DIR) / "assets").resolve().as_posix()
        qss = qss.replace("@ASSETS@", assets_dir)
        app.setStyleSheet(qss)

    icon_path = Path(BASE_DIR) / "assets" / "branding" / "logo_transparence_AS.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow(scale=scale)
    window.show()

    window._log(f"🚀 APO Studio {VERSION} démarré")
    window._log("Console prête — les journaux du pipeline s'affichent ici.")

    if PIPELINE_OK:
        window._refresh_model_card()
        window._on_queue_update({"current": "En attente...", "waiting": []})
        threading.Thread(target=window._check_update, daemon=True).start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
