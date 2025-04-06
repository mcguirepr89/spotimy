import os
import sys
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from youtube_link_generator import generate_html_from_tracks
from youtube_playlist_adder import add_tracks_to_youtube_playlist

load_dotenv()

# Load Spotify API credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Scopes for access
SCOPES = "playlist-read-private"

# Get Spotify client using persistent token cache
def get_spotify_client():
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=".cache"
    )
    return spotipy.Spotify(auth_manager=auth_manager)

# Fetch user playlists and allow selection
def get_user_playlists(sp):
    playlists = sp.current_user_playlists()
    if not playlists["items"]:
        print("No playlists found.")
        return None
    
    print("\nYour Playlists:")
    for idx, playlist in enumerate(playlists["items"], 1):
        print(f"{idx}. {playlist['name']} ({playlist['tracks']['total']} tracks)")

    while True:
        try:
            choice = int(input("\nEnter the playlist number to view its tracks (0 to cancel): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(playlists["items"]):
                return playlists["items"][choice - 1]
            print("Invalid choice, please try again.")
        except ValueError:
            print("Please enter a valid number.")

# Fetch and display tracks from a playlist
def get_playlist_tracks(sp, playlist_id):
    tracks = sp.playlist_tracks(playlist_id)
    if not tracks["items"]:
        print("No tracks found in this playlist.")
        return []

    track_lines = []
    print("\nTracks in Playlist:")
    for idx, item in enumerate(tracks["items"], 1):
        track = item["track"]
        track_info = f"{idx}. {track['name']} - {track['artists'][0]['name']} (Album: {track['album']['name']})"
        print(track_info)
        track_lines.append(track_info)
    return track_lines

# Main flow
def main():
    sp = get_spotify_client()

    playlist = get_user_playlists(sp)
    if not playlist:
        print("No playlist selected. Exiting.")
        return

    track_lines = get_playlist_tracks(sp, playlist["id"])
    if not track_lines:
        print("No tracks found. Exiting.")
        return

    # Ask if user wants to create a YouTube playlist
    youtube_playlist_id = None
    if input("\nDo you want to create a YouTube playlist from these tracks? (y/n): ").strip().lower() == "y":
        youtube_playlist_id = input("Enter your YouTube playlist ID: ").strip()
        try:
            add_tracks_to_youtube_playlist(track_lines, youtube_playlist_id)
        except Exception as e:
            print(f"\n⚠️ Failed to generate YouTube playlist: {e}")
            print("Continuing to generate YouTube-linked HTML file...\n")

    # Ask if user wants to generate HTML with YouTube search links
    if input("\nDo you want to generate a YouTube-linked HTML file? (y/n): ").strip().lower() == "y":
        generate_html_from_tracks(track_lines, youtube_playlist_id)

if __name__ == "__main__":
    main()
