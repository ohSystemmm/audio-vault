import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog # type: ignore
from PyQt6 import uic # type: ignore
from PyQt6.QtGui import QIcon, QTextCursor, QTextCharFormat, QColor # type: ignore
from datetime import datetime
from audio_vault.core.excel.load import load_and_validate_excel # type: ignore
from audio_vault.ui.worker import DownloadWorker # type: ignore
from pathlib import WindowsPath
import os


BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "view"
CSS_PATH = BASE_DIR / "view" / "css" / "main_window.css"
ICON_PATH = BASE_DIR / "assets" / "app-icon.png"


class AudioVaultApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loaded_df = None  # Store loaded DataFrame
        self.loaded_file_path = None  # Store loaded file path
        self.download_worker = None  # Store download worker thread
        self._load_ui()
        self._set_icon()
        self._load_stylesheet()
        self._setup_progress_bar()
        self._connect_signals()
        self.log_message("Audio Vault started")
        self.show()

    def _load_ui(self):
        if not (UI_PATH / "main_window.ui").exists():
            raise FileNotFoundError(f"UI file not found: {UI_PATH / "main_window.ui"}")
        uic.loadUi(UI_PATH / "main_window.ui", self)

    def _set_icon(self):
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

    def _load_stylesheet(self):
        if CSS_PATH.exists():
            self.setStyleSheet(CSS_PATH.read_text())
        else:
            print(f"Warning: CSS file not found at {CSS_PATH}")

    def _setup_progress_bar(self):
        """Initialize progress bar settings"""
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.status_label.setText("0/0 songs")

    def _connect_signals(self):
        self.btn_open_file.clicked.connect(self.on_open_file_clicked)
        self.btn_download.clicked.connect(self.on_download_clicked)
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)

    def on_open_file_clicked(self):
        print("Open file button clicked")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            self.log_message(f"File opened: {Path(file_path).name}")
            
            # Validate and load the Excel file
            df, errors = load_and_validate_excel(file_path)
            
            if errors:
                # Log all errors
                for error in errors:
                    self.log_message(f"[ERROR] Validation Error: {error}")
                self.set_status("File validation failed - file rejected", success=False)
                self.loaded_df = None
                self.loaded_file_path = None
                self.progress_bar.setValue(0)
            elif df is not None:
                # File is valid
                self.log_message(f"[SUCCESS] File validation successful")
                self.log_message(f"Loaded {len(df)} songs")
                self.set_status("File loaded and validated successfully", success=True)
                # Store df for later use (download functionality)
                self.loaded_df = df
                self.loaded_file_path = file_path
                self.progress_bar.setValue(0)
            else:
                self.set_status("File loading failed", success=False)
                self.loaded_df = None
                self.loaded_file_path = None
                self.progress_bar.setValue(0)

    def on_download_clicked(self):
        print("Download button clicked")
        
        # Check if a file has been loaded
        if self.loaded_df is None:
            self.log_message("[ERROR] No file loaded. Please load an Excel file first.")
            self.set_status("No file loaded", success=False)
            return
        
        # Check if a download is already in progress
        if self.download_worker is not None and self.download_worker.isRunning():
            self.log_message("[ERROR] Download already in progress")
            return
        
        # Get the Windows Downloads folder
        downloads_folder = Path(os.path.expanduser("~")) / "Downloads"
        
        # Get Excel filename without extension
        excel_filename = Path(self.loaded_file_path).stem
        
        # Create folder in downloads with Excel filename
        output_dir = downloads_folder / excel_filename
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_message("Download started...")
        self.log_message(f"Output directory: {output_dir}")
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Update button states
        self.btn_open_file.setEnabled(False)
        self.btn_download.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        
        # Create and start download worker
        self.download_worker = DownloadWorker(self.loaded_df, str(output_dir))
        self.download_worker.progress_updated.connect(self.on_progress_updated)
        self.download_worker.log_message.connect(self.log_message)
        self.download_worker.download_finished.connect(self.on_download_finished)
        self.download_worker.error_occurred.connect(self.on_download_error)
        self.download_worker.start()
    
    def on_cancel_clicked(self):
        """Handle cancel button click"""
        if self.download_worker is not None and self.download_worker.isRunning():
            self.log_message("[INFO] Cancelling download...")
            self.download_worker.cancel()
            self.btn_cancel.setEnabled(False)
    
    def on_progress_updated(self, current: int, total: int):
        """Handle progress updates from the download worker"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.status_label.setText(f"{current}/{total} songs")
    
    def on_download_finished(self, successful: int, failed: int, errors: list):
        """Handle download completion"""
        # Log results
        self.log_message(f"[SUCCESS] Successfully downloaded: {successful} songs")
        
        if failed > 0:
            self.log_message(f"[ERROR] Failed to download: {failed} songs")
            for error in errors:
                self.log_message(f"  - {error}")
        
        if successful > 0:
            self.log_message("Download completed successfully")
            self.set_status(f"Download completed: {successful}/{len(self.loaded_df)} songs", success=True)
            self.progress_bar.setValue(100)
        elif failed > 0:
            self.set_status("Download failed", success=False)
        
        # Re-enable buttons
        self.btn_open_file.setEnabled(True)
        self.btn_download.setEnabled(True)
        self.btn_cancel.setEnabled(False)
    
    def on_download_error(self, error_message: str):
        """Handle download errors"""
        self.log_message(f"[ERROR] Download error: {error_message}")
        self.set_status("Download failed with error", success=False)
        
        # Re-enable buttons
        self.btn_open_file.setEnabled(True)
        self.btn_download.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def log_message(self, message: str):
        """Add a message to the log display with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Determine color based on message type
        color = QColor("#B0E8F5")  # Default cyan
        
        if "[ERROR]" in message:
            color = QColor("#FF6666")  # Red for errors
        elif "[SUCCESS]" in message:
            color = QColor("#66FF66")  # Green for success
        elif "completed" in message.lower() and "[ERROR]" not in message:
            color = QColor("#66FF66")  # Green for completions
        elif "(skipped" in message.lower():
            color = QColor("#FFFF66")  # Yellow for skipped
        elif "[CANCELLED]" in message or "[INFO]" in message:
            color = QColor("#FFFF66")  # Yellow for info/cancelled
        
        # Add the colored text to the log
        doc = self.log_display.document()
        cursor = QTextCursor(doc)
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        
        cursor.setCharFormat(fmt)
        cursor.insertText(log_entry + "\n")
        
        # Scroll to bottom
        self.log_display.ensureCursorVisible()
        
        print(log_entry)

    def set_status(self, message: str, success: bool = False):
        """Update the status label"""
        self.status_label.setText(message)
        if success:
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: black;")


def init_ui():
    app = QApplication(sys.argv)

    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    window = AudioVaultApp()
    sys.exit(app.exec())