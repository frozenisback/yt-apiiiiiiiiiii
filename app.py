from flask import Flask, request, jsonify
import yt_dlp
import tempfile
import os
import time

app = Flask(__name__)

# ---- Hardcoded cookies ----
COOKIES = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	TRUE	1793164951	PREF	tz=Asia.Colombo&f6=40000000&f7=100
.youtube.com	TRUE	/	TRUE	1787901316	__Secure-3PAPISID	3tFTcT-bQGul-Mdj/AKKWsSmqamNTh8yQ6
.youtube.com	TRUE	/	TRUE	1784877316	__Secure-1PSIDTS	sidts-CjAB5H03PyeasaPG9wIKHD7VKkiVrbkWzhR9kd5aCL05uSw38fK1K2YNg7Od5xvG0fQQAA
.youtube.com	TRUE	/	TRUE	1784877316	__Secure-3PSIDTS	sidts-CjAB5H03PyeasaPG9wIKHD7VKkiVrbkWzhR9kd5aCL05uSw38fK1K2YNg7Od5xvG0fQQAA
.youtube.com	TRUE	/	TRUE	1787901316	__Secure-3PSID	g.a000zQjuCKhHm2Vkbut5ywtdx8qDlxm0k9KwaN7Odg0fceRdZlck955SNAFKO6kc4ag8fImxzgACgYKAScSARQSFQHGX2MiNGRLZgtqe6bg6AbzvgRBrBoVAUF8yKo1BbqZvxuqe4v--oFejMsx0076
.youtube.com	TRUE	/	TRUE	1787901316	LOGIN_INFO	AFmmF2swRQIgZzTwhbVrxH2jwjT_s5_bmwuKbwtxdrnWJ0oosIvWUMACIQC2JdHuKDxCVgOdyCtp6OBL1ziPBwLUvXVXB0YiF0SmnA:QUQ3MjNmekZ6blZYZXVrclczc1NRcHNnajZic1YxZWNROHpCYmxqb1dOYmVQcWZsMHVpMGxMMktzQXo5dHNjYVZ5QTl3ZkRYbkZrRFdWX0RxcV8wdWlNb3VTcU40cVl1bTBMWG9BQkpTUUtjd1RtQmdTZUFSSVVYQ2xtV192dlZPOWJySHVJZ2xCdEZHRFl4ZGdVbDFCQ2tYdmtVNkNyX0tR
.youtube.com	TRUE	/	FALSE	1758604955	ST-tladcw	session_logininfo=AFmmF2swRQIgZzTwhbVrxH2jwjT_s5_bmwuKbwtxdrnWJ0oosIvWUMACIQC2JdHuKDxCVgOdyCtp6OBL1ziPBwLUvXVXB0YiF0SmnA%3AQUQ3MjNmekZ6blZYZXVrclczc1NRcHNnajZic1YxZWNROHpCYmxqb1dOYmVQcWZsMHVpMGxMMktzQXo5dHNjYVZ5QTl3ZkRYbkZrRFdWX0RxcV8wdWlNb3VTcU40cVl1bTBMWG9BQkpTUUtjd1RtQmdTZUFSSVVYQ2xtV192dlZPOWJySHVJZ2xCdEZHRFl4ZGdVbDFCQ2tYdmtVNkNyX0tR
.youtube.com	TRUE	/	FALSE	1758604956	ST-xuwub9	session_logininfo=AFmmF2swRQIgZzTwhbVrxH2jwjT_s5_bmwuKbwtxdrnWJ0oosIvWUMACIQC2JdHuKDxCVgOdyCtp6OBL1ziPBwLUvXVXB0YiF0SmnA%3AQUQ3MjNmekZ6blZYZXVrclczc1NRcHNnajZic1YxZWNROHpCYmxqb1dOYmVQcWZsMHVpMGxMMktzQXo5dHNjYVZ5QTl3ZkRYbkZrRFdWX0RxcV8wdWlNb3VTcU40cVl1bTBMWG9BQkpTUUtjd1RtQmdTZUFSSVVYQ2xtV192dlZPOWJySHVJZ2xCdEZHRFl4ZGdVbDFCQ2tYdmtVNkNyX0tR
.youtube.com	TRUE	/	TRUE	1790140953	__Secure-3PSIDCC	AKEyXzVdRWCrVmkMyR8UdYZx95vqhsfRfETBuHviCty9ZkcmaWR97_u_nzJWD58S8dpudCZVZfM
.youtube.com	TRUE	/	TRUE	1774156949	VISITOR_INFO1_LIVE	vexWIg6Hlw8
.youtube.com	TRUE	/	TRUE	1774156949	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgGQ%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	jejOfTrsOck
.youtube.com	TRUE	/	TRUE	1774153438	__Secure-ROLLOUT_TOKEN	CNC--4Wlx9b1VBDG1PKtjLKMAxj66qH0hO6PAw%3D%3D
"""


# Save cookies to temp file so yt-dlp can use it
cookie_file = tempfile.NamedTemporaryFile(delete=False)
cookie_file.write(COOKIES.encode('utf-8'))
cookie_file.flush()
cookie_file.close()

# ---- Simple in-memory cache ----
CACHE = {}
CACHE_TTL = 60 * 60  # 1 hour

@app.route("/")
def home():
    return "yt cdn resolver is alive baby"

@app.route("/down")
def down():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    # Serve from cache if fresh
    now = time.time()
    if url in CACHE and now - CACHE[url]["timestamp"] < CACHE_TTL:
        return jsonify({
            "audio": CACHE[url]["audio"],
            "title": CACHE[url]["title"],
            "cached": True
        })

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
        "cookiefile": cookie_file.name,
        "format": "bestaudio",  # Force audio-only formats
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown Title")

            # Only audio formats (filter out any with video)
            audio_formats = [
                f for f in info.get("formats", [])
                if f.get("acodec") != "none" and f.get("vcodec") == "none"
            ]
            if not audio_formats:
                return jsonify({"error": "No pure audio formats found"}), 404

            # Sort by audio bitrate ascending (lowest first)
            audio_formats.sort(key=lambda f: f.get("abr", 0) or 0)
            lowest_audio = audio_formats[0]
            audio_url = lowest_audio.get("url")

            if not audio_url:
                return jsonify({"error": "Could not extract audio URL"}), 500

            # Store in cache
            CACHE[url] = {
                "audio": audio_url,
                "title": title,
                "timestamp": now
            }

            return jsonify({
                "audio": audio_url,
                "title": title,
                "cached": False
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)
