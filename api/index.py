from flask import Flask
from base64 import b64encode
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS

load_dotenv(find_dotenv())

import requests, os, random

SPOTIFY_URL_REFRESH_TOKEN = "https://accounts.spotify.com/api/token"
SPOTIFY_URL_NOW_PLAYING = "https://api.spotify.com/v1/me/player/currently-playing"
SPOTIFY_URL_RECENTLY_PLAY = "https://api.spotify.com/v1/me/player/recently-played?limit=10"

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET_ID = os.environ.get("SPOTIFY_SECRET_ID")
SPOTIFY_REFRESH_TOKEN = os.environ.get("SPOTIFY_REFRESH_TOKEN")


app = Flask(__name__, template_folder="components")

cors = CORS(
    app,
    resources={r"*": {"origins": ["*"]}},
)


def getAuth():
    return b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}".encode()).decode("ascii")


def refreshToken():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": SPOTIFY_REFRESH_TOKEN,
    }

    headers = {"Authorization": "Basic {}".format(getAuth())}

    response = requests.post(SPOTIFY_URL_REFRESH_TOKEN, data=data, headers=headers)
    return response.json()["access_token"]


def recentlyPlayed():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(SPOTIFY_URL_RECENTLY_PLAY, headers=headers)

    if response.status_code == 204:
        return {}

    return response.json()


def nowPlaying():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(SPOTIFY_URL_NOW_PLAYING, headers=headers)

    if response.status_code == 204:
        return {}

    return response.json()














def setSpotifyObjectV2(item):
    musicLink = item["album"]["external_urls"]
    artistName = item["artists"][0]["name"].replace("&", "&amp;")
    songName = item["name"].replace("&", "&amp;")

    spotifyObject = {
        "artistName": artistName,
        "songName": songName,
        "albumCover": item["album"]["images"][0]["url"],
        "musicLink": musicLink
    }
    return spotifyObject



@app.route("/v2")
def catch_all_v2():
    data = nowPlaying()

    if data == {}:
        recent_plays = recentlyPlayed()
        size_recent_play = len(recent_plays["items"])
        idx = random.randint(0, size_recent_play - 1)
        item = recent_plays["items"][idx]["track"]
    else:
        item = data["item"]

    return setSpotifyObjectV2(item)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    print(os.environ)
    return "ok", 200


if __name__ == "__main__":
    app.run()
