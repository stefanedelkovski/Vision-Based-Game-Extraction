import yt_dlp


def download_video(url, resolution="480p", output_path="downloaded_video.mp4"):
    ydl_opts = {
        'format': f'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'outtmpl': output_path,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"Video downloaded to {output_path}")
    return output_path


if __name__ == "__main__":
    # Example usage
    video_url = 'https://kick.com/classybeef/videos/69bcc40a-85c7-47b9-966c-170f18e9b576'  # Replace this with the actual URL
    download_video(video_url)
