A simple tool to convert a Spotify playlist into a YouTube playlist. It also will create a simple TailwindCSS styled HTML page with a YouTube search link for each track.

Requirements:
- A Spotify Premium account to create an app and access the Spotify WebAPI
- Goolge account to create an app and access the YouTube Data API v3

# Setup steps:
1. Clone the repo:
   ```
   git clone https://github.com/mcguirepr89/spotimy.git
   ```
1. Create a Spotify Developer App at Spotify Developer Dashboard
   1. [Create developer app on the dashboard](https://developer.spotify.com/dashboard).
   1. Add a Redirect URI `http://127.0.0.1:8888/callback` in the app settings.
   1. Copy your Client ID and Client Secret and put them in a `.env` file like so:

      `spotimy/.env`:    
      ```
      CLIENT_ID=mylongclientid
      CLIENT_SECRET=mylongclientsecret
      ```
1. Generate a YouTube Data API v3 key:
   1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
   1. Enable the YouTube Data API v3.
   1. Generate OAuth 2.0 credentials with https://www.googleapis.com/auth/youtube.force-ssl scope.
   1. Download your client credentials `JSON` file and rename it `client_secrets.json`
  
1. Install dependencies in a virtual environment in the `spotimy` directory:
   1. `python3 -m venv venv && source ./venv/bin/activate`
   1. `pip install -U pip && pip install -r requirements.txt`

# Usage
  1. Run the script to grant your apps access to your Spotify and Google accounts.
  1. Answer the prompts according to what you want to do.

    

