# YOUTUBE-VIDEO-DOWNLOADER

A python code with index for download youtube videos

# MyTube – YouTube Search, View & Download Web App

MyTube is a self-hosted YouTube-style web app with:
- **Search** videos on YouTube
- **Display results in a grid** (thumbnails, title, duration, views, channel, upload time)
- **Watch videos** in a built-in player
- **Download** as MP4 or MP3 (audio only)
- **Lightweight backend** (Flask + yt-dlp) and **static frontend** (HTML + JS)

---

## 🚀 Features
- Search YouTube without an API key  
- Instant grid view like YouTube’s homepage  
- Play videos directly in the browser  
- Download MP4/MP3 in one click  
- Works locally or on free hosting (Koyeb + Cloudflare Pages)  

---

## 📂 Project Structure
mytube/
├─ api/ # Backend (Flask + yt-dlp)
│ ├─ app.py
│ ├─ requirements.txt
│ └─ Dockerfile
└─ web/ # Frontend (HTML, CSS, JS)
└─ index.html


---

## 🛠 Local Installation

### 1. Clone or unzip the project

## Windows
py -3.10 -m venv .venv
.venv\Scripts\activate

Mac/Linux:
python3.10 -m venv .venv
source .venv/bin/activate

Install dependencies
Important: Ensure yt-dlp version is valid (latest stable).

pip install -r requirements.txt

python app.py

Open web/index.html in your browser
