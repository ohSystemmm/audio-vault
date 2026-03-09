import os
import sys
import re
import yt_dlp

SONGS_DIR = "songs"

def _make_filename(song):
    """Build the padded filename: 00001_Song-name_Artist-name.m4a"""
    idx = str(song.index).zfill(5)

    def slugify(text):
        # Replace spaces with hyphens, strip non-alphanumeric/hyphen chars
        text = text.strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s]+', '-', text)
        return text

    safe_name   = slugify(song.name)
    safe_artist = slugify(song.artist)
    return os.path.join(SONGS_DIR, f"{idx}_{safe_name}_{safe_artist}.m4a")

def search_youtube(query):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)
            if 'entries' in result:
                return [{"title": entry.get('title'), "channel": entry.get('uploader'), "url": entry.get('url')} for entry in result['entries'][:5]]
        except Exception as e:
            print(f"Error searching youtube: {e}", file=sys.stderr)
    return []

def download_all_youtube_audio(songs):
    os.makedirs(SONGS_DIR, exist_ok=True)
    print(f"\n--- Starting YouTube Audio Downloads (output: {SONGS_DIR}/) ---")

    for song in songs:
        if not song.youtube_link or song.youtube_link.lower() == "ignore":
            continue

        filename = _make_filename(song)

        if os.path.exists(filename):
            print(f"Skipping '{os.path.basename(filename)}' (Already exists)")
            continue

        print(f"Downloading {os.path.basename(filename)}...")
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': filename,
            'quiet': False,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([song.youtube_link])
            print(f"  [Success] Saved.")
        except Exception as e:
            # Remove partial file if it exists
            if os.path.exists(filename):
                os.remove(filename)
            print(f"\n  [Error] Download failed for '{os.path.basename(filename)}': {e}")
            print("  Stopping downloads.")
            return

    # Cleanup unreferenced files
    print("\n--- Cleaning up unreferenced audio files ---")
    valid_filenames = set()
    for song in songs:
        if not song.youtube_link or song.youtube_link.lower() == "ignore":
            continue
        valid_filenames.add(os.path.basename(_make_filename(song)))

    if os.path.isdir(SONGS_DIR):
        for f in os.listdir(SONGS_DIR):
            if f.endswith(".m4a") and f not in valid_filenames:
                try:
                    os.remove(os.path.join(SONGS_DIR, f))
                    print(f"  Removed unreferenced file: {f}")
                except Exception as e:
                    print(f"  Failed to remove '{f}': {e}")

    print("--- Downloads & Cleanup Complete ---")
