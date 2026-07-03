import yt_dlp

def get_info(url):
    with yt_dlp.YoutubeDL({}) as ydl:
        return ydl.extract_info(url, download=False)


def download_video(url, quality="best"):
    q = {
        "best": "best",
        "1080": "bestvideo[height<=1080]+bestaudio/best",
        "720": "bestvideo[height<=720]+bestaudio/best",
        "360": "bestvideo[height<=360]+bestaudio/best",
    }

    opts = {
        "format": q.get(quality, "best"),
        "outtmpl": "video.%(ext)s",
        "merge_output_format": "mp4"
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)

    return "video.mp4"


def download_audio(url):
    opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)

    return "audio.mp3"
