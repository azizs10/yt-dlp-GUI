#  YT Downloader

A simple desktop application with a modern GUI for downloading video and audio from YouTube and other websites supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp).

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-green)

##  Features

- Download videos via link (YouTube and hundreds of other websites via yt-dlp)
- Extract audio to MP3 format
- Select video quality (Best, 1080p, 720p, 480p, 360p)
- Choose a destination folder to save files
- Real-time progress bar and download log
- Modern dark-themed interface powered by CustomTkinter
- You can choose to download 1 video or all the playlist

## Interface

The application consists of:
- An input field for pasting the video link;
- Format (video/audio) and quality selectors;
- A destination folder selection field with a "Browse..." button;
- A "Download" button, a progress bar, and a log window.

## Installation

1. Make sure you have **Python 3.9+** installed.
2. Install [FFmpeg](https://ffmpeg.org/download.html) — it is required by yt-dlp for merging video/audio tracks and converting to MP3. Ensure that the `ffmpeg` command is accessible in your terminal.
3. Clone the repository and install the dependencies:
4. Run main.py file

```bash
git clone [https://github.com/](https://github.com/)<your-username>/yt-downloader.git
cd yt-downloader
pip install -r requirements.txt
python main.py
