import os
import re
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    """Authenticate and return a YouTube API client using cached credentials."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def search_first_video(youtube, query):
    request = youtube.search().list(
        q=query,
        part="id",
        maxResults=1,
        type="video"
    )
    response = request.execute()
    if response["items"]:
        return response["items"][0]["id"]["videoId"]
    return None

def list_user_playlists(youtube):
    """Fetches and returns the user's existing playlists."""
    playlists = []
    request = youtube.playlists().list(
        part="snippet,status",
        mine=True,
        maxResults=50
    )
    while request:
        response = request.execute()
        playlists.extend(response.get("items", []))
        request = youtube.playlists().list_next(request, response)
    return playlists

def create_youtube_playlist(youtube, title, privacy_status="private"):
    """Creates a new YouTube playlist and returns its ID."""
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": "Created via Spotimy"},
            "status": {"privacyStatus": privacy_status}
        }
    )
    response = request.execute()
    print(f"✅ Created playlist: {title}")
    return response["id"]

def prompt_user_for_playlist(youtube):
    playlists = list_user_playlists(youtube)

    if playlists:
        print("\n📃 Existing YouTube Playlists:")
        for idx, p in enumerate(playlists, start=1):
            title = p.get("snippet", {}).get("title", "Untitled")
            status = p.get("status", {}).get("privacyStatus", "unknown")
            print(f"{idx}. {title} ({status})")
            print(f"{len(playlists)+1}. ➕ Create a new playlist")


    while True:
        try:
            choice = int(input("\nSelect a playlist or choose to create a new one: "))
            if 1 <= choice <= len(playlists):
                return playlists[choice - 1]["id"]
            elif choice == len(playlists) + 1:
                name = input("Enter new playlist name: ").strip()
                privacy = input("Visibility (public/unlisted/private): ").strip().lower()
                if privacy not in ["public", "unlisted", "private"]:
                    print("Invalid visibility, defaulting to 'private'.")
                    privacy = "private"
                return create_youtube_playlist(youtube, name, privacy)
            else:
                print("Invalid choice, try again.")
        except ValueError:
            print("Please enter a valid number.")

def add_video_to_playlist(youtube, playlist_id, video_id):
    request = youtube.playlistItems().insert(
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
    )
    request.execute()
    print(f"✅ Added video {video_id} to playlist {playlist_id}")

def clean_query(track_line):
    return re.sub(r'^\d+\.\s*', '', track_line)

def add_tracks_to_youtube_playlist(track_lines, playlist_id=None):
    youtube = get_authenticated_service()

    if not playlist_id:
        playlist_id = prompt_user_for_playlist(youtube)

    for track in track_lines:
        query = clean_query(track)
        video_id = search_first_video(youtube, query)
        if video_id:
            add_video_to_playlist(youtube, playlist_id, video_id)
        else:
            print(f"❌ No video found for: {query}")

    return playlist_id
