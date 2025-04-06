import os
import re
import urllib.parse
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    """Authenticate and return a YouTube API client."""
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def search_first_video(youtube, query):
    """Search for the first video result for a given query."""
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
    """Add a video to a YouTube playlist."""
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
    # Remove leading number and dot (e.g. "1. ")
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

if __name__ == "__main__":
    track_file = input("Enter the track list file path: ").strip()
    playlist_id = input("Enter your YouTube playlist ID: ").strip()
    
    if not os.path.exists(track_file):
        print("❌ Error: File not found.")
        exit(1)

    with open(track_file, "r", encoding="utf-8") as f:
        track_lines = [line.strip() for line in f.readlines() if line.strip()]

    add_tracks_to_youtube_playlist(track_lines, playlist_id)
