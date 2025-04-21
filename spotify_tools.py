import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-read-private playlist-modify-private playlist-modify-public"

def authenticate_spotify():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    ))

def fetch_spotify_playlists(sp):
    playlists = sp.current_user_playlists()["items"]
    return [(pl["name"], pl["id"]) for pl in playlists]

def choose_spotify_playlist(playlists):
    print("\nSpotify Playlists:")
    for idx, (name, _) in enumerate(playlists):
        print(f"{idx + 1}: {name}")
    choice = int(input("Select a playlist by number: ")) - 1
    selected_playlist = playlists[choice]
    playlist_name, playlist_id = selected_playlist
    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
    return playlist_name, playlist_id, playlist_url

#def choose_spotify_playlist(playlists):
#    print("\nSpotify Playlists:")
#    for idx, (name, _) in enumerate(playlists):
#        print(f"{idx + 1}: {name}")
#    choice = int(input("Select a playlist by number: ")) - 1
#    return playlists[choice]

def fetch_tracks_from_playlist(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results["items"]:
            track = item["track"]
            if track:
                track_info = f"{track['name']} - {track['artists'][0]['name']}"
                tracks.append(track_info)
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return tracks
