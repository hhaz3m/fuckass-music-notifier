import requests
import time
import xml.etree.ElementTree as ET
import os
from flask import Flask
from threading import Thread

# === CONFIG ===
SOUNDCLOUD_USERS = [
    "https://feeds.soundcloud.com/users/soundcloud:users:871836190/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:277600140/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:671246480/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1153776793/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:1122731785/sounds.rss",
    "https://feeds.soundcloud.com/users/soundcloud:users:523819995/sounds.rss",
]

YT_CHANNELS = [
    "UCMvmRb3dal_aGxmhTVeRCdw",
    "UCeSYZhLKq-L9rkOJHmljRUw",
    "UC18FYoV5GJGVzqv3zDZITYg",
    "UC-q4y1fPEIgh6WbAiW962lw",
    "UC51_vD84WCLxJHGkGtrLnQA",
    "UCI0wE8MldFp305Kq-hd6ahA",
]

SOUNDCLOUD_WEBHOOK = os.environ["HEYOEEFSDFS"]
YOUTUBE_WEBHOOK = os.environ["OHOHA"]
CHECK_INTERVAL = 60

latest_titles = {}
first_run = True

# === FETCH FUNCTIONS ===
def get_latest_track(feed_url):
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
        image = None
    if not image:
        image = "https://a-v2.sndcdn.com/assets/images/sc-icons/ios-a62dfc8fe7.png"
    return {"title": title, "link": link, "artist": artist, "image": image}


def get_latest_youtube(channel_id):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    r = requests.get(feed_url, timeout=10)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    ns = {"media": "http://search.yahoo.com/mrss/"}
    entry = root.find("entry")
    if not entry:
        return None
    title = entry.findtext("title", "Untitled")
    link = entry.find("link").attrib.get("href")
    channel_name = root.findtext("title", "Unknown Channel")
    thumbnail = entry.find("media:group/media:thumbnail", ns).attrib.get("url", "")
    return {"title": title, "link": link, "channel": channel_name, "thumbnail": thumbnail}


# === FLASK SERVER ===
app = Flask(__name__)

@app.route("/")
def home():
    return "🎵 SoundCloud + YouTube Discord Notifier is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# === MAIN LOOP ===
def notifier_loop():
    global first_run
    while True:
        try:
            # --- SoundCloud ---
            for feed in SOUNDCLOUD_USERS:
                track = get_latest_track(feed)
                if not track:
                    continue
                title = track["title"]
                artist = track["artist"]
                link = track["link"]
                image = track["image"]
                if latest_titles.get(feed) == title:
                    continue
                latest_titles[feed] = title
                embed = {
                    "title": title,
                    "url": link,
                    "color": 16742893,
                    "author": {"name": artist, "url": link},
                    "image": {"url": image},
                    "footer": {"text": "SoundCloud • New Upload 🎵"},
                }
                payload = {
                    "content": "@everyone 🎶 **New SoundCloud upload!**",
                    "embeds": [embed],
                    "allowed_mentions": {"parse": ["everyone"]},
                }
                requests.post(SOUNDCLOUD_WEBHOOK, json=payload, timeout=5)
                print(f"✅ SoundCloud: {artist} — {title}")

            # --- YouTube ---
            for channel_id in YT_CHANNELS:
                video = get_latest_youtube(channel_id)
                if not video:
                    continue
                title = video["title"]
                channel = video["channel"]
                link = video["link"]
                thumbnail = video["thumbnail"]
                if not first_run and latest_titles.get(channel_id) == title:
                    continue
                latest_titles[channel_id] = title
                embed = {
                    "title": title,
                    "url": link,
                    "color": 16711680,
                    "author": {"name": channel, "url": f"https://www.youtube.com/channel/{channel_id}"},
                    "image": {"url": thumbnail},
                    "footer": {"text": "YouTube • New Upload ▶️"},
                }
                payload = {
                    "content": "@everyone 🎥 **New YouTube video!**",
                    "embeds": [embed],
                    "allowed_mentions": {"parse": ["everyone"]},
                }
                requests.post(YOUTUBE_WEBHOOK, json=payload, timeout=5)
                print(f"✅ YouTube: {channel} — {title}")

            first_run = False

        except Exception as e:
            print(f"Error: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    Thread(target=run_flask).start()
    Thread(target=notifier_loop).start()
