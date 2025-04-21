import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

class SpotifyAPI:
    def __init__(self):
        load_dotenv()
        self.spotify = self.authenticate_spotify()

    def authenticate_spotify(self):
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="playlist-read-private playlist-modify-private playlist-modify-public"
        ))
    
    def fetch_spotify_playlists(self):
        playlists = self.spotify.current_user_playlists()["items"]
        return [(pl["name"], pl["id"]) for pl in playlists]
    
    def choose_spotify_playlist(self, playlists):
        print("\nSpotify Playlists:")
        for idx, (name, _) in enumerate(playlists):
            print(f"{idx + 1}: {name}")

        while True:
            try:
                choice = int(input("Select a playlist by number: ")) - 1
                if 0 <= choice < len(playlists):
                    playlist_name, playlist_id = playlists[choice]
                    playlist_url = f"https://open.spotify.com/playlist/{playlist_id}"
                    return playlist_name, playlist_id, playlist_url
                else:
                    print("❗ Invalid choice. Try again.")
            except (ValueError, IndexError):
                print("❗ Please enter a valid number.")

    def fetch_tracks_from_playlist(self, playlist_id):
        tracks = []
        results = self.spotify.playlist_tracks(playlist_id)
        while results:
            for item in results["items"]:
                track = item["track"]
                if track:
                    track_info = f"{track['name']} - {track['artists'][0]['name']}"
                    tracks.append(track_info)
            if results.get("next"):
                results = self.spotify.next(results)
            else:
                break
        return tracks
