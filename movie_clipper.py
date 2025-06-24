import os
import glob
import subprocess
from dotenv import load_dotenv

# === Load environment variables (if you want to notify later)
load_dotenv()

# === Constants ===
MOVIE_FOLDER_ROOT = "movies"
CLIPS_FOLDER_ROOT = "clips"

# === Step 1: Find Latest Movie Folder & Largest Video ===
def get_latest_movie_path(base_path=MOVIE_FOLDER_ROOT):
    folders = [os.path.join(base_path, d) for d in os.listdir(base_path)
               if os.path.isdir(os.path.join(base_path, d))]
    if not folders:
        raise FileNotFoundError(f"No folders found in {base_path}")
    latest_folder = max(folders, key=os.path.getmtime)

    valid_exts = (".mp4", ".mkv", ".mov", ".avi", ".webm")
    video_files = []
    for root, _, files in os.walk(latest_folder):
        for f in files:
            if f.lower().endswith(valid_exts):
                video_files.append(os.path.join(root, f))

    if not video_files:
        raise FileNotFoundError(f"No valid video files in {latest_folder}")

    movie_file = max(video_files, key=os.path.getsize)
    return latest_folder, movie_file

movie_folder, movie_file = get_latest_movie_path()
movie_name = os.path.basename(movie_folder).replace(" ", "_")
print("🎬 Movie:", movie_name)
print("📥 File:", movie_file)

# === Step 2: Get Duration ===
def get_video_duration(video_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return float(result.stdout.strip())

duration = get_video_duration(movie_file)
print(f"⏱ Duration: {duration:.2f} seconds")

# === Step 3: Create Clips with CPU (libx264) ===
def create_clips(input_path, output_folder, base_name, total_duration, clip_length=240,
                 start_margin=15*60, end_margin=20*60):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    safe_start = start_margin
    safe_end = int(total_duration) - end_margin

    clip_num = 1
    for start in range(safe_start, safe_end, clip_length):
        out_name = f"{base_name}_reel_{clip_num:02d}.mp4"
        out_path = os.path.join(output_folder, out_name)

        cmd = [
            "ffmpeg", "-ss", str(start), "-i", input_path,
            "-t", str(clip_length),
            "-vf", "scale=w=1080:h=1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
            "-c:v", "libx264", "-crf", "22", "-preset", "slow",
            "-c:a", "aac", "-b:a", "128k", "-y", out_path
        ]

        print(f"🎞 Creating clip: {out_name}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        clip_num += 1

# === Step 4: Run ===
output_dir = os.path.join(CLIPS_FOLDER_ROOT, movie_name)
create_clips(movie_file, output_dir, movie_name, duration)
print(f"✅ All clips saved to: {output_dir}")
