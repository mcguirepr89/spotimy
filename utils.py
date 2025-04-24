import json
import re

def sanitize_filename(name):
    """Make filenames safe for saving."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

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

def load_json(path):
    with open(path) as f:
        return json.load(f)

def update_resume_file(resume_data, resume_path):
    with open(resume_path, "w") as f:
        json.dump(resume_data, f, indent=2)

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
