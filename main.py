import requests
import xml.etree.ElementTree as ET
import os
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
   # "https://feeds.soundcloud.com/users/soundcloud:users:/sounds.rss",
    #"https://feeds.soundcloud.com/users/soundcloud:users:/sounds.rss",
   # "https://feeds.soundcloud.com/users/soundcloud:users:/sounds.rss",
]

SOUNDCLOUD_WEBHOOK = os.environ.get("HEYOEEFSDFS")
PORT = int(os.environ.get("PORT", 8080))

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
            image = o.get("thumbnail_url")
        except Exception:
            image = "https://a-v2.sndcdn.com/assets/images/sc-icons/ios-a62dfc8fe7.png"
        if not image:
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
    for feed in SOUNDCLOUD_USERS:
        track = get_latest_track(feed)
        if track:
            send_discord(track)
        else:
            print(f"No track found for feed: {feed}")

# =====================
# FLASK SERVER
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "ok"}), 200  # 200 OK for UptimeRobot

@app.route("/send")
def send_all():
    notify_all_feeds()
    return jsonify({"status": "sent"}), 200

# =====================
# RUN
# =====================
if __name__ == "__main__":
    notify_all_feeds()  # send immediately on start
    app.run(host="0.0.0.0", port=PORT)
