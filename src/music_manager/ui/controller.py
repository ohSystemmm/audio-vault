import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow 
from PyQt6 import uic

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = Path(__file__).parent / "view" / "main_window.ui"
        uic.loadUi(ui_path, self)
        self.show()

def InitUI():
    app = QApplication(sys.argv)
    window = UI()
    sys.exit(app.exec())