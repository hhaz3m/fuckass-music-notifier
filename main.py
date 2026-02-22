import requests
import threading, time, json, os
import xml.etree.ElementTree as ET
from flask import Flask, jsonify

# =====================
# CONFIG
# =====================
SOUNDCLOUD_USERS = [
    "https://feeds.soundcloud.com/users/soundcloud:users:871836190/sounds.rss", # asteria
    "https://feeds.soundcloud.com/users/soundcloud:users:1522578684/sounds.rss", # an4rch (asteria archive)
    "https://feeds.soundcloud.com/users/soundcloud:users:277600140/sounds.rss", # lytra
    "https://feeds.soundcloud.com/users/soundcloud:users:671246480/sounds.rss", # vyzer
    "https://feeds.soundcloud.com/users/soundcloud:users:1014983476/sounds.rss", # vychives
    "https://feeds.soundcloud.com/users/soundcloud:users:1153776793/sounds.rss", # kets4eki
    "https://feeds.soundcloud.com/users/soundcloud:users:1200417373/sounds.rss", # kets2eki (kets archive)
    "https://feeds.soundcloud.com/users/soundcloud:users:1122731785/sounds.rss", # d3r
    "https://feeds.soundcloud.com/users/soundcloud:users:1221437284/sounds.rss", # despised
    "https://feeds.soundcloud.com/users/soundcloud:users:523819995/sounds.rss", # 6arelyhuman
    "https://feeds.soundcloud.com/users/soundcloud:users:1353863904/sounds.rss", # anarchist sanctuary (remixes)
    "https://feeds.soundcloud.com/users/soundcloud:users:1478512195/sounds.rss", # anarchist sanctuary (songs)
    "https://feeds.soundcloud.com/users/soundcloud:users:1221718432/sounds.rss", # archive
]
YOUTUBE_USERS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCMvmRb3dal_aGxmhTVeRCdw",  # asteria main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCJMm3-iHCoqaWkr_Q5_E8UA",  # asteria topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCOkqU6zsc_yxKFj5X1-O9HQ",  # an4rch topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCeSYZhLKq-L9rkOJHmljRUw",  # lytra main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCK2_5EdAbnsffpsukfFczAQ",  # lytra topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC18FYoV5GJGVzqv3zDZITYg",  # vyzer main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCJl6F8Cm_5b4xLePetRO_qw",  # vyzer topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-q4y1fPEIgh6WbAiW962lw",  # kets4eki main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCtLqYA9BYXeFwXtm1m2hyHQ",  # kets4eki topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCfblnc0y3hlfq4QWl8ly1IA",  # kets2eki topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC51_vD84WCLxJHGkGtrLnQA",  # d3r main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvvfAEnHwOEoMMnt7Ag-DmA",  # d3r topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCBNRE3Axcf6espkth9G_KpA",  # despised main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCSW-wNDh8bK037-QHmbD9Gw",  # despised topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCI0wE8MldFp305Kq-hd6ahA",  # 6arelyhuman main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCgwQOhO0eKZsqdWcPDkrGZQ",  # 6arelyhuman topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCRuQ1ST8xCwHZrX95fj1ypA",  # as remixes topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCQZET0rGIVQWb228H2vu9UQ",  # as songs main channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC9iWImT4TFIit7FLJcBKFfA",  # as songs topic channel
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC3nYNIeWVEx0bvBs55-l34g",  # archive5077 main channel
]

SOUNDCLOUD_WEBHOOK = os.environ.get("HEYOEEFSDFS")
YT_WEBHOOK = os.environ.get("OHOHA")
UPTIMEROBOT_API_KEY = os.environ.get("UPTIMEROBOT_API_KEY")
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
        if not item:
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
            "platform": "YouTube"
        }

    except Exception as e:
        print(f"❌ Error fetching YouTube feed {feed_url}: {e}")
        return None

