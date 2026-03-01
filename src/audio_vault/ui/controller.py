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
        
        # Connect the button click to our function
        self.btn_import.clicked.connect(self.open_file_dialog)
        self.showMaximized()

    def open_file_dialog(self):
        # Open file explorer
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Audio or Excel File", 
            "", 
            "All Files (*);;Excel Files (*.xlsx *.xls);;Audio Files (*.mp3 *.wav)"
        )
        
        if file_path:
            file_name = os.path.basename(file_path)
            self.listWidget.addItem(file_name)

def InitUI():
    app = QApplication(sys.argv)
    window = AudioVaultApp()
    sys.exit(app.exec())
