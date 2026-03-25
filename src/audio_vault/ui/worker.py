from PyQt6.QtCore import QThread, pyqtSignal # type: ignore
import yt_dlp
from pathlib import Path


class DownloadWorker(QThread):
    """Worker thread for downloading songs without freezing the UI"""
    
    # Signals for communication with the main thread
    progress_updated = pyqtSignal(int, int)  # (index, total)
    log_message = pyqtSignal(str)  # (message)
    download_finished = pyqtSignal(int, int, list)  # (successful, failed, errors)
    error_occurred = pyqtSignal(str)  # (error_message)
    
    def __init__(self, df, output_dir: str):
        super().__init__()
        self.df = df
        self.output_dir = output_dir
        self.is_cancelled = False
    
    def cancel(self):
        """Request cancellation of the download"""
        self.is_cancelled = True
    
    def run(self):
        """Run the download process in a separate thread"""
        try:
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            successful = 0
            failed = 0
            skipped = 0
            errors = []
            total_songs = len(self.df)
            
            for idx, row in self.df.iterrows():
                current_index = idx + 1
                # Check for cancellation
                if self.is_cancelled:
                    self.log_message.emit(f"[CANCELLED] Download cancelled by user (stopped at {current_index}/{total_songs})")
                    break
                
                song_name = row["Songname"].strip()
                youtube_link = row["Youtube link"].strip()
                
                # Create filename with zero-padded index
                file_number = str(current_index).zfill(6)
                filename = f"{file_number}_{self._sanitize_filename(song_name)}.m4a"
                output_file = output_path / filename
                
                # Check if file already exists
                if output_file.exists():
                    skipped += 1
                    self.log_message.emit(f"{current_index}/{total_songs} - {song_name} (skipped - already exists)")
                    # Update progress
                    self.progress_updated.emit(current_index, total_songs)
                    continue
                
                self.log_message.emit(f"{current_index}/{total_songs} - Downloading: {song_name}")
                
                try:
                    self._download_youtube_as_m4a(youtube_link, str(output_file), song_name)
                    successful += 1
                    self.log_message.emit(f"{current_index}/{total_songs} - {song_name} completed")
                except Exception as e:
                    failed += 1
                    error_msg = f"Failed to download '{song_name}': {str(e)}"
                    errors.append(error_msg)
                    self.log_message.emit(f"[ERROR] {current_index}/{total_songs} - {error_msg}")
                
                # Update progress
                self.progress_updated.emit(current_index, total_songs)
            
            # Emit finish signal
            self.download_finished.emit(successful, failed, errors)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def _download_youtube_as_m4a(self, youtube_url: str, output_path: str, song_name: str) -> None:
        """Download audio from a YouTube URL and save it as .m4a format"""
        output_base = output_path.replace(".m4a", "")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192',
            }],
            'outtmpl': output_base,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing/replacing invalid characters"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = filename.strip('. ')
        return filename