def send_discord_soundcloud(track):
    payload = {
        "content": f"{track['artist']} — {track['title']} @everyone",
        "embeds": [{
            "title": track["title"],
            "url": track["link"],
            "color": 16742893,
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
    payload = {
        "content": f"{video['artist']} — {video['title']} @everyone",
        "embeds": [{
            "title": video["title"],
            "url": video["link"],
            "color": 16711680,  # red
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

    for feed in YOUTUBE_CHANNELS:
        video = get_latest_youtube_video(feed)
        if not video:
            continue

        last_link = cache.get(feed)
        if last_link != video["link"]:
            send_youtube_discord(video)
            cache[feed] = video["link"]
            updated = True
        else:
            print(f"⏩ Skipped YT (already sent): {video['artist']} — {video['title']}")

    if updated:
        save_cache(cache)
        
# =====================
# FLASK SERVER
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    html = """
    <div style="max-width:600px;margin:auto;text-align:center;font-family:sans-serif;">
      <h2>Server Uptime Monitor</h2>
      <p style="color:#666;">View real-time uptime stats here:</p>
      <a href="https://stats.uptimerobot.com/T2er9KoWTg/801768071" target="_blank"
         style="display:inline-block;background:#4caf50;color:white;padding:10px 20px;
                border-radius:8px;text-decoration:none;box-shadow:0 4px 8px rgba(0,0,0,0.2);">
         🔗 View Live Status (Uptime Robot)
      </a>
      <a href="https://m0sxgqql.status.cron-job.org" target="_blank"
         style="display:inline-block;background:#4caf50;color:white;padding:10px 20px;
                border-radius:8px;text-decoration:none;box-shadow:0 4px 8px rgba(0,0,0,0.2);">
         🔗 View Live Status (Cron Job)
      </a>
      <a href="https://fuckass-music-notifier.betteruptime.com" target="_blank"
         style="display:inline-block;background:#4caf50;color:white;padding:10px 20px;
                border-radius:8px;text-decoration:none;box-shadow:0 4px 8px rgba(0,0,0,0.2);">
         🔗 View Live Status (Better Stack)
      </a>
      <a href="https://fuckass-music-notifier.onrender.com/status" target="_blank"
         style="display:inline-block;background:#4caf50;color:white;padding:10px 20px;
                border-radius:8px;text-decoration:none;box-shadow:0 4px 8px rgba(0,0,0,0.2);">
         🔗 Go To Status Page
      </a>
    </div>
    """
    return html, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/status")
def uptime_status():
    if not UPTIMEROBOT_API_KEY:
        return "<h3 style='color:red;text-align:center;'>❌ Missing UPTIMEROBOT_API_KEY in environment</h3>", 500, {"Content-Type": "text/html; charset=utf-8"}
    try:
        response = requests.post(
            "https://api.uptimerobot.com/v2/getMonitors",
            data={"api_key": UPTIMEROBOT_API_KEY, "format": "json"},
            timeout=5
        ).json()

        monitor = response["monitors"][0]
        name = monitor["friendly_name"]
        status = monitor["status"]
        uptime = monitor.get("all_time_uptime_ratio", "N/A")

        status_text = "🟢 Online" if status == 2 else "🔴 Down"
        color = "#4caf50" if status == 2 else "#f44336"

        html = f"""
        <div style="font-family:sans-serif;text-align:center;margin-top:50px;">
            <h2>{name} — Status</h2>
            <p style="font-size:24px;color:{color};">{status_text}</p>
            <p>All-time uptime: <b>{uptime}%</b></p>
            <iframe src="https://fuckass-music-notifier.betteruptime.com/badge?theme=dark" width="250" height="30" frameborder="0" scrolling="no" style="color-scheme: normal"></iframe>
            <iframe src="https://fuckass-music-notifier.betteruptime.com" width="1000" height="800"></iframe>
        </div>
        """
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return f"<h3>⚠️ Error fetching UptimeRobot data: {e}</h3>", 500, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/sendsc")
def send_all():
    notify_all_feeds()
    return jsonify({"status": "sent"}), 200

@app.route("/sendyt")
def send_all():
    notify_all_youtube()
    return jsonify({"status": "sent"}), 200

@app.route("/sendall")
def send_all():
    notify_all_feeds()
    notify_all_youtube()
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
        time.sleep(90)  # every 1.5 minutes (90 seconds)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    notify_all_feeds()  # send immediately on start
    threading.Thread(target=auto_notify_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)
