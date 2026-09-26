# tag-music-player

Play Spotify tracks and playlists on a Raspberry Pi from a link. Links will later come from NFC tags read by an RC522 reader.

The Pi runs [raspotify](https://github.com/dtcooper/raspotify), which makes it a Spotify Connect speaker. This app uses [spotipy](https://spotipy.readthedocs.io/) to tell Spotify what to play on that speaker. You need Spotify Premium.

## Setup

### 1. Make the Pi a Spotify speaker

```sh
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
```

Edit `/etc/raspotify/conf` and set the speaker name:

```sh
LIBRESPOT_NAME="tag-music-player"
```

Choose the audio output with `LIBRESPOT_DEVICE`. List the available devices with `aplay -L`.

| Output | Example |
| --- | --- |
| 3.5mm jack | `LIBRESPOT_DEVICE="hw:CARD=Headphones,DEV=0"` |
| HDMI | `LIBRESPOT_DEVICE="hw:CARD=vc4hdmi0,DEV=0"` |
| USB speaker / DAC | `LIBRESPOT_DEVICE="hw:CARD=<name from aplay -L>,DEV=0"` |
| Bluetooth | Pair it with `bluetoothctl`, install `bluez-alsa-utils`, then `LIBRESPOT_DEVICE="bluealsa:DEV=<MAC>,PROFILE=a2dp"` |

```sh
sudo systemctl restart raspotify
```

Open the Spotify app on a phone on the same network and pick **tag-music-player** as the speaker once. Raspotify caches the login, so after that the speaker is visible to the Web API.

### 2. Create a Spotify developer app

1. Go to https://developer.spotify.com/dashboard and create an app with the **Web API** enabled.
2. Add the redirect URI `http://127.0.0.1:8888/callback`.
3. Copy the client ID and client secret.

### 3. Install this project

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp .env.example .env   # then fill in the client ID and secret
```

`SPOTIFY_DEVICE_NAME` in `.env` must match `LIBRESPOT_NAME`.

## Usage

```sh
.venv/bin/tag-music-player                                          # plays the built-in demo track
.venv/bin/tag-music-player https://open.spotify.com/playlist/<id>   # any track, album, playlist, artist, episode or show
```

On the first run, the app prints a Spotify login URL. Open it in any browser and log in. The browser is then redirected to a `127.0.0.1` page that won't load; copy that page's full URL and paste it back into the terminal. The token is cached in `.cache-spotify`, so you only need to do this once.

## Tests

```sh
.venv/bin/pytest
```

## Design

- `media.py` parses Spotify URLs and URIs.
- `player.py` has the `Player` interface and `SpotifyPlayer`, which plays on the Connect device.
- `sources.py` has the `LinkSource` interface for anything that produces links. `StaticSource` covers the hard-coded or CLI link.
- `app.py` is the loop that sends each link from a source to the player.

To add the NFC reader, implement a `LinkSource` that yields the URL read from each tag and pass it to `TagMusicPlayer` in `__main__.py`.
