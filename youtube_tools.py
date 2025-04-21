import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests
from google.oauth2.credentials import Credentials

class YoutubeAPI:
    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client_secrets_file = "client_secret.json"
        self.youtube = self.authenticate_youtube()

    def authenticate_youtube(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes
                )
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=creds
        )

    def search_and_add_video(self, query, playlist_id):
        try:
            search_response = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=1
            ).execute()

            items = search_response.get("items", [])
            if not items:
                print(f"No results found for '{query}'")
                return False

            video_id = items[0]["id"]["videoId"]

            self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()

            return True

        except Exception as e:
            print(f"Error adding video: {e}")
            return False

    def choose_or_create_youtube_playlist(self, default_name):
        playlists = self.youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50
        ).execute()

        existing_playlists = {idx + 1: (item["snippet"]["title"], item["id"]) 
                              for idx, item in enumerate(playlists.get("items", []))}

        print("\nYour YouTube Playlists:")
        for idx, (title, _) in existing_playlists.items():
            print(f"{idx}: {title}")

        choice = input("\nSelect a playlist number, or press Enter to create a new one: ")

        if choice.strip() == "":
            name = input(f"Enter a new playlist name (default: {default_name}): ").strip() or default_name
            visibility = input("Visibility (public/private/unlisted)? [private]: ").strip().lower()
            if visibility not in ["public", "unlisted"]:
                visibility = "private"

            playlist = self.youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {"title": name},
                    "status": {"privacyStatus": visibility}
                }
            ).execute()

            return playlist["id"]
        else:
            try:
                selected_idx = int(choice)
                return existing_playlists[selected_idx][1]
            except (ValueError, KeyError):
                print("❗ Invalid choice. Exiting.")
                exit(1)

    def add_tracks_to_youtube_playlist(self, resume_data, youtube_playlist_id, resume_path):
        for idx, track_entry in enumerate(resume_data["tracks"]):
            if track_entry["added"]:
                continue

            query = track_entry["track_info"]
            print(f"\nSearching and adding: {query}")

            success = self.search_and_add_video(query, youtube_playlist_id)

            if success:
                print(f"✔ Added: {query}")
                resume_data["tracks"][idx]["added"] = True
                import utils
                utils.update_resume_file(resume_data, resume_path)
            else:
                print(f"✖ Failed: {query}")

    def get_youtube_playlist_name(self, playlist_id):
        playlist = self.youtube.playlists().list(
            part="snippet",
            id=playlist_id
        ).execute()
        items = playlist.get("items", [])
        if items:
            return items[0]["snippet"]["title"]
        return "YouTubePlaylist"
