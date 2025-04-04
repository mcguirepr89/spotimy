import os
import sys
import webbrowser
import requests
import spotipy
from youtube_link_generator import generate_html_from_tracks
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

load_dotenv()

# Load Spotify API Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"

# Scopes for access
SCOPES = "user-read-private user-read-email playlist-read-private"

# Authorization flow
class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        if "code" in query_components:
            self.server.auth_code = query_components["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authentication successful! You can close this window.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authentication failed!")

def get_auth_token():
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPES}"
    webbrowser.open(auth_url)
    
    server = HTTPServer(("localhost", 8888), AuthHandler)
    server.handle_request()
    auth_code = server.auth_code

    token_url = "https://accounts.spotify.com/api/token"
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    response = requests.post(token_url, data=token_data)
    return response.json().get("access_token")

# Initialize Spotify client
def get_spotify_client():
    token = get_auth_token()
    return spotipy.Spotify(auth=token)

# Fetch user profile
def get_user_profile(sp):
    user = sp.current_user()
    print(f"User: {user['display_name']} ({user['email']})")
    print(f"ID: {user['id']}")
    print(f"Country: {user['country']}")

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
                return playlists["items"][choice - 1]["id"]
            print("Invalid choice, please try again.")
        except ValueError:
            print("Please enter a valid number.")

# Fetch and display tracks from a playlist
def get_playlist_tracks(sp, playlist_id):
    tracks = sp.playlist_tracks(playlist_id)
    if not tracks["items"]:
        print("No tracks found in this playlist.")
        return

    track_lines = []
    print("\nTracks in Playlist:")
    for idx, item in enumerate(tracks["items"], 1):
        track = item["track"]
        track_info = f"{idx}. {track['name']} - {track['artists'][0]['name']} (Album: {track['album']['name']})"
        print(track_info)
        track_lines.append(track_info)

    # Ask if user wants to create the YouTube-linked HTML file
    create_html = input("\nDo you want to generate a YouTube-linked HTML file? (y/n): ").strip().lower()
    if create_html == "y":
        generate_html_from_tracks(track_lines)

# Search for a track
def search_track(sp, query):
    results = sp.search(q=query, type="track", limit=5)
    tracks = results["tracks"]["items"]
    if not tracks:
        print("No results found.")
        return
    print("\nSearch Results:")
    for idx, track in enumerate(tracks, 1):
        print(f"{idx}. {track['name']} - {track['artists'][0]['name']}")

# CLI Interface
def main():
    sp = get_spotify_client()
    
    while True:
        print("\nSpotify CLI:")
        print("1. Get User Profile")
        print("2. Get User Playlists & View Tracks")
        print("3. Search for a Track")
        print("4. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            get_user_profile(sp)
        elif choice == "2":
            playlist_id = get_user_playlists(sp)
            if playlist_id:
                get_playlist_tracks(sp, playlist_id)
        elif choice == "3":
            query = input("Enter track name: ")
            search_track(sp, query)
        elif choice == "4":
            print("Goodbye!")
            sys.exit()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
