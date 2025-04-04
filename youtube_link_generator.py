import os
import re
import urllib.parse

TAILWIND_CSS_CDN = "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"

def format_search_query(track_line):
    """Converts a track line into a YouTube search URL."""
    track_line = re.sub(r"^\d+\.\s*", "", track_line)  # Remove leading numbers
    query = urllib.parse.quote_plus(track_line)
    return f"https://www.youtube.com/results?search_query={query}"

def generate_html_from_tracks(track_lines, output_file="youtube_links.html"):
    """Generates an HTML file with clickable YouTube search links."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Links</title>
    <link href="{TAILWIND_CSS_CDN}" rel="stylesheet">
</head>
<body class="bg-gray-900 text-white p-6">
    <div class="max-w-3xl mx-auto">
        <h1 class="text-3xl font-bold mb-4">YouTube Search Links</h1>
        <ul class="list-disc pl-6 space-y-2">
""")
        for track in track_lines:
            if not track.strip():
                continue  # Skip empty lines
            youtube_url = format_search_query(track)
            f.write(f'            <li><a href="{youtube_url}" class="text-blue-400 hover:underline" target="_blank">{track}</a></li>\n')

        f.write("""        </ul>
    </div>
</body>
</html>""")

    print(f"\n✅ HTML file generated: {output_file}")

if __name__ == "__main__":
    input_file = input("Enter the track list file path: ").strip()
    if not os.path.exists(input_file):
        print("❌ Error: File not found.")
        exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        track_lines = f.readlines()

    generate_html_from_tracks(track_lines)
