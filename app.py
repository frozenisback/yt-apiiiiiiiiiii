from flask import Flask, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import time
import subprocess
import logging

app = Flask(__name__)

# ---- Auto Install Deno if missing ----
def ensure_deno_installed():
    try:
        result = subprocess.run(["deno", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[INIT] Deno detected: {result.stdout.strip()}")
            return True
        else:
            print("[INIT] Deno not found, attempting to install...")
    except FileNotFoundError:
        print("[INIT] Deno not found, installing...")

    try:
        subprocess.run("curl -fsSL https://deno.land/install.sh | sh", shell=True, check=True)
        deno_path = os.path.expanduser("~/.deno/bin/deno")
        if os.path.exists(deno_path):
            os.environ["PATH"] = f"{os.path.expanduser('~/.deno/bin')}:{os.environ['PATH']}"
            print("[INIT] Deno installed successfully and added to PATH.")
            return True
        else:
            print("[INIT ERROR] Deno install script ran but binary not found.")
            return False
    except Exception as e:
        print(f"[INIT ERROR] Failed to install Deno: {e}")
        return False

# ---- yt-dlp EJS Solver Initializer ----
def init_yt_dlp_solver():
    try:
        if not ensure_deno_installed():
            print("[INIT WARNING] Deno missing. Signature solving may fail.")

        # Update yt-dlp to nightly for latest cipher fixes
        subprocess.run(["yt-dlp", "--update-to", "nightly"], check=False)

        # Clear old caches
        subprocess.run(["yt-dlp", "--rm-cache-dir"], check=False)

        # Preload EJS challenge solver
        subprocess.run([
            "yt-dlp",
            "--remote-components", "ejs:github",
            "--simulate", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ], check=False)

        print("[INIT] yt-dlp EJS challenge solver initialized successfully.")
    except Exception as e:
        print(f"[INIT ERROR] Failed to initialize yt-dlp EJS solver: {e}")

# ---- COOKIES ----
COOKIES = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.
.youtube.com	TRUE	/	FALSE	1793522371	HSID	AdzGzDS-sv2Dxh6gj
.youtube.com	TRUE	/	TRUE	1793522371	SSID	ANodiydGwjRxMjhLQ
.youtube.com	TRUE	/	FALSE	1793522371	APISID	cifAe6-LMoB3BUto/AwbmzxwAD66JAoIw_
"""  # truncated; use your full cookies

cookie_file = tempfile.NamedTemporaryFile(delete=False)
cookie_file.write(COOKIES.encode("utf-8"))
cookie_file.flush()
cookie_file.close()

# ---- Simple Cache ----
CACHE = {}
CACHE_TTL = 60 * 60  # 1 hour
PLAYER_CLIENTS = ["android", "ios", "tvhtml5", "web"]

@app.route("/")
def home():
    return "yt cdn resolver is alive baby"

@app.route("/down")
def down():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

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
        "format": "249",
        "youtube_include_dash_manifest": False,
        "extract_flat": False,
        "force_generic_extractor": False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown Title")
            audio_url = info.get("url")

            if not audio_url:
                return jsonify({"error": "Could not extract audio URL"}), 500

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

# ---- Debug Endpoint ----
logging.basicConfig(level=logging.DEBUG)

@app.route("/debug-down")
def debug_down():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    results = {}
    for client in PLAYER_CLIENTS:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "cookiefile": cookie_file.name,
            "format": "bestaudio/best",
            "player_client": client,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get("title", "Unknown Title")
                formats = info.get("formats", [])
                urls = [
                    {
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "abr": f.get("abr"),
                        "url": f.get("url"),
                    }
                    for f in formats if f.get("url")
                ]
                if not urls and info.get("url"):
                    urls.append({
                        "format_id": "direct",
                        "ext": info.get("ext"),
                        "abr": info.get("abr"),
                        "url": info.get("url"),
                    })

                results[client] = {"title": title, "urls": urls}
        except Exception as e:
            results[client] = {"error": str(e)}

    return jsonify(results)

# ---- Spotify Downloader ----
@app.route("/spotify-down")
def spotify_down():
    url = request.args.get("url")
    if not url:
        logging.error("Missing url parameter")
        return jsonify({"error": "Missing url parameter"}), 400

    cookies_file = "spotifycookies.txt"
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Using persistent output directory: {output_dir}")

    cmd = [
        "votify",
        "--disable-wvd",
        "--cookies-path", cookies_file,
        "--audio-quality", "aac-medium",
        "--output-path", output_dir,
        url
    ]
    logging.info(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logging.debug(f"STDOUT: {result.stdout}")
        logging.debug(f"STDERR: {result.stderr}")

        audio_file_path = None
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith((".ogg", ".mp3", ".m4a", ".wav")):
                    audio_file_path = os.path.join(root, file)
                    logging.info(f"Found audio file: {audio_file_path}")
                    break
            if audio_file_path:
                break

        if not audio_file_path:
            logging.error("No audio file found in output directory")
            return jsonify({"error": "No audio file found after votify download"}), 500

        return send_file(audio_file_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        logging.error(f"Votify failed: {e.stderr}")
        return jsonify({"error": "Votify failed", "details": e.stderr}), 500
    except Exception as e:
        logging.exception("Unexpected error in spotify_down")
        return jsonify({"error": str(e)}), 500

# ---- Run App ----
if __name__ == "__main__":
    init_yt_dlp_solver()
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)
