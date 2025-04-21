import os
import json
import argparse

import spotify_tools as st
import youtube_tools as yt
import generate_html as gh
import utils

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
        resume_data = utils.load_json(args.resume)
        resume_file = args.resume
    else:
        sp = st.SpotifyAPI()
        playlists = sp.fetch_spotify_playlists()
        playlist_name, playlist_id, spotify_playlist_url = sp.choose_spotify_playlist(playlists)

        tracks = sp.fetch_tracks_from_playlist(playlist_id)

        yt_api = yt.YoutubeAPI()
        youtube_playlist_id = yt_api.choose_or_create_youtube_playlist(playlist_name)
        youtube_playlist_name = yt_api.get_youtube_playlist_name(youtube_playlist_id)

        resume_file = f"{utils.sanitize_filename(playlist_name)}-to-{utils.sanitize_filename(youtube_playlist_name)}.json"

        utils.save_resume_file(tracks, playlist_name, youtube_playlist_name, resume_file, spotify_playlist_url)

        resume_data = utils.load_json(resume_file)
        resume_data["youtube_playlist_id"] = youtube_playlist_id
        utils.update_resume_file(resume_data, resume_file)

    yt_api = yt.YoutubeAPI()
    youtube_playlist_id = resume_data["youtube_playlist_id"]
    yt_api.add_tracks_to_youtube_playlist(resume_data, youtube_playlist_id, resume_file)

    print("\n🎵 All tracks processed!")

    if should_generate_html(args):
        print("\n🌐 Generating YouTube links page...")
        gh.generate_html_with_links_and_embed(resume_data)
        print("\n✅ HTML page created!")

    if all(track["added"] for track in resume_data["tracks"]):
        if confirm("\n🧹 All tracks added. Delete the resume file? (y/N): "):
            os.remove(resume_file)
            print(f"🗑 Deleted {resume_file}")

def should_generate_html(args):
    if args.generate_html:
        return True
    return confirm("\n🌐 Would you like to generate the YouTube links HTML page? (y/N): ")

def confirm(prompt):
    return input(prompt).strip().lower() in ["y", "yes"]

if __name__ == "__main__":
    main()
