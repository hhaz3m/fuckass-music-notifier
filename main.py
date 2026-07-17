import requests
import threading, time, json, os
import xml.etree.ElementTree as ET
from flask import Flask, jsonify
from yt_dlp import YoutubeDL
import uuid
import base64
INSTANCE_ID = str(uuid.uuid4())
print("Instance ID:", INSTANCE_ID)

# =====================
# CONFIG
# =====================
SOUNDCLOUD_USERS = [
    "https://feeds.soundcloud.com/users/soundcloud:users:871836190/sounds.rss", # asteria
    "https://feeds.soundcloud.com/users/soundcloud:users:1522578684/sounds.rss", # an4rch (asteria archive)
    "https://feeds.soundcloud.com/users/soundcloud:users:277600140/sounds.rss", # lytra
    "https://feeds.soundcloud.com/users/soundcloud:users:1481050799/sounds.rss", # (used to be) lychives
    "https://feeds.soundcloud.com/users/soundcloud:users:671246480/sounds.rss", # vyzer
    "https://feeds.soundcloud.com/users/soundcloud:users:1014983476/sounds.rss", # vychives
    "https://feeds.soundcloud.com/users/soundcloud:users:1153776793/sounds.rss", # kets4eki
    "https://feeds.soundcloud.com/users/soundcloud:users:1200417373/sounds.rss", # kets2eki (kets archive)
    "https://feeds.soundcloud.com/users/soundcloud:users:1122731785/sounds.rss", # d3r
    "https://feeds.soundcloud.com/users/soundcloud:users:1221437284/sounds.rss", # despised
    "https://feeds.soundcloud.com/users/soundcloud:users:523819995/sounds.rss", # 6arelyhuman
    "https://feeds.soundcloud.com/users/soundcloud:users:1353863904/sounds.rss", # anarchist sanctuary (remixes)
    "https://feeds.soundcloud.com/users/soundcloud:users:1671149930/sounds.rss", # anarchist sanctuary (distributor)
    "https://feeds.soundcloud.com/users/soundcloud:users:1478512195/sounds.rss", # anarchist sanctuary (songs)
    "https://feeds.soundcloud.com/users/soundcloud:users:1221718432/sounds.rss", # archive
]
YOUTUBE_USERS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCMvmRb3dal_aGxmhTVeRCdw",  # asteria main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCJMm3-iHCoqaWkr_Q5_E8UA",  # asteria topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCOkqU6zsc_yxKFj5X1-O9HQ",  # an4rch topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCeSYZhLKq-L9rkOJHmljRUw",  # lytra main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCK2_5EdAbnsffpsukfFczAQ",  # lytra topic channel
    ## lychives doesnt exist on yt :(
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC18FYoV5GJGVzqv3zDZITYg",  # vyzer main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCJl6F8Cm_5b4xLePetRO_qw",  # vyzer topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-q4y1fPEIgh6WbAiW962lw",  # kets4eki main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCtLqYA9BYXeFwXtm1m2hyHQ",  # kets4eki topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCRlou117WaCPnx9BJEA6Jsw",  # kets2eki main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCfblnc0y3hlfq4QWl8ly1IA",  # kets2eki topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC51_vD84WCLxJHGkGtrLnQA",  # d3r main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvvfAEnHwOEoMMnt7Ag-DmA",  # d3r topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCBNRE3Axcf6espkth9G_KpA",  # despised main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCSW-wNDh8bK037-QHmbD9Gw",  # despised topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCI0wE8MldFp305Kq-hd6ahA",  # 6arelyhuman main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgwQOhO0eKZsqdWcPDkrGZQ",  # 6arelyhuman topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCRuQ1ST8xCwHZrX95fj1ypA",  # as remixes topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCGyu4H0YNhFZIU8j47C_yZg",  # as distributor topic channel 
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCQZET0rGIVQWb228H2vu9UQ",  # as songs main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC3nYNIeWVEx0bvBs55-l34g",  # archive5077 main channel
]
SPOTIFY_USERS = [
    "0I7VmE5LkRmWoHltutTUh9", # asteria
    "15fAtfsWfQ28x4A5fgNooB", # an4rch
    "765caWhYCY7Yiw5F6jZZHg", # lytra
    # couldnt find lychives
    "5jLQxZDFd3vrRb7t8OETCA", # vyzer
    "4waORdvuFnffJPrj784KeG", # kets4eki
    "04WeXjs1GAsBo58NYheafu", # kets2eki
    "41PE0deubI6MpwYruSEWHG", # d3r
    "0lFdeVF7rU3RXDaOx4Uiqf", # despised (d3r archive on spotify)
    "1oYXEVbGh1L7EWGm9C68cN", # 6arelyhuman
    "1Vb46tObS5tpK7GVJrVVpq"  # anarchist sanctuary
    # archive5077 sadly doesnt exist on spotify :(
]
TIKTOK_USERS = [
    "asteriasdeath", # i dont even need to list who is who its already in the u/n
    "an4rch82108363974",
    "lytramusic",
    "vyzer.mp3",
    "kets4eki",
    "kets4eki6251726",
    "superswagboi2005", # kets4eki 3rd acc
    "veryswagboy2005", # kets4eki 4th acc
    "d3rcore",
    "6arelyhuman",
##  "@anarchistsanctuary",
    "archive5077"
]

