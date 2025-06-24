# 📤 movie_upload.py — Facebook Uploader (AWS Version)

import os
import time
import json
import requests
import random
from datetime import datetime
from dotenv import load_dotenv

# === Load .env secrets ===
load_dotenv()

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_TOKEN")
PAGE_ID = os.environ.get("PAGE_ID")
CAPTIONS_FILE = "captions.txt"
CLIPS_DIR = "clips"
BATCH_SIZE = 5

# === Discord Notification ===
def notify_discord(message):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message})
    except Exception as e:
        print("❌ Discord notification failed:", e)

# === Pick Random Caption ===
def get_random_caption():
    if os.path.exists(CAPTIONS_FILE):
        with open(CAPTIONS_FILE) as f:
            captions = [line.strip() for line in f if line.strip()]
        if captions:
            return random.choice(captions)
    return "🎬 Check out this video!"

# === Find Latest Clip Folder ===
def get_latest_clips_folder():
    folders = [os.path.join(CLIPS_DIR, d) for d in os.listdir(CLIPS_DIR)
               if os.path.isdir(os.path.join(CLIPS_DIR, d))]
    if not folders:
        raise RuntimeError("No clip folders found in 'clips/'")
    return max(folders, key=os.path.getmtime)

# === Upload Batch of Videos ===
def upload_batch(folder, token, page_id):
    files = sorted([f for f in os.listdir(folder)
                    if f.lower().endswith(('.mp4', '.mov', '.avi'))])

    if not files:
        print("❌ No videos to upload.")
        return

    batch = files[:BATCH_SIZE]
    results = []

    print(f"📤 Uploading batch of {len(batch)} videos...")
    notify_discord(f"📤 Uploading {len(batch)} videos to Facebook...")

    for idx, file in enumerate(batch, 1):
        try:
            path = os.path.join(folder, file)
            caption = f"{file}\n\n{get_random_caption()}"

            with open(path, 'rb') as vid:
                post_url = f"https://graph.facebook.com/v16.0/{page_id}/videos"
                res = requests.post(post_url,
                    data={"access_token": token, "description": caption},
                    files={"source": (file, vid, "video/mp4")},
                    timeout=300
                )

            if res.status_code == 200:
                vid_id = res.json().get("id")
                print(f"✅ {file} uploaded (Video ID: {vid_id})")
                results.append({"file": file, "status": "success", "id": vid_id})
                os.remove(path)
            else:
                error = res.json().get("error", {}).get("message", "Unknown error")
                print(f"❌ Failed to upload {file}: {error}")
                results.append({"file": file, "status": "failed", "error": error})
        except Exception as e:
            print(f"❌ Exception uploading {file}: {e}")
            results.append({"file": file, "status": "failed", "error": str(e)})

    # Log results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"upload_log_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    # Notify completion
    successes = sum(1 for r in results if r["status"] == "success")
    notify_discord(f"✅ Upload complete: {successes}/{len(batch)} succeeded.")

# === Run ===
if __name__ == "__main__":
    try:
        folder = get_latest_clips_folder()
        upload_batch(folder, PAGE_ACCESS_TOKEN, PAGE_ID)
    except Exception as e:
        print("❌ Upload failed:", e)
        notify_discord(f"❌ Facebook upload failed:\n```{str(e)[:1500]}```")
