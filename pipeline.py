import os
import time
import subprocess
import shutil
from dotenv import load_dotenv
import requests

# === Load env variables ===
load_dotenv()
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")

# === Paths ===
MOVIES_PATH = "movies"
CLIPS_PATH = "clips"
CSV_PATH = "imdb_magnet_links.csv"

# === Notify via Discord ===
def notify_discord(message):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message})
    except Exception as e:
        print("❌ Discord notification failed:", e)

# === Get Latest Movie/Clip Folder ===
def get_latest_movie_folder():
    folders = [os.path.join(MOVIES_PATH, d) for d in os.listdir(MOVIES_PATH) if os.path.isdir(os.path.join(MOVIES_PATH, d))]
    return max(folders, key=os.path.getmtime)

def get_latest_clip_folder():
    folders = [os.path.join(CLIPS_PATH, d) for d in os.listdir(CLIPS_PATH) if os.path.isdir(os.path.join(CLIPS_PATH, d))]
    return max(folders, key=os.path.getmtime)

# === Run a Script ===
def run_script(name):
    try:
        print(f"🚀 Running {name}.py...")
        result = subprocess.run(["python3", f"{name}.py"], capture_output=True, text=True, timeout=3600)
        if result.returncode != 0:
            notify_discord(f"❌ `{name}.py` failed:\n```{result.stderr[:1500]}```")
            print(result.stderr)
            return False
        print(result.stdout)
        return True
    except Exception as e:
        notify_discord(f"❌ Failed to run `{name}.py`:\n```{str(e)}```")
        return False

# === Delete Last Movie & Clips ===
def delete_latest_movie_and_clips():
    try:
        latest_movie = get_latest_movie_folder()
        latest_clip = os.path.join(CLIPS_PATH, os.path.basename(latest_movie))
        shutil.rmtree(latest_movie)
        shutil.rmtree(latest_clip)
        notify_discord("🧹 Deleted movie and clips after success.")
    except Exception as e:
        notify_discord(f"⚠️ Cleanup failed: {e}")

# === Main Pipeline ===
if __name__ == "__main__":
    notify_discord("🎬 Movie pipeline started")

    if not run_script("download"):
        notify_discord("❌ Aborted after download failure.")
        exit(1)

    if not run_script("clipper"):
        notify_discord("❌ Aborted after clipper failure.")
        exit(1)

    # Upload loop (6 batches of 5 videos per hour)
    for i in range(6):
        clip_folder = get_latest_clip_folder()
        if not os.listdir(clip_folder):
            notify_discord("✅ All clips uploaded.")
            break

        notify_discord(f"📤 Uploading batch {i+1}/6")
        if not run_script("upload"):
            notify_discord("⚠️ Upload script failed during batch.")
            break

        if os.listdir(clip_folder):
            print("⏳ Waiting 1 hour for next batch...")
            time.sleep(3600)

    # Final cleanup
    if not os.listdir(get_latest_clip_folder()):
        delete_latest_movie_and_clips()
        notify_discord("✅ Movie pipeline finished.")
    else:
        notify_discord("⚠️ Some clips remain. Manual cleanup may be needed.")
