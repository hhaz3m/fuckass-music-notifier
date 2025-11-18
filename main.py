import requests
import threading, time, json, os
import xml.etree.ElementTree as ET
from flask import Flask, jsonify

# =====================
# CONFIG
# =====================
SOUNDCLOUD_USERS = [
    "https://feeds.soundcloud.com/users/soundcloud:users:871836190/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:277600140/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:671246480/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1153776793/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1122731785/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:523819995/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1200417373/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1478512195/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1221437284/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1522578684/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1221718432/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1353863904/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1014983476/sounds.rss",
]

SOUNDCLOUD_WEBHOOK = os.environ.get("HEYOEEFSDFS")
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
def get_latest_track(feed_url):
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

def send_discord(track):
    payload = {
        "content": "@everyone 🎶 **New SoundCloud upload!**",
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

def notify_all_feeds():
    global cache
    updated = False

    for feed in SOUNDCLOUD_USERS:
        track = get_latest_track(feed)
        if not track:
            continue

        last_link = cache.get(feed)
        if last_link != track["link"]:  # only send if new
            send_discord(track)
            cache[feed] = track["link"]
            updated = True
        else:
            print(f"⏩ Skipped (already sent): {track['artist']} — {track['title']}")

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
         🔗 View Live Status
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
        </div>
        """
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return f"<h3>⚠️ Error fetching UptimeRobot data: {e}</h3>", 500, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/send")
def send_all():
    notify_all_feeds()
    return jsonify({"status": "sent"}), 200

# =====================
# BACKGROUND LOOP
# =====================
def auto_notify_loop():
    while True:
        print("🔁 Checking SoundCloud feeds...")
        notify_all_feeds()
        time.sleep(300)  # every 5 minutes (300 seconds)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    notify_all_feeds()  # send immediately on start
    threading.Thread(target=auto_notify_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)
