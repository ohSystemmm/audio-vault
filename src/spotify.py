import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from dotenv import load_dotenv

def get_client(interactive=False):
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8081/callback")
    
    if not client_id or client_id == "your_spotify_client_id_here":
        client_id = input("\nEnter your Spotify Client ID (from developer.spotify.com): ").strip()
        
    if not client_secret or client_secret == "your_spotify_client_secret_here":
        client_secret = input("Enter your Spotify Client Secret: ").strip()
        
    if not client_id or not client_secret:
        raise ValueError("Spotify Client ID and Secret are required to use the Spotify API.")
    if interactive:
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="playlist-modify-public playlist-modify-private",
            open_browser=True
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    else:
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        return spotipy.Spotify(auth_manager=auth_manager)

def search_spotify(query):
    try:
        sp = get_client(interactive=False)
        results = sp.search(q=query, limit=5, type='track')
        items = results.get('tracks', {}).get('items', [])
        suggestions = []
        for item in items:
            artist = item['artists'][0]['name'] if item.get('artists') else "Unknown"
            url = item.get('external_urls', {}).get('spotify', '')
            suggestions.append({"name": item.get('name'), "artist": artist, "url": url})
        return suggestions
    except Exception as e:
        print(f"Spotify search failed: {e}")
        return []

def extract_id(url):
    if "track/" in url:
        return url.split("track/")[1].split("?")[0]
    if url.startswith("spotify:track:"):
        return url.replace("spotify:track:", "")
    return url

def _extract_playlist_id(link):
    if "playlist/" in link:
        return link.split("playlist/")[1].split("?")[0]
    if link.startswith("spotify:playlist:"):
        return link.replace("spotify:playlist:", "")
    return link  # assume raw ID

def fetch_playlist_tracks(playlist_link):
    """Fetch all tracks from a public Spotify playlist. Returns a list of dicts with name, artist, duration_ms, spotify_url."""
    playlist_id = _extract_playlist_id(playlist_link)
    try:
        sp = get_client(interactive=False)
    except Exception as e:
        print(f"Spotify auth error: {e}")
        return []

    tracks = []
    try:
        results = sp.playlist_items(playlist_id, fields="items(track(name,artists,duration_ms,external_urls)),next", limit=100)
        while True:
            for item in results['items']:
                track = item.get('track')
                if not track:
                    continue
                name = track.get('name', 'Unknown')
                artist = track['artists'][0]['name'] if track.get('artists') else 'Unknown'
                duration_ms = track.get('duration_ms', 0)
                # Convert ms → M:SS
                total_seconds = duration_ms // 1000
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                duration_str = f"{minutes}:{seconds:02d}"
                spotify_url = track.get('external_urls', {}).get('spotify', '')
                tracks.append({
                    'name': name,
                    'artist': artist,
                    'duration': duration_str,
                    'spotify_url': spotify_url,
                })
            if results.get('next'):
                results = sp.next(results)
            else:
                break
    except Exception as e:
        print(f"Error fetching playlist: {e}")

    return tracks

def sync_spotify_playlist(songs):
    load_dotenv()
    playlist_id_raw = os.getenv("SPOTIFY_PLAYLIST_ID")
    
    # Check if empty, or if it's strictly the template placeholder
    if not playlist_id_raw or playlist_id_raw == "your_spotify_playlist_id_here":
        link = input("\nEnter Spotify Playlist Link (or ID): ").strip()
        if not link:
            print("Operation cancelled: No playlist link provided.")
            return
        
        # Extract ID from a potential full URL like https://open.spotify.com/playlist/7xI8d8X3Uo42YyxyYt554s
        if "playlist/" in link:
            playlist_id_raw = link.split("playlist/")[1].split("?")[0]
        elif link.startswith("spotify:playlist:"):
            playlist_id_raw = link.replace("spotify:playlist:", "")
        else:
            playlist_id_raw = link # Assume they pasted an ID directly

    try:
        sp = get_client(interactive=True)
        playlist = sp.playlist(playlist_id_raw)
        print(f"\n--- Syncing Spotify Playlist: {playlist['name']} ---")
    except Exception as e:
        print(f"Failed to fetch playlist: {e}")
        return

    # Desired tracks
    desired_ids = []
    for song in songs:
        if song.spotify_link and song.spotify_link.lower() != "ignore":
            tid = extract_id(song.spotify_link)
            if tid:
                desired_ids.append(tid)

    print(f"Mirroring {len(desired_ids)} tracks from Excel to Spotify...")
    if not desired_ids:
        try:
            sp.playlist_replace_items(playlist_id_raw, [])
            print("Playlist has been cleared.")
        except Exception as e:
            print(f"Failed to clear playlist: {e}")
        return

    try:
        sp.playlist_replace_items(playlist_id_raw, desired_ids[:100])
        for i in range(100, len(desired_ids), 100):
            sp.playlist_add_items(playlist_id_raw, desired_ids[i:i+100])
        print("Sync Complete. The Spotify playlist now perfectly mirrors the Excel file.")
    except Exception as e:
        print(f"Error during synchronization: {e}")
