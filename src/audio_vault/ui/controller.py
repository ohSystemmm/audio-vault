import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog # type: ignore
from PyQt6 import uic # type: ignore

class AudioVaultApp(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = Path(__file__).parent / "view" / "main_window.ui"
        uic.loadUi(ui_path, self)
        
        # self.btn_import.clicked.connect(self.open_file_dialog)
        self.show()
        css_path = Path(__file__).parent / "view" / "css" / "main_window.css"
        self.load_stylesheet(css_path)

    def load_stylesheet(self, file_path):
        try:
            with open(file_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Error: The CSS file was not found at {file_path}")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Audio or Excel File", 
            "", 
            "All Files (*);;Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            file_name = os.path.basename(file_path)
            self.listWidget.addItem(file_name)

def InitUI():
    app = QApplication(sys.argv)
    window = AudioVaultApp()
    sys.exit(app.exec())
