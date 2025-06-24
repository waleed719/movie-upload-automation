# 🎬 download.py — CPU-friendly, AWS-ready

import os
import time
import glob
import shutil
import random
import subprocess
import requests
import pandas as pd
from dotenv import load_dotenv

# === Load env variables ===
load_dotenv()
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

# === Constants ===
CSV_PATH = "imdb_magnet_links.csv"
MOVIE_DOWNLOAD_FOLDER = "movies"

# === Notify via Discord ===
def notify_discord(message):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("❌ Discord notify failed:", e)

# === Aria2c Magnet Downloader ===
def download_with_aria2(magnet_link, download_dir="download_tmp"):
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)
    os.makedirs(download_dir, exist_ok=True)

    print("⬇ Downloading with aria2c (max 10 mins)...")

    cmd = [
        "aria2c", magnet_link,
        "--dir", download_dir,
        "--seed-time=0",
        "--enable-dht=true",
        "--bt-enable-lpd=true",
        "--bt-save-metadata=true",
        "--summary-interval=5",
        "--bt-tracker-timeout=60",
        "--bt-tracker-connect-timeout=60",
        "--timeout=60"
    ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        start_time = time.time()
        download_started = False

        while True:
            line = process.stdout.readline()
            if line:
                print(line.strip())
                if "[#Download" in line or "[METADATA]" in line:
                    download_started = True
                    print("✅ aria2c: Download or metadata acquisition started!")
                    break

            if time.time() - start_time > 30 or process.poll() is not None:
                break
            time.sleep(0.1)

        stdout_full, stderr_full = process.communicate(timeout=600 - (time.time() - start_time))
        print(stdout_full)
        print(stderr_full)

        if process.returncode != 0:
            print(f"❌ aria2c failed: Exit code {process.returncode}")
            return None

    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ aria2c timed out.")
        return None
    except Exception as e:
        print(f"❌ aria2c error: {e}")
        return None

    # Check if any files were downloaded
    downloaded_files = glob.glob(f"{download_dir}/**/*", recursive=True)
    if not downloaded_files:
        print("❌ No files downloaded.")
        return None

    print(f"✅ Downloaded {len(downloaded_files)} file(s).")
    return download_dir

# === Main Download Logic ===
def main():
    try:
        # Load CSV of movies
        df = pd.read_csv(CSV_PATH)
        if df.empty:
            raise ValueError("❌ Movie magnet list is empty!")

        # Pick a random movie
        selected_row = df.sample(n=1).iloc[0]
        movie_name = selected_row["Movies"].replace(" ", "_")
        magnet_link = selected_row["Magnet Links"]

        print("🎯 Selected:", movie_name)
        print("🔗 Magnet:", magnet_link)

        notify_discord(f"🎬 Movie selected: `{movie_name}`")
        notify_discord(f"🔗 Magnet: {magnet_link[:80]}...")

        download_dir = os.path.join(MOVIE_DOWNLOAD_FOLDER, movie_name)
        downloaded = download_with_aria2(magnet_link, download_dir)

        if downloaded:
            print(f"📦 Downloaded to: {download_dir}")
            df = df[df["Movies"] != selected_row["Movies"]]
            df.to_csv(CSV_PATH, index=False)
            notify_discord("✅ Download complete. Movie removed from CSV.")
        else:
            notify_discord("❌ Download failed.")

    except Exception as e:
        print("❌ Download pipeline failed:", e)
        notify_discord(f"❌ Download failed: {str(e)[:1500]}")

# === Entry Point ===
if __name__ == "__main__":
    main()
