from flask import Flask, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import time
import subprocess

app = Flask(__name__)

# ---- Hardcoded cookies for YouTube ----
COOKIES = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	TRUE	1780289559	__Secure-3PAPISID	FZvxNUJUwn5ikq_n/AGOLeNFb5Ncbyhz98
.youtube.com	TRUE	/	TRUE	1780289559	__Secure-3PSID	g.a000wQhyu9KGfG90e3B_32ZqF1Lu6TPTeeUHD78Iim-HbBlZvY6aBwlK2mM2W01dXC52hGF-iQACgYKATASARISFQHGX2MiGMi-P9Hm03IdPaEoe-YOuBoVAUF8yKrlyk0KPcGPyTwdXgFYL7p_0076
.youtube.com	TRUE	/	TRUE	1780289559	LOGIN_INFO	AFmmF2swRQIgW4pDUh7SJVBl82E1gLDV3Z2_Zm0_vnAwX3NXxF8BnQcCIQCsCYgIlHFboGFreetoMHSNilWY8_gAwxltF7KZdgm9uw:QUQ3MjNmeUUxYTNuMFNVcmhPZ19GNkhqd2RqaFdodGZhMTMzTHpObERpZHV1VHZqZ1FiUU9FVldvUXJLX1QyOUliT1FjME9MTWJ5SkdxcjI4c0xjVndrOUVTRnlHUWs1d1VXSi0wQlhCdTI4UDVMcGI1SkVDSFpDN2dVT2JpX3ZSU19CU0VMNy05bExLdFlkOFVPSWZmNGR2WGtQRlZjZk53
.youtube.com	TRUE	/	TRUE	1794078362	PREF	f6=40000000&tz=Asia.Colombo&f7=100
.youtube.com	TRUE	/	TRUE	1791054350	__Secure-1PSIDTS	sidts-CjIBmkD5S_iHLoJqaFWUr6SztS3bNnb9egMCzum5uoyriCvS94izWjBRBVzwCwVhOTdPVRAA
.youtube.com	TRUE	/	TRUE	1791054350	__Secure-3PSIDTS	sidts-CjIBmkD5S_iHLoJqaFWUr6SztS3bNnb9egMCzum5uoyriCvS94izWjBRBVzwCwVhOTdPVRAA
.youtube.com	TRUE	/	FALSE	1759518367	ST-hcbf8d	session_logininfo=AFmmF2swRQIgW4pDUh7SJVBl82E1gLDV3Z2_Zm0_vnAwX3NXxF8BnQcCIQCsCYgIlHFboGFreetoMHSNilWY8_gAwxltF7KZdgm9uw%3AQUQ3MjNmeUUxYTNuMFNVcmhPZ19GNkhqd2RqaFdodGZhMTMzTHpObERpZHV1VHZqZ1FiUU9FVldvUXJLX1QyOUliT1FjME9MTWJ5SkdxcjI4c0xjVndrOUVTRnlHUWs1d1VXSi0wQlhCdTI4UDVMcGI1SkVDSFpDN2dVT2JpX3ZSU19CU0VMNy05bExLdFlkOFVPSWZmNGR2WGtQRlZjZk53
.youtube.com	TRUE	/	FALSE	1759518366	ST-1762dx4	itct=CNsDENwwIhMIs6_k19yIkAMVh6BmAh2j7S25MgpnLWhpZ2gtcmVjWg9GRXdoYXRfdG9fd2F0Y2iaAQYQjh4YngHKAQR_0xsj&csn=kUfNdGdV8yEmSRM-&session_logininfo=AFmmF2swRQIgW4pDUh7SJVBl82E1gLDV3Z2_Zm0_vnAwX3NXxF8BnQcCIQCsCYgIlHFboGFreetoMHSNilWY8_gAwxltF7KZdgm9uw%3AQUQ3MjNmeUUxYTNuMFNVcmhPZ19GNkhqd2RqaFdodGZhMTMzTHpObERpZHV1VHZqZ1FiUU9FVldvUXJLX1QyOUliT1FjME9MTWJ5SkdxcjI4c0xjVndrOUVTRnlHUWs1d1VXSi0wQlhCdTI4UDVMcGI1SkVDSFpDN2dVT2JpX3ZSU19CU0VMNy05bExLdFlkOFVPSWZmNGR2WGtQRlZjZk53&endpoint=%7B%22clickTrackingParams%22%3A%22CNsDENwwIhMIs6_k19yIkAMVh6BmAh2j7S25MgpnLWhpZ2gtcmVjWg9GRXdoYXRfdG9fd2F0Y2iaAQYQjh4YngHKAQR_0xsj%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fwatch%3Fv%3Dd4Q6RvGSbs4%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_WATCH%22%2C%22rootVe%22%3A3832%7D%7D%2C%22watchEndpoint%22%3A%7B%22videoId%22%3A%22d4Q6RvGSbs4%22%2C%22watchEndpointSupportedOnesieConfig%22%3A%7B%22html5PlaybackOnesieConfig%22%3A%7B%22commonConfig%22%3A%7B%22url%22%3A%22https%3A%2F%2Frr1---sn-icnxg8pjxn-qxae.googlevideo.com%2Finitplayback%3Fsource%3Dyoutube%26oeis%3D1%26c%3DWEB%26oad%3D3200%26ovd%3D3200%26oaad%3D11000%26oavd%3D11000%26ocs%3D700%26oewis%3D1%26oputc%3D1%26ofpcc%3D1%26siu%3D1%26msp%3D1%26odepv%3D1%26id%3D77843a46f1926ece%26ip%3D43.227.227.210%26initcwndbps%3D1688750%26mt%3D1759517736%26oweuc%3D%26pxtags%3DCg4KAnR4Egg1MTM1NzQzNw%26rxtags%3DCg4KAnR4Egg1MTM1NzQzNQ%252CCg4KAnR4Egg1MTM1NzQzNg%252CCg4KAnR4Egg1MTM1NzQzNw%22%7D%7D%7D%7D%7D
.youtube.com	TRUE	/	TRUE	1791054362	__Secure-3PSIDCC	AKEyXzUAIaUke5f9AY0gGka0B-vpf5mUu0no1EqrkftA1tOIOlnuMD0DzwCM7ugNgWZR7FO1bQ
.youtube.com	TRUE	/	TRUE	1759518962	CONSISTENCY	AKreu9sD6vnhQz2pcrCfhMz8lflUk6SSUWA1J4fOz2hFGk5CMbITgVkFUkHvu8Zb5E0uR3WN39Gf5wKxmbXOsb9b_dbsaHn_dsnXEXf-snV0k3HpYf-U3KK2uqFokWro2jMbxsE2nrZDE12-DTpmj5pv
.youtube.com	TRUE	/	TRUE	1775070354	VISITOR_INFO1_LIVE	ioWo_mpCzcg
.youtube.com	TRUE	/	TRUE	1775070354	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgNg%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	YHVuW52B7SE
.youtube.com	TRUE	/	TRUE	1775070347	__Secure-ROLLOUT_TOKEN	CKiBna-Th9vlEhDm7O66tfeMAxj90-HX3IiQAw%3D%3D
""" # truncated for brevity; keep all lines from your original COOKIES

# Save cookies to temp file for yt-dlp
cookie_file = tempfile.NamedTemporaryFile(delete=False)
cookie_file.write(COOKIES.encode('utf-8'))
cookie_file.flush()
cookie_file.close()

# ---- Simple in-memory cache for YouTube ----
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

# ---- Spotify download endpoint (streams audio directly) ----
@app.route("/spotify-down")
def spotify_down():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    cookies_file = r"C:\Users\PC\Downloads\spotifycookies.txt"
    temp_dir = tempfile.mkdtemp()  # temporary output folder

    cmd = [
        "votify",
        "--disable-wvd",
        "--cookies-path", cookies_file,
        "--audio-quality", "aac-medium",  # low-quality audio
        "--output-path", temp_dir,
        url
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Find the actual audio file inside the temp directory
        audio_file_path = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith((".ogg", ".mp3", ".m4a", ".wav")):
                    audio_file_path = os.path.join(root, file)
                    break
            if audio_file_path:
                break

        if not audio_file_path:
            return jsonify({"error": "No audio file found after votify download"}), 500

        # Stream the file directly to the user
        return send_file(audio_file_path, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Votify failed", "details": e.stderr}), 500

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        if os.path.exists(cookie_file.name):
            os.unlink(cookie_file.name)

