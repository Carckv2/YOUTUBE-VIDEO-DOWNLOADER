from __future__ import annotations
import os, pathlib, tempfile, time, uuid, shutil
from typing import List, Dict
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from yt_dlp import YoutubeDL

APP = Flask(__name__)
CORS(APP)
TMP = pathlib.Path(tempfile.gettempdir()) / "yt_site_dl"
TMP.mkdir(parents=True, exist_ok=True)

YDL_FLAT = {"quiet": True, "extract_flat": True, "skip_download": True, "noplaylist": True}
YDL_INFO = {"quiet": True, "noplaylist": True}

def _thumb(e):
    thumbs = e.get("thumbnails") or []
    if not thumbs: return None
    return sorted(thumbs, key=lambda t: (t.get("width",0)*t.get("height",0)), reverse=True)[0].get("url")

def _basic(entry):
    return {
        "id": entry.get("id"),
        "title": entry.get("title") or "",
        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
        "channel": entry.get("uploader") or entry.get("channel") or "",
        "duration": entry.get("duration") or 0,
        "views": entry.get("view_count"),
        "upload_date": entry.get("upload_date"),
        "thumb": _thumb(entry),
    }

@APP.get("/api/home")
def home():
    # Trending page as “home”
    with YoutubeDL(YDL_FLAT) as ydl:
        info = ydl.extract_info("https://www.youtube.com/feed/trending", download=False)
    entries = info.get("entries", []) if isinstance(info, dict) else []
    return jsonify([_basic(e) for e in entries[:32]])

@APP.get("/api/search")
def search():
    q = (request.args.get("q") or "").strip()
    if not q: return jsonify([])
    n = int(request.args.get("limit", 32))
    with YoutubeDL(YDL_FLAT) as ydl:
        info = ydl.extract_info(f"ytsearch{n}:{q}", download=False)
    entries = info.get("entries", []) if isinstance(info, dict) else []
    return jsonify([_basic(e) for e in entries])

@APP.get("/api/watch")
def watch():
    vid = request.args.get("id")
    if not vid: abort(400, "missing id")
    with YoutubeDL({**YDL_INFO, "extract_flat": False}) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
    mp4s = []
    for f in info.get("formats", []):
        if f.get("acodec") != "none" and f.get("vcodec") != "none" and "mp4" in (f.get("ext") or ""):
            mp4s.append({
                "format_id": f.get("format_id"),
                "resolution": f"{(f.get('height') or '')}p",
                "filesize": f.get("filesize") or f.get("filesize_approx"),
            })
    return jsonify({
        "id": info.get("id"),
        "title": info.get("title"),
        "channel": info.get("uploader"),
        "duration": info.get("duration"),
        "thumb": _thumb(info),
        "mp4": mp4s,
    })

@APP.get("/api/download")
def download():
    vid = request.args.get("id"); kind = (request.args.get("kind") or "mp4").lower()
    if not vid: abort(400, "missing id")
    work = TMP / str(uuid.uuid4()); work.mkdir(parents=True, exist_ok=True)
    if kind == "mp3":
        opts = {
            **YDL_INFO,
            "format": "bestaudio/best",
            "outtmpl": str(work / "%(title)s.%(ext)s"),
            "postprocessors": [{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"192"}],
        }
        ext = ".mp3"
    else:
        opts = {
            **YDL_INFO,
            "format": "bv*+ba/b",
            "merge_output_format": "mp4",
            "outtmpl": str(work / "%(title)s.%(ext)s"),
        }
        ext = ".mp4"
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=True)
    file = next(work.glob(f"*{ext}"), None)
    if not file: abort(500, "no file produced")
    def _cleanup(path, d):
        from threading import Thread
        def later(): 
            import time as _t
            _t.sleep(15); 
            import shutil as _s
            _s.rmtree(d, ignore_errors=True)
        Thread(target=later, daemon=True).start()
        return send_file(str(path), as_attachment=True)
    return _cleanup(file, work)

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))