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

.youtube.com	TRUE	/	TRUE	1793163125	__Secure-3PAPISID	Ku6vwXGG4P_uFc1W/Aa6fcW7uTMD1U0Yrf
.youtube.com	TRUE	/	FALSE	1793163125	HSID	AG4luAIdd_BQLfRio
.youtube.com	TRUE	/	TRUE	1793163125	SSID	AbqInrik0HFolZUer
.youtube.com	TRUE	/	FALSE	1793163125	APISID	MOeFxc2lmBsatd9y/Aa72W4P--g6WfgXam
.youtube.com	TRUE	/	TRUE	1793163125	SAPISID	Ku6vwXGG4P_uFc1W/Aa6fcW7uTMD1U0Yrf
.youtube.com	TRUE	/	TRUE	1793163125	__Secure-1PAPISID	Ku6vwXGG4P_uFc1W/Aa6fcW7uTMD1U0Yrf
.youtube.com	TRUE	/	TRUE	1771521433	LOGIN_INFO	AFmmF2swRAIgd6_GSw-xY8BuJbGJGD4WT0Bv75yi89fq4IywtlHlLA4CIHxwbF9lbicSABMgDZQh6pTj3HDddYVBqJ60hqyMGexo:QUQ3MjNmekNaSXhtR0VjWjdzLS1lOFFpLXJCTjhWRUxxdmJEU3lRZVJCeXk4dmlHV1FOTm00N1NJNHZmb2xvY2hJdmp2N0xaMUdFT3IxS29oY1hYdnB6aWlDejVoOHhWRHFHNFhZOGxxWllDVnJuNjNxb2t5ajlDQTMyY1EtejkyR1ZSTlJnNzNWWldneFJKbERQczg4M2JGc09sZEc4bnJB
.youtube.com	TRUE	/	TRUE	1793163141	PREF	f6=40000000&tz=Asia.Colombo&f7=100
.youtube.com	TRUE	/	FALSE	1793163125	SID	g.a0001gijJOBsXybjo3E2gY5pgW6zs5T0o9XdQz5q6AyLv4rwlo2K3IW-b9ScWKz3JmQGCcr1IgACgYKAU0SARISFQHGX2MiP_SE3ZGXKJIf1oUu2aSJ9hoVAUF8yKrG1zzKwrjfqwUDbzwLHhNE0076
.youtube.com	TRUE	/	TRUE	1793163125	__Secure-1PSID	g.a0001gijJOBsXybjo3E2gY5pgW6zs5T0o9XdQz5q6AyLv4rwlo2KQqZkyHP-y7o0e1nz1FlzdQACgYKAYESARISFQHGX2MiNANyzTvj8vIb_ig6vN96fRoVAUF8yKqh4o8hPCw0F5_JW4QmCxaX0076
.youtube.com	TRUE	/	TRUE	1793163125	__Secure-3PSID	g.a0001gijJOBsXybjo3E2gY5pgW6zs5T0o9XdQz5q6AyLv4rwlo2Kv-GX0oSs4KVoohHOlumdawACgYKAd8SARISFQHGX2MifSw06cMP9YVCpKfXljBYKhoVAUF8yKrL3H2dvMj4aU-OhT_hSBak0076
.youtube.com	TRUE	/	TRUE	1790139129	__Secure-1PSIDTS	sidts-CjIBmkD5S-VKd9SDGFicrT0g0WggZnbdi9UaFv2LqF6gI4MNOFbS5E33EFSQE9NXn5q6rBAA
.youtube.com	TRUE	/	TRUE	1790139129	__Secure-3PSIDTS	sidts-CjIBmkD5S-VKd9SDGFicrT0g0WggZnbdi9UaFv2LqF6gI4MNOFbS5E33EFSQE9NXn5q6rBAA
.youtube.com	TRUE	/	FALSE	1790139135	SIDCC	AKEyXzU2LnPNOX0Xoq3Hoh2FgqO7VeRNeZ23Nx1eD--bWx7A2ZDBka-RVhcwAAhjIEEveSfhxbw
.youtube.com	TRUE	/	TRUE	1790139135	__Secure-1PSIDCC	AKEyXzX2x4JKpXD_g8M7lFO26v1TsEq9iXx-oSHEMgJXXM4Eo6oMEqo4nEvQWwgbRg0Vwg5PDw
.youtube.com	TRUE	/	TRUE	1790139135	__Secure-3PSIDCC	AKEyXzXt7WuS8D0VjIMXUNFs4brjfeWxsziJPAz1XV_JjYVS11p9lt9unWXlWT_I4Z66LJ58Nw
.youtube.com	TRUE	/	TRUE	1758603744	CONSISTENCY	AKreu9s6beQl_ZqvDb8YHQULAVF5KXMZ5WaVjZ-nVAkGtdOY2fzgbDXlFZVlYG-MkzaZtiY8eygP2NFp8-XbL2mHLspSIPinLWocSlqGMwjrFfTqdAgAsj-QCkM
.youtube.com	TRUE	/	FALSE	1758603149	ST-1ylrgch	itct=CBgQ7fkGGAEiEwjJu9ufi-6PAxUA7aACHfVoFrKaAQIIOsoBBHm5Gsk%3D&csn=GvM1oJ5hc9lpgljs&session_logininfo=AFmmF2swRAIgd6_GSw-xY8BuJbGJGD4WT0Bv75yi89fq4IywtlHlLA4CIHxwbF9lbicSABMgDZQh6pTj3HDddYVBqJ60hqyMGexo%3AQUQ3MjNmekNaSXhtR0VjWjdzLS1lOFFpLXJCTjhWRUxxdmJEU3lRZVJCeXk4dmlHV1FOTm00N1NJNHZmb2xvY2hJdmp2N0xaMUdFT3IxS29oY1hYdnB6aWlDejVoOHhWRHFHNFhZOGxxWllDVnJuNjNxb2t5ajlDQTMyY1EtejkyR1ZSTlJnNzNWWldneFJKbERQczg4M2JGc09sZEc4bnJB&endpoint=%7B%22clickTrackingParams%22%3A%22CBgQ7fkGGAEiEwjJu9ufi-6PAxUA7aACHfVoFrKaAQIIOsoBBHm5Gsk%3D%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fshorts%2FwJ8xitL3ASA%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_SHORTS%22%2C%22rootVe%22%3A37414%7D%7D%2C%22reelWatchEndpoint%22%3A%7B%22videoId%22%3A%22wJ8xitL3ASA%22%2C%22playerParams%22%3A%228AEByAMTwATgnJGD9uqs-L4BogYVAXaSymAw3yMLqEO7InZYPIavpT8fqgZDQU9BckJGdXpKTHFjX2pkSDI2ckkySEJVWkIyUXRUYnFwYWZDb3dxdzFWb2VaVjhGNEQ1OW9qTUlEN0FWanRSSzlUb5AHArgHlYjcn4vujwPIBwE%253D%22%2C%22thumbnail%22%3A%7B%22thumbnails%22%3A%5B%7B%22url%22%3A%22https%3A%2F%2Fi.ytimg.com%2Fvi%2FwJ8xitL3ASA%2Fframe0.jpg%22%2C%22width%22%3A720%2C%22height%22%3A1280%7D%5D%2C%22isOriginalAspectRatio%22%3Atrue%7D%2C%22overlay%22%3A%7B%22reelPlayerOverlayRenderer%22%3A%7B%22style%22%3A%22REEL_PLAYER_OVERLAY_STYLE_SHORTS%22%2C%22trackingParams%22%3A%22CBkQsLUEIhMIybvbn4vujwMVAO2gAh31aBay%22%2C%22reelPlayerNavigationModel%22%3A%22REEL_PLAYER_NAVIGATION_MODEL_UNSPECIFIED%22%7D%7D%2C%22params%22%3A%22CA8aEwiViNyfi-6PAxUWq2MGHeC3GqIqAKIBEwiZvYqfi-6PAxVNMbcAHVBdK8O6ARhVQ0N4OFF2WnY2Ul9QVHFrVXltSnFVYnc%253D%22%2C%22loggingContext%22%3A%7B%22vssLoggingContext%22%3A%7B%22serializedContextData%22%3A%22CgIIDA%253D%253D%22%7D%2C%22qoeLoggingContext%22%3A%7B%22serializedContextData%22%3A%22CgIIDA%253D%253D%22%7D%7D%2C%22ustreamerConfig%22%3A%22CAw%3D%22%7D%7D
.youtube.com	TRUE	/	FALSE	1758603149	ST-1b	disableCache=false&itct=CB8Q8KgHGAAiEwiL_O6Zi-6PAxWNxaACHXsWBnjKAQR5uRrJ&csn=u7ByuKvJmC_r7Vm4&session_logininfo=AFmmF2swRAIgd6_GSw-xY8BuJbGJGD4WT0Bv75yi89fq4IywtlHlLA4CIHxwbF9lbicSABMgDZQh6pTj3HDddYVBqJ60hqyMGexo%3AQUQ3MjNmekNaSXhtR0VjWjdzLS1lOFFpLXJCTjhWRUxxdmJEU3lRZVJCeXk4dmlHV1FOTm00N1NJNHZmb2xvY2hJdmp2N0xaMUdFT3IxS29oY1hYdnB6aWlDejVoOHhWRHFHNFhZOGxxWllDVnJuNjNxb2t5ajlDQTMyY1EtejkyR1ZSTlJnNzNWWldneFJKbERQczg4M2JGc09sZEc4bnJB&endpoint=%7B%22clickTrackingParams%22%3A%22CB8Q8KgHGAAiEwiL_O6Zi-6PAxWNxaACHXsWBnjKAQR5uRrJ%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2F%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_BROWSE%22%2C%22rootVe%22%3A3854%2C%22apiUrl%22%3A%22%2Fyoutubei%2Fv1%2Fbrowse%22%7D%7D%2C%22browseEndpoint%22%3A%7B%22browseId%22%3A%22FEwhat_to_watch%22%7D%7D
.youtube.com	TRUE	/	FALSE	1758603149	ST-yve142	session_logininfo=AFmmF2swRAIgd6_GSw-xY8BuJbGJGD4WT0Bv75yi89fq4IywtlHlLA4CIHxwbF9lbicSABMgDZQh6pTj3HDddYVBqJ60hqyMGexo%3AQUQ3MjNmekNaSXhtR0VjWjdzLS1lOFFpLXJCTjhWRUxxdmJEU3lRZVJCeXk4dmlHV1FOTm00N1NJNHZmb2xvY2hJdmp2N0xaMUdFT3IxS29oY1hYdnB6aWlDejVoOHhWRHFHNFhZOGxxWllDVnJuNjNxb2t5ajlDQTMyY1EtejkyR1ZSTlJnNzNWWldneFJKbERQczg4M2JGc09sZEc4bnJB
.youtube.com	TRUE	/	TRUE	1774155133	VISITOR_INFO1_LIVE	mz2_xmtQZ40
.youtube.com	TRUE	/	TRUE	1774155133	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgOg%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	svwPvmJAbX0
.youtube.com	TRUE	/	TRUE	1774155125	__Secure-ROLLOUT_TOKEN	CJThjtXguo751wEQufi9yZ34igMY9LLmmIvujwM%3D
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
