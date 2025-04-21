import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

class SpotifyAPI:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        self.scope = "playlist-read-private playlist-modify-private playlist-modify-public"
        self.spotify = self.authenticate_spotify()

    def authenticate_spotify(self):
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        ))
    
    def fetch_spotify_playlists(self):
        playlists = self.spotify.current_user_playlists()["items"]
        return [(pl["name"], pl["id"]) for pl in playlists]
    
    def choose_spotify_playlist(self, playlists):
        print("\nSpotify Playlists:")
        for idx, (name, _) in enumerate(playlists):
            print(f"{idx + 1}: {name}")
        choice = int(input("Select a playlist by number: ")) - 1
        selected_playlist = playlists[choice]
        playlist_name, playlist_id = selected_playlist
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
        return playlist_name, playlist_id, playlist_url
    
    def fetch_tracks_from_playlist(self, playlist_id):
        tracks = []
        results = self.spotify.playlist_tracks(playlist_id)
        while results:
            for item in results["items"]:
                track = item["track"]
                if track:
                    track_info = f"{track['name']} - {track['artists'][0]['name']}"
                    tracks.append(track_info)
            if results["next"]:
                results = self.next(results)
            else:
                break
        return tracks
