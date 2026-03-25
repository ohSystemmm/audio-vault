import yt_dlp
from pathlib import Path
from typing import List, Tuple, Optional, Callable
import os


def download_songs(df, output_dir: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[int, int, List[str]]:
    """
    Download songs from YouTube links provided in a DataFrame.
    
    Args:
        df: DataFrame with 'Songname' and 'Youtube link' columns
        output_dir: Directory to save downloaded files
        progress_callback: Optional callback function(current, total) to track progress
        
    Returns:
        Tuple of (successful_downloads, failed_downloads, list of error messages)
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = 0
    errors = []
    total_songs = len(df)
    
    for idx, row in df.iterrows():
        song_name = row["Songname"].strip()
        youtube_link = row["Youtube link"].strip()
        
        # Create filename with zero-padded index
        file_number = str(idx + 1).zfill(6)  # 000001, 000002, etc.
        filename = f"{file_number}_{_sanitize_filename(song_name)}.m4a"
        output_file = output_path / filename
        
        try:
            _download_youtube_as_m4a(youtube_link, str(output_file), song_name)
            successful += 1
        except Exception as e:
            failed += 1
            error_msg = f"Failed to download '{song_name}': {str(e)}"
            errors.append(error_msg)
        
        # Call progress callback if provided
        if progress_callback:
            progress_callback(successful + failed, total_songs)
    
    return successful, failed, errors


def _download_youtube_as_m4a(youtube_url: str, output_path: str, song_name: str) -> None:
    """
    Download audio from a YouTube URL and save it as .m4a format.
    
    Args:
        youtube_url: YouTube video URL
        output_path: Full path where the file should be saved (including filename)
        song_name: Name of the song (for logging purposes)
        
    Raises:
        Exception: If download fails
    """
    # Remove file extension from output path since yt-dlp adds it
    output_base = output_path.replace(".m4a", "")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192',
        }],
        'outtmpl': output_base,
        'quiet': False,
        'no_warnings': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for use in file systems
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    return filename