SOUNDCLOUD_WEBHOOK = os.environ.get("scDCWH")
YT_WEBHOOK = os.environ.get("ytDCWH")
SPOTIFY_WEBHOOK = os.environ.get("spDCWH")
TIKTOK_WEBHOOK = os.environ.get("ttDCWH")
SPOTIFY_CID = os.environ.get("spCIDKEYA")
SPOTIFY_CSC = os.environ.get("spCSCASDA")
UPTIMEROBOT_API_KEY = os.environ.get("uptrapik")
PORT = int(os.environ.get("PORT", 8080))
CACHE_FILE = "last_sent.json"

# =====================
# CACHE HANDLING
# =====================
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

cache = load_cache()

# =====================
# FUNCTIONS
# =====================
def get_latest_soundcloud_track(feed_url):
    try:
        r = requests.get(feed_url, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        artist = root.findtext("./channel/title", "Unknown Artist")
        item = root.find("./channel/item")
        if item is None:
            return None
        title = item.findtext("title", "Untitled")
        link = item.findtext("link", "")
        try:
            oembed_url = f"https://soundcloud.com/oembed?format=json&url={link}"
            o = requests.get(oembed_url, timeout=5).json()
            image = o.get("thumbnail_url") or "https://a-v2.sndcdn.com/assets/images/sc-icons/ios-a62dfc8fe7.png"
        except Exception:
            image = "https://a-v2.sndcdn.com/assets/images/sc-icons/ios-a62dfc8fe7.png"
        return {"title": title, "link": link, "artist": artist, "image": image}
    except Exception as e:
        print(f"❌ Error fetching {feed_url}: {e}")
        return None

def get_latest_youtube_video(feed_url):
    try:
        r = requests.get(feed_url, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.text)

        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015",
            "media": "http://search.yahoo.com/mrss/"
        }

        channel_title = root.findtext("atom:title", default="Unknown Channel", namespaces=ns)

        entry = root.find("atom:entry", ns)
        if entry is None:
            return None

        title = entry.findtext("atom:title", "Untitled", ns)
        link = entry.find("atom:link", ns).attrib["href"]
        video_id = entry.findtext("yt:videoId", "", ns)

        thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

        return {
            "title": title,
            "link": link,
            "artist": channel_title,
            "image": thumbnail,
            "video_id": video_id,
            "platform": "YouTube"
        }

    except Exception as e:
        print(f"❌ Error fetching YouTube feed {feed_url}: {e}")
        return None

def get_spotify_token():
    if not SPOTIFY_CID or not SPOTIFY_CSC:
        raise Exception("Missing Spotify credentials in env vars")

    auth = base64.b64encode(
        f"{SPOTIFY_CID}:{SPOTIFY_CSC}".encode()
    ).decode()

    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials"
        }
    )

    if not r.ok:
        print("Spotify token error:", r.status_code, r.text)
        raise Exception("Spotify auth failed")

    try:
        return r.json()["access_token"]
    except Exception:
        print("Bad response:", r.text)
        raise
        
def get_latest_spotify_release(artist_id, token):
    r = requests.get(
        f"https://api.spotify.com/v1/artists/{artist_id}/albums",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "include_groups": "album,single",
            "limit": 1,
            "market": "US"
        },
        timeout=10
    )

    if not r.ok:
        print("Spotify release error:", r.status_code, r.text)
        return None

    items = r.json().get("items", [])
    if not items:
        return None

    album = items[0]
    images = album.get("images") or []

    return {
        "id": album["id"],
        "title": album["name"],
        "artist": album["artists"][0]["name"],
        "image": images[0]["url"] if images else "",
        "link": album["external_urls"]["spotify"]
    }

class SilentYTDLPLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass
def get_latest_tiktok_video(username):
    username = username.lstrip("@")

    try:
        with YoutubeDL({
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "playlistend": 6,
            "ignoreerrors": True,
            "socket_timeout": 20,
            "logger": SilentYTDLPLogger(),
        }) as ydl:
            profile = ydl.extract_info(
                f"https://www.tiktok.com/@{username}",
                download=False,
            )

        if not profile:
            print(f"⏩ Skipped TikTok: @{username} has no public videos")
            return None

        videos = [video for video in (profile.get("entries") or []) if video]

        if not videos:
            print(f"⏩ Skipped TikTok: @{username} has no public videos")
            return None

        latest = max(videos, key=lambda video: video.get("timestamp") or 0)
        video_id = str(latest["id"])

        return {
            "id": video_id,
            "title": latest.get("description") or latest.get("title") or "New TikTok",
            "link": latest.get("webpage_url")
                    or f"https://www.tiktok.com/@{username}/video/{video_id}",
            "artist": latest.get("uploader") or username,
            "image": latest.get("thumbnail") or "",
        }

    except Exception:
        print(f"⏩ Skipped TikTok: @{username} is unavailable")
        return None

def send_discord_soundcloud(track):
    if not SOUNDCLOUD_WEBHOOK:
        print("Missing SoundCloud webhook")
        return
    
    payload = {
        "content": f"{track['artist']} — {track['title']} @everyone",
        "embeds": [{
            "title": track["title"],
            "url": track["link"],
            "color": 0xff7005,
            "author": {"name": track["artist"], "url": track["link"]},
            "image": {"url": track["image"]},
            "footer": {"text": "SoundCloud • New Upload 🎵"},
        }],
        "allowed_mentions": {"parse": ["everyone"]}
    }
    try:
        r = requests.post(SOUNDCLOUD_WEBHOOK, json=payload, timeout=5)
        if r.ok:
            print(f"✅ Sent: {track['artist']} — {track['title']}")
        else:
            print(f"❌ Failed webhook: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")

def send_youtube_discord(video):
    if not YT_WEBHOOK:
        print("Missing YouTube webhook")
        return
    
    payload = {
        "content": f"{video['artist']} — {video['title']} @everyone",
        "embeds": [{
            "title": video["title"],
            "url": video["link"],
            "color": 0xff0000,  # red
            "author": {"name": video["artist"], "url": video["link"]},
            "image": {"url": video["image"]},
            "footer": {"text": "YouTube • New Upload ▶️"},
        }],
        "allowed_mentions": {"parse": ["everyone"]}
    }

    try:
        r = requests.post(YT_WEBHOOK, json=payload, timeout=5)
        if r.ok:
            print(f"✅ Sent YT: {video['artist']} — {video['title']}")
        else:
            print(f"❌ Failed YT webhook: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Error sending YT webhook: {e}")

def send_spotify_discord(release):
    if not SPOTIFY_WEBHOOK:
        print("Missing Spotify webhook")
        return

    embed = {
        "title": release["title"],
        "url": release["link"],
        "color": 0x1DB954,
        "author": {
            "name": release["artist"],
            "url": release["link"]
        },
        "footer": {
            "text": "Spotify • New Release 🎵"
        }
    }

    if release.get("image"):
        embed["image"] = {"url": release["image"]}

    payload = {
        "content": f"{release['artist']} — {release['title']} @everyone",
        "embeds": [embed],
        "allowed_mentions": {"parse": ["everyone"]}
    }

    try:
        r = requests.post(SPOTIFY_WEBHOOK, json=payload, timeout=5)
        if not r.ok:
            print(f"❌ Failed Spotify webhook: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Error sending Spotify webhook: {e}")

def send_tiktok_discord(video):
    if not TIKTOK_WEBHOOK:
        print("Missing TikTok webhook")
        return False

    embed = {
        "title": video["title"],
        "url": video["link"],
        "color": 0x9a6adf,
        "author": {"name": video["artist"], "url": video["link"]},
        "footer": {"text": "TikTok • New Upload"},
    }
    if video["image"]:
        embed["image"] = {"url": video["image"]}

    try:
        r = requests.post(
            TIKTOK_WEBHOOK,
            json={
                "content": f"{video['artist']} — new TikTok @everyone",
                "embeds": [embed],
                "allowed_mentions": {"parse": ["everyone"]},
            },
            timeout=10,
        )
        if not r.ok:
            print(f"❌ Failed TikTok webhook: {r.status_code} {r.text}")
        return r.ok
    except Exception as e:
        print(f"❌ Error sending TikTok webhook: {e}")
        return False


