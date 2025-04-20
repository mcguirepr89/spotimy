import os
import json
import html
from youtube_tools import YoutubeAPI, choose_or_create_youtube_playlist, add_tracks_to_youtube_playlist
from spotify_tools import authenticate_spotify, fetch_spotify_playlists, choose_spotify_playlist, fetch_tracks_from_playlist

RESUME_FILE = "resume.json"

def generate_html_with_links_and_embed(data, output_file="youtube_links.html"):
    tracks = data["tracks"]
    youtube_playlist_id = data.get("youtube_playlist_id")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n<title>Youtube Links</title>\n</head>\n<body>\n")
        f.write("<h1>YouTube Links</h1>\n<ul>\n")

        for track in tracks:
            if track.get("added"):  # Only include tracks that were added
                query = html.escape(track["track_info"])
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                f.write(f"<li><a href='{search_url}' target='_blank'>{query}</a></li>\n")

        f.write("</ul>\n")

        if youtube_playlist_id:
            f.write("<h2>Embedded YouTube Playlist</h2>\n")
            embed_url = f"https://www.youtube.com/embed/videoseries?list={youtube_playlist_id}"
            f.write(f"<iframe width='560' height='315' src='{embed_url}' frameborder='0' allowfullscreen></iframe>\n")

        f.write("</body>\n</html>\n")

def save_resume_file(tracks, playlist_name, resume_path):
    resume_data = {
        "playlist_name": playlist_name,
        "youtube_playlist_id": None,
        "tracks": [{"track_info": t, "added": False} for t in tracks]
    }
    with open(resume_path, "w") as f:
        json.dump(resume_data, f, indent=2)

def load_resume_file(resume_path):
    with open(resume_path) as f:
        return json.load(f)

def update_resume_file(resume_data, resume_path):
    with open(resume_path, "w") as f:
        json.dump(resume_data, f, indent=2)

def main():
    if os.path.exists(RESUME_FILE):
        print(f"\nFound existing {RESUME_FILE}. Resuming...")
        resume_data = load_resume_file(RESUME_FILE)
    else:
        sp = authenticate_spotify()
        playlists = fetch_spotify_playlists(sp)
        playlist_name, playlist_id = choose_spotify_playlist(playlists)

        tracks = fetch_tracks_from_playlist(sp, playlist_id)
        save_resume_file(tracks, playlist_name, RESUME_FILE)
        resume_data = load_resume_file(RESUME_FILE)

    yt_api = YoutubeAPI()
    
    if not resume_data["youtube_playlist_id"]:
        youtube_playlist_id = choose_or_create_youtube_playlist(yt_api, resume_data["playlist_name"])
        resume_data["youtube_playlist_id"] = youtube_playlist_id
        update_resume_file(resume_data, RESUME_FILE)
    else:
        youtube_playlist_id = resume_data["youtube_playlist_id"]

    add_tracks_to_youtube_playlist(resume_data, yt_api, youtube_playlist_id, RESUME_FILE)

    print("\n🎵 All tracks processed. Generating YouTube links page...")

    generate_html_with_links_and_embed(resume_data)

    print("\n✅ All done! 🎵")

if __name__ == "__main__":
    main()
