import os
import time
from pytubefix import YouTube
from pytubefix.exceptions import VideoUnavailable, RegexMatchError

file_size = 0
start_time = 0

def on_progress(stream, chunk, bytes_remaining):
    global file_size, start_time

    bytes_downloaded = file_size - bytes_remaining
    percent_completed = (bytes_downloaded / file_size) * 100

    elapsed_time = time.time() - start_time
    if elapsed_time == 0 or bytes_downloaded == 0:
        download_speed_mbps = 0
        eta_str = "ETA: --m --s"
    else:
        download_speed_mbps = (bytes_downloaded / (1024 * 1024)) / elapsed_time # Convert to MB/s
        time_remaining = bytes_remaining / (download_speed_mbps * 1024 * 1024) # Recalculate based on MB/s
        minutes, seconds = divmod(int(time_remaining), 60)
        eta_str = f"ETA: {minutes:02d}m {seconds:02d}s"

    bar_length = 20
    filled_bar = '█' * int(percent_completed / (100 / bar_length))
    empty_bar = '-' * (bar_length - len(filled_bar))

    print(f"\rDownloading: [{filled_bar}{empty_bar}] {percent_completed:.1f}% | Speed: {download_speed_mbps:.2f} MB/s | {eta_str}", end="")

def download_youtube_video(url):
    global file_size, start_time

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        
        print(f"\nDownloading: {yt.title}")

        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        if stream:
            file_size = stream.filesize
            
            downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
            os.makedirs(downloads_folder, exist_ok=True)

            print(f"Saving to: {downloads_folder}")
            
            start_time = time.time()

            stream.download(output_path=downloads_folder)
            
            print("\nDownload complete!")
            print(f"Video saved as: {os.path.join(downloads_folder, stream.default_filename)}")
        else:
            print("No suitable progressive MP4 stream found for download.")

    except VideoUnavailable:
        print("Error: The video is unavailable or restricted.")
    except RegexMatchError:
        print("Error: Invalid YouTube URL or video ID not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("\nPress Enter to exit in 3 seconds or press Enter to exit immediately...")
        time.sleep(3)

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_youtube_video(video_url)