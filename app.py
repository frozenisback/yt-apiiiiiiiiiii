from flask import Flask, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import time
import subprocess
import logging

app = Flask(__name__)

# ---- Hardcoded cookies for YouTube ----
COOKIES = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	FALSE	1795761542	HSID	AjLj4GUKUGmVndVbE
.youtube.com	TRUE	/	TRUE	1795761542	SSID	AlPUBLp0uW2rFM-rb
.youtube.com	TRUE	/	FALSE	1795761542	APISID	QZ8D_LY2atENWTIn/AdgoRXpYh0uaQjsKd
.youtube.com	TRUE	/	TRUE	1795761542	SAPISID	Gz-FjS4oNW2jywOV/AkD9DOiTICMtDZvoW
.youtube.com	TRUE	/	TRUE	1795761542	__Secure-1PAPISID	Gz-FjS4oNW2jywOV/AkD9DOiTICMtDZvoW
.youtube.com	TRUE	/	TRUE	1795761542	__Secure-3PAPISID	Gz-FjS4oNW2jywOV/AkD9DOiTICMtDZvoW
.youtube.com	TRUE	/	TRUE	1786033029	LOGIN_INFO	AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ:QUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	TRUE	1795761551	PREF	f6=40000000&tz=Asia.Colombo&f7=100
.youtube.com	TRUE	/	FALSE	1795761542	SID	g.a0002wgBqIEQrO5eeehruVj0AoFkzUm4_bkBr97jU9axjDVNqKv1O6aKnlHdm-Z3CPhfh5xJAgACgYKAQgSARMSFQHGX2MiT_oF8iuQdu10KcGaNZwRJBoVAUF8yKqsUo0x1FAl8lahXNN3Dnpm0076
.youtube.com	TRUE	/	TRUE	1795761542	__Secure-1PSID	g.a0002wgBqIEQrO5eeehruVj0AoFkzUm4_bkBr97jU9axjDVNqKv1PwcrYeO7YfhoVJIq8DmTpAACgYKAZoSARMSFQHGX2Mix28Hb1WCmI4mAhSG9HTD9BoVAUF8yKrzBXfUNeHauI1K5ck29Omr0076
.youtube.com	TRUE	/	TRUE	1795761542	__Secure-3PSID	g.a0002wgBqIEQrO5eeehruVj0AoFkzUm4_bkBr97jU9axjDVNqKv10iiw5Z4SDkQXa6MoHDFJYQACgYKAZISARMSFQHGX2MiMzX3IvTzK7AwUrLLE_j2XRoVAUF8yKolH9xoxrSn9nOb4moLf9p80076
.youtube.com	TRUE	/	FALSE	1761201554	ST-3opvp5	session_logininfo=AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ%3AQUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	FALSE	1761201554	ST-1ngtmcv	itct=CKoFENwwIhMIq5XjkNu5kAMVS5VmAh2CnTUkMgpnLWhpZ2gtcmVjWg9GRXdoYXRfdG9fd2F0Y2iaAQYQjh4YngHKAQSF5E4t&csn=33-EWvq-qp9RDudy&session_logininfo=AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ%3AQUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR&endpoint=%7B%22clickTrackingParams%22%3A%22CKoFENwwIhMIq5XjkNu5kAMVS5VmAh2CnTUkMgpnLWhpZ2gtcmVjWg9GRXdoYXRfdG9fd2F0Y2iaAQYQjh4YngHKAQSF5E4t%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fwatch%3Fv%3DqIiYlBkYswk%26list%3DRDqIiYlBkYswk%26start_radio%3D1%26pp%3DoAcB%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_WATCH%22%2C%22rootVe%22%3A3832%7D%7D%2C%22watchEndpoint%22%3A%7B%22videoId%22%3A%22qIiYlBkYswk%22%2C%22playlistId%22%3A%22RDqIiYlBkYswk%22%2C%22params%22%3A%22OAHAAQG4BQE%253D%22%2C%22playerParams%22%3A%22oAcB%22%2C%22loggingContext%22%3A%7B%22vssLoggingContext%22%3A%7B%22serializedContextData%22%3A%22Gg1SRHFJaVlsQmtZc3dr%22%7D%7D%2C%22watchEndpointSupportedOnesieConfig%22%3A%7B%22html5PlaybackOnesieConfig%22%3A%7B%22commonConfig%22%3A%7B%22url%22%3A%22https%3A%2F%2Frr2---sn-icnxg8pjxn-qxae.googlevideo.com%2Finitplayback%3Fsource%3Dyoutube%26oeis%3D1%26c%3DWEB%26oad%3D3200%26ovd%3D3200%26oaad%3D11000%26oavd%3D11000%26ocs%3D700%26oewis%3D1%26oputc%3D1%26ofpcc%3D1%26siu%3D1%26msp%3D1%26odepv%3D1%26oreouc%3D1%26id%3Da88898941918b309%26ip%3D43.227.225.120%26initcwndbps%3D1667500%26mt%3D1761201405%26oweuc%3D%22%7D%7D%7D%7D%7D
.youtube.com	TRUE	/	FALSE	1761201555	ST-xuwub9	session_logininfo=AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ%3AQUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	TRUE	1792737551	__Secure-1PSIDTS	sidts-CjIBmkD5S21xcrfSUb6xyNzzl6T3fwtgIv1WEZyF6JdPGIyPgfsxIHfYwtImrelrwkw4mRAA
.youtube.com	TRUE	/	TRUE	1792737551	__Secure-3PSIDTS	sidts-CjIBmkD5S21xcrfSUb6xyNzzl6T3fwtgIv1WEZyF6JdPGIyPgfsxIHfYwtImrelrwkw4mRAA
.youtube.com	TRUE	/	FALSE	1792737551	SIDCC	AKEyXzWYnoBtRcsfy-D6oxyq4lXPbsjxcX35aeFryKsWcSczsGiqiiT_9qID3SLyOZ9_J-6nxA
.youtube.com	TRUE	/	TRUE	1792737551	__Secure-1PSIDCC	AKEyXzX78wa9fpdA9Z1efMAPNpjBlA7NCtXLth6h9qzaV1mlDHGLTpjBEy_Fk1NDk9QyTk2umvc
.youtube.com	TRUE	/	TRUE	1792737551	__Secure-3PSIDCC	AKEyXzVoGsRmne7daLe1BGQAJGp6iO3UQAwXWZqTkun8dQYuS2-3X_tLpAqXWhC9Xk3ZraCsMA
.youtube.com	TRUE	/	TRUE	1776753547	VISITOR_INFO1_LIVE	7w1ogUx5pFY
.youtube.com	TRUE	/	TRUE	1776753547	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgFQ%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	AcmORRYwot8
.youtube.com	TRUE	/	TRUE	1776753542	__Secure-ROLLOUT_TOKEN	CP36gob5nIvrhgEQ5IaYkvCejwMYnLm0jtu5kAM%3D
""" # truncated for brevity; keep all lines from your original COOKIES

# Save cookies to temp file for yt-dlp
cookie_file = tempfile.NamedTemporaryFile(delete=False)
cookie_file.write(COOKIES.encode('utf-8'))
cookie_file.flush()
cookie_file.close()

# ---- Simple in-memory cache for YouTube ----
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
        "format": "249",  # force Opus 52kbps
        "youtube_include_dash_manifest": False,
        "extract_flat": False,
        "force_generic_extractor": False,
        "player_client": "android",  # forces old client giving direct HTTP audio
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown Title")

            audio_url = info.get("url")
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

                # yt-dlp may have multiple formats
                formats = info.get("formats", [])
                urls = []
                for f in formats:
                    if f.get("url"):
                        urls.append({
                            "format_id": f.get("format_id"),
                            "ext": f.get("ext"),
                            "abr": f.get("abr"),
                            "url": f.get("url")
                        })

                # fallback if "formats" not present
                if not urls and info.get("url"):
                    urls.append({
                        "format_id": "direct",
                        "ext": info.get("ext"),
                        "abr": info.get("abr"),
                        "url": info.get("url")
                    })

                results[client] = {
                    "title": title,
                    "urls": urls
                }
        except Exception as e:
            results[client] = {"error": str(e)}

    return jsonify(results)


@app.route("/spotify-down")
def spotify_down():
    url = request.args.get("url")
    if not url:
        logging.error("Missing url parameter")
        return jsonify({"error": "Missing url parameter"}), 400

    cookies_file = "spotifycookies.txt"
    output_dir = "downloads"  # persistent folder
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

        # Find the downloaded audio file in the output folder
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


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)

