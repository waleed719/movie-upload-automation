# 🎬 Movie Clipper & Auto Facebook Uploader 🤖

This project is a fully automated Python pipeline that takes top-rated movies, clips them into vertical reels, and uploads them to Facebook — completely hands-free.

Hosted on AWS Free Tier with Discord notifications, and built for automation lovers who want to scale content effortlessly.

---

## 🚀 Features

✅ **IMDB Top Movie Automation**  
✅ **Magnet Link Downloader** via qBittorrent / Aria2c  
✅ **FFmpeg Clipper** (CPU-only, margin-aware)  
✅ **Auto Upload to Facebook Pages**  
✅ **Scheduled or Manual Pipeline Execution**  
✅ **Discord Notifications** at every step  
✅ **Deletes old movies/clips** to save storage  
✅ **Runs on AWS EC2 (Free Tier)**  

---

## 🧠 How It Works

```
🎯  Step 1: Pick a movie from a CSV (IMDB Top List)
⬇️  Step 2: Download using magnet link
✂️  Step 3: Clip into vertical reels (1080x1920) skipping credits
📤  Step 4: Upload 5 reels/hour to Facebook Page
🔔  Step 5: Notify each step via Discord
🧹  Step 6: Delete movie & clips after upload
```

---

## 🗂️ Project Structure

```
movie-upload-automation/
├── movies/                  # Downloaded movie folders
├── clips/                   # Output video reels
├── logs/                    # Logs of pipeline runs
├── .env                     # Your secrets
│
├── movie_download.py        # Downloads movie using magnet link
├── movie_clipper.py         # Clips full movie into reels
├── movie_upload.py          # Uploads reels to Facebook
├── pipeline.py              # Runs full process w/ Discord notifications
│
├── Movies_with_links.csv    # CSV of movie name + magnet link
├── captions.txt             # Pool of captions (randomized)
├── requirements.txt
└── README.md
```

---

## 🔐 Setup: Configuration & Secrets

Create a `.env` file in the root folder:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
FB_TOKEN=your_facebook_page_access_token
FB_PAGE_ID=your_facebook_page_id
```

---

## ⚙️ Installation (Ubuntu AWS EC2)

```bash
# 1. Clone the repo
git clone https://github.com/waleed719/movie-upload-automation
cd movie-upload-automation

# 2. Install system deps
sudo apt update
sudo apt install python3-pip ffmpeg aria2

# 3. Install Python deps
pip3 install -r requirements.txt

# 4. Add your secrets
nano .env  # paste in your DISCORD_WEBHOOK_URL, FB_TOKEN, FB_PAGE_ID

# 5. Run the full pipeline
python3 pipeline.py
```

---

## 🕒 Optional: Schedule Weekly Execution with crontab

```bash
crontab -e
```

Paste this to run every Monday at 2:00 AM:

```bash
0 2 * * 1 cd /home/ubuntu/movie-upload-automation && /usr/bin/python3 pipeline.py >> logs/pipeline.log 2>&1
```

---

## 📤 Upload Customization

- Uploads 5 clips per hour (Facebook policy-safe)
- Captions are randomized from `captions.txt`
- Movie name is extracted from folder name like:
  ```txt
  🎬 Movie: The Matrix

  👉 “Don’t follow the white rabbit.”
  ```

---

## 📈 Future Add-ons (WIP)

- [ ] Upload to Instagram & YouTube Shorts
- [ ] GUI interface to add/edit caption pool
- [ ] Telegram/WhatsApp/Email notifier options
- [ ] GPU clipping support for faster processing

---

## 👤 Author

Built by **[Waleed Qamar](https://github.com/waleed719)**  
🧠 Automation addict, movie nerd, and Python lover.

---

## 🧾 License

[MIT License](LICENSE) — Free to use, fork, remix, and automate your content.

---

## 🙌 Support

If this project saves you time, consider ⭐ starring the repo — it helps visibility!