def notify_all_feeds():
    global cache
    updated = False

    for feed in SOUNDCLOUD_USERS:
        track = get_latest_soundcloud_track(feed)
        if not track:
            continue

        last_link = cache.get(feed)
        if last_link != track["link"]:  # only send if new
            send_discord_soundcloud(track)
            cache[feed] = track["link"]
            updated = True
        else:
            print(f"⏩ Skipped (already sent): {track['artist']} — {track['title']}")

    if updated:
        save_cache(cache)

def notify_all_youtube():
    global cache
    updated = False

    sent_videos = set(cache.get("youtube_sent_ids", []))

    for feed in YOUTUBE_USERS:
        video = get_latest_youtube_video(feed)
        if not video:
            continue

        if video["video_id"] in sent_videos:
            print(f"⏩ Skipped duplicate YT: {video['title']}")
            continue

        send_youtube_discord(video)
        sent_videos.add(video["video_id"])
        updated = True

    if updated:
        cache["youtube_sent_ids"] = list(sent_videos)
        save_cache(cache)
        

def notify_all_spotify():
    global cache
    try:
        token = get_spotify_token()
    except Exception as e:
        print(f"❌ Couldn't get Spotify token: {e}")
        return
    updated=False
    for artist_id in SPOTIFY_USERS:
        try:
            release=get_latest_spotify_release(artist_id, token)
            if not release:
                continue
            key=f"spotify_{artist_id}"
            if cache.get(key)==release["id"]:
                print(f"⏩ Skipped Spotify: {release['artist']} — {release['title']}")
                continue
            send_spotify_discord(release)
            cache[key]=release["id"]
            updated=True
        except Exception as e:
            print(f"❌ Spotify error ({artist_id}): {e}")
    if updated:
        save_cache(cache)

def notify_all_tiktok():
    global cache
    updated = False

    for username in TIKTOK_USERS:
        video = get_latest_tiktok_video(username)
        if not video:
            continue

        cache_key = f"tiktok:{username.lower()}"
        if cache.get(cache_key) == video["id"]:
            print(f"⏩ Skipped TikTok: {video['artist']} — {video['title']}")
            continue

        if send_tiktok_discord(video):
            cache[cache_key] = video["id"]
            updated = True

    if updated:
        save_cache(cache)

# =====================
# FLASK SERVER
# =====================
app = Flask(__name__)

# =====================
# HOME PAGE
# =====================
@app.route("/")
def home():
    html = """
    <html>
    <head>
    <title>fmn - home</title>
    <style>
    body {
        background-color: #000;
        color: red;
        font-family: Arial, sans-serif;
        font-size: 24px;
        margin: 0;
        min-height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        width: 100%;
        max-width: 700px;
        padding: 20px;
    }
    h1, h2, h3, p {
        margin: 0;
    }
    .button {
        background-color: #000;
        color: red;
        padding: 16px 24px;
        font-size: 24px;
        border: 2px solid red;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        border-radius: 8px;
        display: inline-block;
        width: 100%;
        box-sizing: border-box;
    }
    .button:hover {
        background-color: #111;
        border-color: #ff3333;
        color: #ff3333;
    }
    </style>
    </head>
    <body>
        <div class="main-container">
            <h1>server uptime monitor</h1>
            <p>view uptime stats here</p>

            <a class="button"
               href="https://stats.uptimerobot.com/T2er9KoWTg/801768071"
               target="_blank">
               view live status (uptime robot)
            </a>

            <a class="button"
               href="https://m0sxgqql.status.cron-job.org"
               target="_blank">
               view live status (cron job)
            </a>

            <a class="button"
               href="https://fuckass-music-notifier.betteruptime.com"
               target="_blank">
               view live status (better stack)
            </a>

            <a class="button"
               href="/status"
               target="_blank">
               status page
            </a>
        </div>
    </body>
    </html>
    """

    return html, 200, {"Content-Type": "text/html; charset=utf-8"}


