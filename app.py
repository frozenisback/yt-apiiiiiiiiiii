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

.youtube.com	TRUE	/	FALSE	1793160756	HSID	AjLj4GUKUGmVndVbE
.youtube.com	TRUE	/	TRUE	1793160756	SSID	AlPUBLp0uW2rFM-rb
.youtube.com	TRUE	/	FALSE	1793160756	APISID	QZ8D_LY2atENWTIn/AdgoRXpYh0uaQjsKd
.youtube.com	TRUE	/	TRUE	1793160756	SAPISID	Gz-FjS4oNW2jywOV/AkD9DOiTICMtDZvoW
.youtube.com	TRUE	/	TRUE	1793160756	__Secure-1PAPISID	Gz-FjS4oNW2jywOV/AkD9DOiTICMtDZvoW
.youtube.com	TRUE	/	TRUE	1793160756	__Secure-3PAPISID	Gz-FjS4oNW2jywOV/AkD9DOiTICMtDZvoW
.youtube.com	TRUE	/	TRUE	1786033029	LOGIN_INFO	AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ:QUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	TRUE	1793160761	PREF	f6=40000000&tz=Asia.Colombo&f7=100
.youtube.com	TRUE	/	FALSE	1793160756	SID	g.a0001ggBqJ9KvN8rWVjMcup3ixRqf2dh5fsgxmZEbZTsacK8Jl5rLIHP459rocXHqI0J4kuFagACgYKAewSARMSFQHGX2MictXbtFFI-wHCd7IqnmMKMBoVAUF8yKrgT9xMt-CX2DHjd0-wp-pD0076
.youtube.com	TRUE	/	TRUE	1793160756	__Secure-1PSID	g.a0001ggBqJ9KvN8rWVjMcup3ixRqf2dh5fsgxmZEbZTsacK8Jl5r3vsvHbLUV4k0YGZFNO_8AgACgYKARQSARMSFQHGX2MiKxSu5kKqVL9rzQJR00_9HhoVAUF8yKpoZ07Ux4vgf15LTXdK2h-_0076
.youtube.com	TRUE	/	TRUE	1793160756	__Secure-3PSID	g.a0001ggBqJ9KvN8rWVjMcup3ixRqf2dh5fsgxmZEbZTsacK8Jl5rO3aRdP8y1GzbWH87mnMCiAACgYKAWESARMSFQHGX2Mi6MINAjBI5wqEOsW67buvlhoVAUF8yKrJa8LNR9nBBE03-dQn_oQl0076
.youtube.com	TRUE	/	FALSE	1758600766	ST-tladcw	session_logininfo=AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ%3AQUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	FALSE	1758600769	ST-3opvp5	session_logininfo=AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ%3AQUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	FALSE	1758600766	ST-hcbf8d	session_logininfo=AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ%3AQUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	FALSE	1758600766	ST-xuwub9	session_logininfo=AFmmF2swRQIhAPJE9Wy4EJJ3velOot45M4SkHvO5aXTdBb7YP_ZUtN6zAiBA2TT8jtOUmt0ih543QvrhM1MoUZn6rbhTAWu9kP2VwQ%3AQUQ3MjNmekl6T0w2LWN6dU5mY3JYc2wzMTdWLWVqemNqR1FRMEFMc3pkNFQ3eWg3TzZTaW5WUWpNVVZvVDNDRVhGOVRIdGRMMlFZcmtaOVJRNzByUlpiYXdsUUdRODQ0SnBEWXVDMGVCSUpFYkRXa3lUMzBTMFA1dlFPZHBoQTZrOWRPMGpydlRrOWU1N1NFZ2NOcUZ5X042RC1HNl9yOXJR
.youtube.com	TRUE	/	TRUE	1758601362	CONSISTENCY	AKreu9vggeZHG-E4P2hLcP9H9xrlJFn1e8epkXMduWr17QULUQFew2OuFezbUymm2GiE-HZtFwp81xxshQs1Kp3iD8aliJepvGcLa8U_CKdtV3JrLPbJG_vwjBq5J9q7RGsxKhwIj9HSApfX4jAS576B
.youtube.com	TRUE	/	TRUE	1790136763	__Secure-1PSIDTS	sidts-CjIBmkD5S7OUPRC5VgqzIWYxQD-hXRINyDwzU3V0YpaM7HmflynTg-s58aIP_af_2K3WUxAA
.youtube.com	TRUE	/	TRUE	1790136763	__Secure-3PSIDTS	sidts-CjIBmkD5S7OUPRC5VgqzIWYxQD-hXRINyDwzU3V0YpaM7HmflynTg-s58aIP_af_2K3WUxAA
.youtube.com	TRUE	/	FALSE	1790136764	SIDCC	AKEyXzUAx8M8_v4Dn5maPQryyPCrb9PVGHYD1auRKT36jy9Yd9SfAghA59pOsvtvSbcKoOD-
.youtube.com	TRUE	/	TRUE	1790136764	__Secure-1PSIDCC	AKEyXzXgtq44rtGutIb2go99JYDMMAN_MbKH7POJOkcM52Kebzjgqoi_NbWRCLMr8fO5jf2P2g
.youtube.com	TRUE	/	TRUE	1790136764	__Secure-3PSIDCC	AKEyXzXvomhBr9ikgab2k9bMAa_UEJNF2AD3YYplzlXTV5UUX9ndZsCFlgmbTzF6yTyf4QCq
.youtube.com	TRUE	/	TRUE	1774152764	VISITOR_INFO1_LIVE	7w1ogUx5pFY
.youtube.com	TRUE	/	TRUE	1774152764	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgFQ%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	3RT9yl1Ru2Y
.youtube.com	TRUE	/	TRUE	1774152756	__Secure-ROLLOUT_TOKEN	CP36gob5nIvrhgEQ5IaYkvCejwMY1Yier4LujwM%3D
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
