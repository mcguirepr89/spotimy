# Spotify to YouTube Playlist Converter 🎵➡️📺

A Python tool that helps you quickly convert a Spotify playlist into a YouTube playlist — and generates a beautiful, mobile-friendly HTML page with all your tracks and links.

Built with **Spotipy**, **Google API**, **TailwindCSS**, and lots of love. ❤️

---

## Features ✨

- 🔄 Convert a Spotify playlist into a YouTube playlist automatically
- 🌐 Generate an HTML page with:
  - Embedded YouTube playlist player
  - Link to the original Spotify playlist
  - Toggleable track list (show/hide)
  - Beautiful responsive design with dark mode
- 🌓 Dark mode support (follows system preferences)
- 📜 Simple, clean codebase with easy customization
- ⚡ Fast and lightweight, no server needed — just open the HTML file!

---

## Screenshots 📸

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/c9b3b0c0-3b83-42d9-a7e6-d0e2e7b80dac" alt="Screenshot 1" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/691f9138-6d61-4651-9dc4-262b118d88ab" alt="Screenshot 2" width="100%"></td>
  </tr>
</table>


---

## Requirements:
- A Spotify Premium account to create an app and access the Spotify WebAPI
- Goolge account to create an app and access the YouTube Data API v3

---

## Installation ⚙️

1. Clone the repository:
   ```bash
   git clone https://github.com/mcguirepr89/spotimy.git
   cd spotimy
   ```
1. Create a Spotify Developer App at Spotify Developer Dashboard
   1. [Create developer app on the dashboard](https://developer.spotify.com/dashboard).
   1. Add a Redirect URI `http://127.0.0.1:8888/callback` in the app settings.
   1. Copy your Client ID and Client Secret and put them in a `.env` file like so:

      `spotimy/.env`:    
      ```
      SPOTIFY_CLIENT_ID=mylongclientid
      SPOTIFY_CLIENT_SECRET=mylongclientsecret
      ```
1. Generate a YouTube Data API v3 key:
   1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
   1. Enable the YouTube Data API v3.
   1. Generate OAuth 2.0 credentials with `https://www.googleapis.com/auth/youtube.force-ssl` scope.
   1. Download your client credentials `JSON` file and rename it `client_secret.json`
  
1. Install dependencies in a virtual environment in the `spotimy` directory:
   1. ```bash
      python3 -m venv venv && source ./venv/bin/activate
      ```
   1. ```bash
      pip install -U pip && pip install -r requirements.txt
      ```

---

## Usage 🚀
```
usage: spotimy.py [-h] [--resume RESUME] [--generate-html] [--spotify-add SPOTIFY_ADD]

Spotify to YouTube playlist converter and web page creator.

options:
  -h, --help            show this help message and exit
  --resume RESUME       Path to a resume JSON file to continue a previous session.
  --generate-html       Generate an HTML page with links and optional embed.
  --spotify-add SPOTIFY_ADD
                        Path to file containing Spotify track IDs for adding to Spotify playlist.
```

Run the script interactively:

```bash
python spotimy.py
```

You will be prompted to:
- Choose a Spotify playlist
- Optionally create a YouTube playlist or select an existing one
- Export a mobile-friendly HTML page with embedded YouTube links

You can then open the generated `youtube_links.html` in any web browser!

OR resume from a previous conversion (see [Limitations](https://github.com/mcguirepr89/spotimy/blob/main/README.md#limitations) below for why this might be needed/helpful):
```bash
python spotimy.py --resume Spotify_playlist-to-Youtube_playlist.json
```

AND you can add tracks from a tracklist to a new or existing Spotify playlist (see [Hints](https://github.com/mcguirepr89/spotimy/blob/main/README.md#hints) below for tips on using this feature):
```bash
python spotimy.py --spotify-add ListOfSpotifyTrackIDs_OR_song_links.txt
```

---

## Technologies Used 🛠

- [Python 3](https://www.python.org/)
- [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/)
- [Google API Client Library for Python](https://googleapis.dev/python/google-api-core/latest/index.html)
- [Tailwind CSS](https://tailwindcss.com/)

---

## License 📄

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.


# Known bugs and limitations
### Bugs
Since this tool works by adding the first video from the YouTube search of format `Track Title - Artist Name (Album: Album Name)`, mistakes are bound to happen. One problem that seems to be pretty common is that "Full Album" videos get added when a song is also an album name.

Example: `Colour Green - Sibylle Baier (Album: Colour Green)` adds the video [Sibylle Baier - Colour Green (Full Album)](https://www.youtube.com/watch?v=8xVw7BEnkEI)

### Limitations
The API requests are limited. At the time of writing, (April 14th, 2025), I've only been able to convert 68 Spotify tracks into YouTube playlist items before hitting the API daily rate limit.

# Hints
Spotify deprecated being able to get the tracks from their currated playlists. This little javascript code snippet can be used to extract all of the `href` targets from the `<a>` tags when you open those playlist pages in your browser, zoom ALLLLL the way out so that every track is loaded and visible, and then dumping those into a file.

```
const trackLinks = Array.from(document.querySelectorAll('a'))
                        .map(a => a.getAttribute('href'))
                        .filter(href => href && href.includes('track'))
                        .map(href => href.split('/track/')[1]);

console.log(trackLinks.join('\n'));
```

Example workflow using Chrome:
1. Go to the playlist in the web browser.
1. Press `Ctrl` + `Shift` + `I` to enter the browser's web inspector.
1. Using the element explorer, highlight the `<div`> element that contains the playlist track listing and right click to "cut" it into your clipboard.
1. Delete the entire `<body>` element
1. Append (paste) the `<div>` from your clipboard.
1. Go to the web inspector's "Console" to paste the javascript snippet above.
1. Copy and paste the results into a text file.
