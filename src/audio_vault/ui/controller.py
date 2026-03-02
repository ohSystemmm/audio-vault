import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog # type: ignore
from PyQt6 import uic # type: ignore
from PyQt6.QtGui import QIcon # type: ignore


BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "view" / "main_window.ui"
CSS_PATH = BASE_DIR / "view" / "css" / "main_window.css"
ICON_PATH = BASE_DIR / "assets" / "app-icon.png"


class AudioVaultApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self._load_ui()
        self._set_icon()
        self._load_stylesheet()
        self._connect_signals()

        self.show()

    def _load_ui(self):
        if not UI_PATH.exists():
            raise FileNotFoundError(f"UI file not found: {UI_PATH}")
        uic.loadUi(UI_PATH, self)

    def _set_icon(self):
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

    def _load_stylesheet(self):
        if CSS_PATH.exists():
            self.setStyleSheet(CSS_PATH.read_text())
        else:
            print(f"Warning: CSS file not found at {CSS_PATH}")

    def _connect_signals(self):
        self.btn_import.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            self.listWidget.addItem(Path(file_path).name)


def init_ui():
    app = QApplication(sys.argv)

    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    window = AudioVaultApp()
    sys.exit(app.exec())
