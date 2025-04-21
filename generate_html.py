import html

def generate_html_with_links_and_embed(data, output_file="youtube_links.html"):
    tracks = data["tracks"]
    youtube_playlist_id = data.get("youtube_playlist_id")
    spotify_playlist_url = data.get("spotify_playlist_url")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html lang='en' class='dark'>\n<head>\n")
        f.write("<meta charset='UTF-8'>\n")
        f.write("<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
        f.write("<title>My Spotimy Page</title>\n")
        f.write('<script src="https://cdn.tailwindcss.com"></script>\n')
        f.write("""
<script>
    tailwind.config = {
        darkMode: 'class',
    }
</script>
""")
        f.write("</head>\n<body class='bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200 min-h-screen'>\n")

        f.write("<div class='max-w-4xl mx-auto p-6'>\n")
        f.write("<h1 class='text-3xl font-bold mb-6 text-center'>My Spotimy Page</h1>\n")

        if youtube_playlist_id:
            embed_url = f"https://www.youtube.com/embed/videoseries?list={youtube_playlist_id}"
            f.write(f"<div class='mb-8 flex justify-center'>\n")
            f.write(f"<iframe class='w-full h-64 sm:h-96 rounded-lg shadow-lg' src='{embed_url}' frameborder='0' allowfullscreen></iframe>\n")
            f.write("</div>\n")

        if spotify_playlist_url:
            f.write(f"<div class='text-center mb-8'>\n")
            f.write(f"<a href='{html.escape(spotify_playlist_url)}' target='_blank' class='text-blue-500 hover:underline text-lg'>View Original Spotify Playlist</a>\n")
            f.write("</div>\n")

        # Toggle Button
        f.write("""
<div class="text-center mb-6">
    <button id="toggleButton" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition">
        Show Tracks
    </button>
</div>
""")

        # Hidden Track List
        f.write("""
<div id="trackList" class="hidden text-center space-y-4 transition-all duration-500 ease-in-out">
<ul>
""")
        for track in tracks:
            if track.get("added"):
                query = html.escape(track["track_info"])
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                f.write(f"<li class='bg-white dark:bg-gray-800 p-4 rounded-lg shadow hover:bg-gray-100 dark:hover:bg-gray-700 transition'>")
                f.write(f"<a href='{search_url}' target='_blank' class='text-blue-600 dark:text-blue-400 hover:underline'>{query}</a>")
                f.write("</li>\n")
        f.write("</ul>\n</div>\n")  # close trackList div

        f.write("""
<div class="text-center mb-6">
    <span>Webpage created with</span><a href="https://github.com/mcguirepr89/spotimy" target='_blank' class="text-blue-500 hover:underline text-lg">
        Spotimy
    </a>
</div>
""")

        f.write("</div>\n")  # close main container

        # JavaScript for toggle behavior
        f.write("""
<script>
    const toggleButton = document.getElementById('toggleButton');
    const trackList = document.getElementById('trackList');

    toggleButton.addEventListener('click', () => {
        if (trackList.classList.contains('hidden')) {
            trackList.classList.remove('hidden');
            toggleButton.textContent = 'Hide Tracks';
        } else {
            trackList.classList.add('hidden');
            toggleButton.textContent = 'Show Tracks';
        }
    });
</script>
""")

        f.write("</body>\n</html>\n")
