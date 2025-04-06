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

def add_tracks_to_youtube_playlist(track_lines, playlist_id):
    youtube = get_authenticated_service()
    for track in track_lines:
        query = clean_query(track)
        video_id = search_first_video(youtube, query)
        if video_id:
            add_video_to_playlist(youtube, playlist_id, video_id)
        else:
            print(f"❌ No video found for: {query}")
