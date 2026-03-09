from dataclasses import dataclass

@dataclass
class Song:
    index: int
    name: str
    artist: str
    length: str
    youtube_link: str
    spotify_link: str