# =====================
# STATUS PAGE
# =====================
@app.route("/status")
def uptime_status():
    if not UPTIMEROBOT_API_KEY:
        return """
        <html>
        <body style="background:black;color:red;font-family:Arial;text-align:center;padding-top:50px;">
            <h2>❌ missing UPTIMEROBOT_API_KEY in environment</h2>
        </body>
        </html>
        """, 500, {"Content-Type": "text/html; charset=utf-8"}
    try:
        response = requests.post(
            "https://api.uptimerobot.com/v2/getMonitors",
            data={
                "api_key": UPTIMEROBOT_API_KEY,
                "format": "json"
            },
            timeout=5
        ).json()
        monitor = response["monitors"][0]
        name = monitor["friendly_name"]
        status = monitor["status"]
        uptime = monitor.get("all_time_uptime_ratio", "N/A")
        status_text = "🟢 Online" if status == 2 else "🔴 Down"
        color = "#4caf50" if status == 2 else "#f44336"
        html = f"""
        <html>
        <head>
        <title>fmn - status</title>
        <style>
        body {{
            background-color: #000;
            color: red;
            font-family: Arial, sans-serif;
            margin: 0;
            min-height: 100vh;

            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}
        .main-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 25px;
            width: 100%;
            max-width: 1200px;
            padding: 20px;
        }}
        .status-box {{
            border: 2px solid red;
            padding: 20px;
            border-radius: 12px;
            background: #111;
            width: 100%;
            box-sizing: border-box;
        }}
        iframe {{
            border: 2px solid red;
            border-radius: 8px;
            background: #000;
        }}
        .status-text {{
            font-size: 36px;
            color: {color};
        }}
        .uptime {{
            font-size: 24px;
        }}
        .button {{
            background-color: #000;
            color: red;
            padding: 16px 24px;
            font-size: 20px;
            border: 2px solid red;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            border-radius: 8px;
            display: inline-block;
        }}
        .button:hover {{
            background-color: #111;
            border-color: #ff3333;
            color: #ff3333;
        }}
        </style>
        </head>
        <body>
            <div class="main-container">
                <div class="status-box">
                    <h1>{name} — status</h1>
                    <p class="status-text">{status_text}</p>
                    <p class="uptime">
                        all-time uptime: <b>{uptime}%</b>
                    </p>
                </div>
                <iframe
                    src="https://fuckass-music-notifier.betteruptime.com/badge?theme=dark"
                    width="250"
                    height="30"
                    frameborder="0"
                    scrolling="no">
                </iframe>
                <iframe
                    src="https://fuckass-music-notifier.betteruptime.com"
                    width="1000"
                    height="700">
                </iframe>
                <a class="button" href="/">
                    ⬅ home
                </a>
            </div>
        </body>
        </html>
        """
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}

    except Exception as e:
        return f"""
        <html>
        <body style="background:black;color:red;font-family:Arial;text-align:center;padding-top:50px;">
            <h2>⚠️ error fetching UptimeRobot data</h2>
            <p>{e}</p>
        </body>
        </html>
        """, 500, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/sendsc")
def send_sc():
    notify_all_feeds()
    return jsonify({"status": "sent"}), 200

@app.route("/sendyt")
def send_yt():
    notify_all_youtube()
    return jsonify({"status": "sent"}), 200

@app.route("/sendsp")
def send_sp():
   # notify_all_spotify()
    return jsonify({"text":"im so sorry i dont have premium so its not gon work chat"}), 404
@app.route("/sendtt")
def send_tt():
    notify_all_tiktok()
    return jsonify({"status": "sent"}), 200

@app.route("/sendall")
def send_all():
    notify_all_feeds()
    notify_all_youtube()
    # notify_all_spotify()
    notify_all_tiktok()
    return jsonify({"status": "sent"}), 200

# =====================
# BACKGROUND LOOP
# =====================
def auto_notify_loop():
    while True:
        print("🔁 Checking SoundCloud feeds...")
        notify_all_feeds()
        print("🔁 Checking YouTube feeds...")
        notify_all_youtube()
       # print("🔁 Checking Spotify releases...")
       # notify_all_spotify()
        print("🔁 Checking TikTok feeds...")
        notify_all_tiktok()
        time.sleep(90)  # every 1.5 minutes (1m 30s /// 90 seconds)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    notify_all_feeds()
    notify_all_youtube()
    # notify_all_spotify()
    notify_all_tiktok()
    threading.Thread(target=auto_notify_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)
