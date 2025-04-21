import os
import json
import argparse
import youtube_tools as yt
import generate_html as gh
from youtube_tools import update_resume_file
import spotify_tools as st

def save_resume_file(tracks, playlist_name, youtube_playlist_name, resume_path, spotify_playlist_url=None):
    resume_data = {
        "playlist_name": playlist_name,
        "spotify_playlist_url": spotify_playlist_url,
        "youtube_playlist_name": youtube_playlist_name,
        "youtube_playlist_id": None,
        "tracks": [{"track_info": t, "added": False} for t in tracks]
    }
    with open(resume_path, "w") as f:
        json.dump(resume_data, f, indent=2)

def load_resume_file(resume_path):
    with open(resume_path) as f:
        return json.load(f)

def sanitize_filename(name):
    """Make filenames safe."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

def main():
    about = "Spotify to YouTube playlist converter and web page creator."

    parser = argparse.ArgumentParser(
        description=about,
        epilog="See https://github.com/mcguirepr89/spotimy.git for more information"
    )
    parser.add_argument("--resume", help="Path to a resume JSON file to continue a previous session.")
    parser.add_argument("--generate-html", action="store_true", help="Generate an HTML page with links and optional embed.")
    args = parser.parse_args()

    if args.resume:
        if not os.path.exists(args.resume):
            print(f"❌ Resume file {args.resume} not found.")
            return
        print(f"\n📄 Resuming from {args.resume}...")
        resume_data = load_resume_file(args.resume)
        resume_file = args.resume
    else:
        sp = st.SpotifyAPI()
        playlists = sp.fetch_spotify_playlists()
        playlist_name, playlist_id, spotify_playlist_url = sp.choose_spotify_playlist(playlists)

        tracks = sp.fetch_tracks_from_playlist(playlist_id)

        yt_api = yt.YoutubeAPI()
        youtube_playlist_id = yt_api.choose_or_create_youtube_playlist(playlist_name)
        youtube_playlist_name = yt_api.get_youtube_playlist_name(youtube_playlist_id)


        resume_file_name = f"{sanitize_filename(playlist_name)}-to-{sanitize_filename(youtube_playlist_name)}.json"
        resume_file = resume_file_name

        save_resume_file(tracks, playlist_name, youtube_playlist_name, resume_file, spotify_playlist_url)

        resume_data = load_resume_file(resume_file)
        resume_data["youtube_playlist_id"] = youtube_playlist_id
        update_resume_file(resume_data, resume_file)

    yt_api = yt.YoutubeAPI()

    youtube_playlist_id = resume_data["youtube_playlist_id"]

    yt_api.add_tracks_to_youtube_playlist(resume_data, youtube_playlist_id, resume_file)

    print("\n🎵 All tracks processed!")

    all_added = all(t["added"] for t in resume_data["tracks"])

    generate_html = args.generate_html

    if not args.generate_html:
        # Interactive post-process
        if input("\n🌐 Would you like to generate the YouTube links HTML page? (y/N): ").lower().startswith('y'):
            generate_html = True

    if generate_html:
        print("\n🌐 Generating YouTube links page...")
        gh.generate_html_with_links_and_embed(resume_data)
        print("\n✅ HTML page created!")

    if all_added:
        if input("\n🧹 All tracks added. Delete the resume file? (y/N): ").lower().startswith('y'):
            os.remove(resume_file)
            print(f"🗑 Deleted {resume_file}")

if __name__ == "__main__":
    main()
