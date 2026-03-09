import sys
from src.excel import load_and_validate, create_excel_from_tracks
from src.youtube import download_all_youtube_audio
from src.spotify import sync_spotify_playlist, fetch_playlist_tracks

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path-to-excel-file>")
        sys.exit(1)

    filename = sys.argv[1]

    while True:
        print("\n=== Audio Vault ===")
        print("1 - Load Excel and Download YouTube Audio")
        print("2 - Load Excel and Sync Spotify Playlist")
        print("3 - Create Excel from Spotify Playlist")
        print("4 - Exit")
        try:
            opt = input("Select an option: ").strip()
        except EOFError:
            break

        if opt == "1":
            print(f"\nLoading music data from {filename}...")
            songs = load_and_validate(filename)
            if songs is None:
                print("Failed to load Excel file.")
                continue
            print(f"Total songs loaded: {len(songs)}")
            try:
                download_all_youtube_audio(songs)
            except Exception as e:
                print(f"Downloads failed: {e}")

        elif opt == "2":
            print(f"\nLoading music data from {filename}...")
            songs = load_and_validate(filename)
            if songs is None:
                print("Failed to load Excel file.")
                continue
            print(f"Total songs loaded: {len(songs)}")
            try:
                sync_spotify_playlist(songs)
            except Exception as e:
                print(f"Sync failed: {e}")

        elif opt == "3":
            link = input("\nEnter Spotify Playlist Link: ").strip()
            if not link:
                print("No link provided.")
                continue
            out = input(f"Save Excel as (default: {filename}): ").strip()
            if not out:
                out = filename
            print("Fetching tracks from Spotify...")
            tracks = fetch_playlist_tracks(link)
            if not tracks:
                print("No tracks found or an error occurred.")
                continue
            print(f"Found {len(tracks)} tracks. Writing to {out}...")
            create_excel_from_tracks(out, tracks)

        elif opt == "4":
            print("Exiting.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
