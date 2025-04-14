import os
import re
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
SCOPES = "playlist-read-private playlist-modify-private playlist-modify-public"

def get_spotify_client():
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=".cache"
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def get_user_playlists(sp):
    playlists = sp.current_user_playlists()
    if not playlists["items"]:
        print("No playlists found.")
        return None
    
    print("\nYour Playlists:")
    for idx, playlist in enumerate(playlists["items"], 1):
        print(f"{idx}. {playlist['name']} ({playlist['tracks']['total']} tracks)")
    print(f"{len(playlists['items']) + 1}. ➕ Create a new playlist")

    while True:
        try:
            choice = int(input("\nEnter the playlist number to use (0 to cancel): "))
            if choice == 0:
                return None
            if 1 <= choice <= len(playlists["items"]):
                return playlists["items"][choice - 1]
            elif choice == len(playlists["items"]) + 1:
                name = input("Enter new playlist name: ").strip()
                public = input("Make public? (y/n): ").strip().lower() == "y"
                new_playlist = sp.user_playlist_create(sp.me()["id"], name, public=public)
                print(f"✅ Created new playlist: {name}")
                return new_playlist
            print("Invalid choice, try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_playlist_tracks(sp, playlist_id):
    tracks = sp.playlist_tracks(playlist_id)
    if not tracks["items"]:
        print("No tracks found in this playlist.")
        return []

    track_lines = []
    print("\nTracks in Playlist:")
    for idx, item in enumerate(tracks["items"], 1):
        track = item["track"]
        if not track:
            continue
        track_info = f"{idx}. {track['name']} - {track['artists'][0]['name']} (Album: {track['album']['name']})"
        print(track_info)
        track_lines.append(track_info)
    return track_lines

def read_track_ids_from_file(filepath):
    track_ids = []
    pattern = re.compile(r"(?:spotify:track:|https://open\.spotify\.com/track/)?([A-Za-z0-9]{22})")

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            match = pattern.search(line)
            if match:
                track_ids.append(match.group(1))  # Extract the base62 ID
            else:
                print(f"⚠️ Skipping invalid line: {line}")

    return track_ids

def file_mode_flow(sp, filepath):
    track_ids = read_track_ids_from_file(filepath)
    if not track_ids:
        print("No valid track IDs found in the file.")
        return

    playlist = get_user_playlists(sp)
    if not playlist:
        print("No playlist selected. Exiting.")
        return

    confirm = input(f"\nAdd {len(track_ids)} track(s) to playlist '{playlist['name']}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Aborted. Exiting.")
        return

    sp.playlist_add_items(playlist["id"], track_ids)
    print(f"✅ Added {len(track_ids)} tracks to playlist '{playlist['name']}'.")

    # Continue with normal flow using the updated playlist
    track_lines = get_playlist_tracks(sp, playlist["id"])
    if not track_lines:
        print("No tracks found. Exiting.")
        return

    youtube_playlist_id = None
    if input("\nDo you want to create a YouTube playlist from these tracks? (y/n): ").strip().lower() == "y":
        try:
            youtube_playlist_id = add_tracks_to_youtube_playlist(track_lines, youtube_playlist_id)
        except Exception as e:
            print(f"\n⚠️ Failed to generate YouTube playlist: {e}")
            print("Continuing to generate YouTube-linked HTML file...\n")

    if input("\nDo you want to generate a YouTube-linked HTML file? (y/n): ").strip().lower() == "y":
        generate_html_from_tracks(track_lines, youtube_playlist_id)

def interactive_mode_flow(sp):
    playlist = get_user_playlists(sp)
    if not playlist:
        print("No playlist selected. Exiting.")
        return

    track_lines = get_playlist_tracks(sp, playlist["id"])
    if not track_lines:
        print("No tracks found. Exiting.")
        return

    youtube_playlist_id = None
    if input("\nDo you want to create a YouTube playlist from these tracks? (y/n): ").strip().lower() == "y":
        try:
            youtube_playlist_id = add_tracks_to_youtube_playlist(track_lines, youtube_playlist_id)
        except Exception as e:
            print(f"\n⚠️ Failed to generate YouTube playlist: {e}")
            print("Continuing to generate YouTube-linked HTML file...\n")

    if input("\nDo you want to generate a YouTube-linked HTML file? (y/n): ").strip().lower() == "y":
        generate_html_from_tracks(track_lines, youtube_playlist_id)

def main():
    sp = get_spotify_client()

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        filepath = sys.argv[1]
        file_mode_flow(sp, filepath)
    else:
        interactive_mode_flow(sp)

if __name__ == "__main__":
    main()
