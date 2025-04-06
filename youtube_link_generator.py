import os
import re
import urllib.parse

TAILWIND_CSS_CDN = "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"

def format_search_query(track_line):
    """Converts a track line into a YouTube search URL."""
    track_line = re.sub(r"^\d+\.\s*", "", track_line)
    query = urllib.parse.quote_plus(track_line)
    return f"https://www.youtube.com/results?search_query={query}"

def generate_html_from_tracks(track_lines, youtube_playlist_id=None, output_file="youtube_links.html"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Links</title>
    <script src="{TAILWIND_CSS_CDN}"></script>
</head>
<body class="bg-gray-900 text-white p-6">
    <div class="max-w-3xl mx-auto">
""")

        if youtube_playlist_id:
            f.write(f"""        <h1 class="text-3xl font-bold mb-4 text-center">YouTube Playlist</h1>
        <div class="relative w-full" style="padding-top: 56.25%;">
            <iframe class="absolute top-0 left-0 w-full h-full"
                    src="https://www.youtube.com/embed/videoseries?list={youtube_playlist_id}"
                    title="YouTube video player"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    referrerpolicy="strict-origin-when-cross-origin"
                    allowfullscreen>
            </iframe>
        </div>\n\n""")

        f.write("""        <h1 class="text-3xl font-bold mb-4 text-center pt-6">YouTube Search Links</h1>
        <ul class="list-disc pl-6 space-y-2">
""")

        for track in track_lines:
            if not track.strip():
                continue
            youtube_url = format_search_query(track)
            f.write(f'            <li><a href="{youtube_url}" class="text-blue-400 hover:underline" target="_blank">{track}</a></li>\n')

        f.write("""        </ul>
    <br>
    <h3 class="text-3xl font-bold mb-4 text-center "><a class="hover:text-blue-400 hover:underline" href="https://github.com/mcguirepr89/spotimy" target="_blank">Source Code</a></h3>
    </div>
</body>
</html>""")

    print(f"\n✅ HTML file generated: {output_file}")
