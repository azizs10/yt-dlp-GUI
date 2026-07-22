"""
YT Downloader is a simple application with a modern GUI for downloading
videos from YouTube and other sites supported by yt-dlp.

Author: Aziz(azizs10)
License: Apache License 2.0
"""

import os
import threading
import queue 
import subprocess
import sys
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


APP_NAME = "YT Downloader"
APP_VERSION = "1.0.0"
DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Downloads")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("760x560")
        self.minsize(640, 580)

        self.msg_queue = queue.Queue()
        self.download_thread = None
        self.is_downloading = False

        self.output_dir = ctk.StringVar(value=DEFAULT_DOWNLOAD_DIR)
        self.url_var = ctk.StringVar()
        self.format_var = ctk.StringVar(value="Video (mp4)")
        self.quality_var = ctk.StringVar(value="Best quality")

        self._build_ui()
        self._poll_queue()

        if yt_dlp is None:
            self._log(
                " yt-dlp library not found. Install dependencies using:\n"
                "    pip install -r requirements.txt\n"
            )
        self.playlist = False

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # for radio button need to remember
        self.radio_var = ctk.IntVar(value=1)

        header = ctk.CTkLabel(
            self,
            text="YT Downloader",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        subtitle = ctk.CTkLabel(
            self,
            text="Download videos from YouTube and other sites powered by yt-dlp",
            font=ctk.CTkFont(size=13),
            text_color=("gray30", "gray70"),
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        ex = ctk.CTkLabel(
            self,
            text='Choose what to download: Video or PLaylist',
            font=ctk.CTkFont(size=13, weight="bold"),

        )
        ex.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        self.radio_frame = ctk.CTkFrame(master=self, fg_color="transparent")
        self.radio_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="w")

        self.radio_vd = ctk.CTkRadioButton(
            master=self.radio_frame,
            text='Video',
            command = self.radio_event,
            value = 1,
            variable = self.radio_var
        )
        self.radio_vd.pack(side='left', padx=(0, 15))

        self.radio_pl = ctk.CTkRadioButton(
            master=self.radio_frame,
            text='Playlist',
            command = self.radio_event,
            value = 2,
            variable = self.radio_var,
        )
        self.radio_pl.pack(side='left')

        url_frame = ctk.CTkFrame(self, corner_radius=12)
        url_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            url_frame, text="Video URL", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w")

        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.url_entry.grid(row=4, column=0, padx=15, pady=(0, 12), sticky="ew")

        options_frame = ctk.CTkFrame(self, corner_radius=12)
        options_frame.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        options_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            options_frame, text="Format", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w")
        self.format_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.format_var,
            values=["Video (mp4)", "Audio only (mp3)"],
            height=36,
        )
        self.format_menu.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(
            options_frame, text="Quality", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, padx=15, pady=(12, 2), sticky="w")
        self.quality_menu = ctk.CTkOptionMenu(
            options_frame,
            variable=self.quality_var,
            values=["Best quality", "1080p", "720p", "480p", "360p"],
            height=36,
        )
        self.quality_menu.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        folder_frame = ctk.CTkFrame(self, corner_radius=12)
        folder_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            folder_frame, text="Save Folder", font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w", columnspan=2)

        self.folder_entry = ctk.CTkEntry(
            folder_frame, textvariable=self.output_dir, height=38
        )
        self.folder_entry.grid(row=1, column=0, padx=(15, 5), pady=(0, 12), sticky="ew")

        self.browse_btn = ctk.CTkButton(
            folder_frame, text="Browse...", width=100, height=38, command=self._choose_folder
        )
        self.browse_btn.grid(row=1, column=1, padx=(5, 15), pady=(0, 12))

        self.download_btn = ctk.CTkButton(
            self,
            text="Download",
            height=46,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_download,
        )
        self.download_btn.grid(row=7, column=0, padx=20, pady=(15, 5), sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self, height=14)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=8, column=0, padx=20, pady=(5, 5), sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=9, column=0, padx=20, pady=(0, 5), sticky="w")

        self.grid_rowconfigure(10, weight=1)
        self.log_box = ctk.CTkTextbox(self, corner_radius=12, font=ctk.CTkFont(size=12))
        self.log_box.grid(row=8, column=0, padx=20, pady=(5, 20), sticky="nsew")
        self.log_box.configure(state="disabled")

    def radio_event(self):
        self.playlist = True if self.radio_var.get() == 2 else False

    def _choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir.get() or ".")
        if folder:
            self.output_dir.set(folder)

    def _log(self, text: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text: str):
        self.status_label.configure(text=text)

    def _start_download(self):
        if self.is_downloading:
            messagebox.showinfo(APP_NAME, "Download is already in progress, please wait.")
            return

        if yt_dlp is None:
            messagebox.showerror(
                APP_NAME,
                "The yt-dlp library is not installed.\nRun: pip install -r requirements.txt",
            )
            return

        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning(APP_NAME, "Please enter a video URL.")
            return

        out_dir = self.output_dir.get().strip() or DEFAULT_DOWNLOAD_DIR
        os.makedirs(out_dir, exist_ok=True)

        self.is_downloading = True
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        self._set_status("Preparing...")
        self._log(f"Starting download: {url}")

        self.download_thread = threading.Thread(
            target=self._download_worker, args=(url, out_dir), daemon=True
        )
        self.download_thread.start()

    def _download_worker(self, url: str, out_dir: str):
        def progress_hook(d):
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    fraction = downloaded / total
                    self.msg_queue.put(("progress", fraction))
                speed = d.get("_speed_str", "").strip()
                eta = d.get("_eta_str", "").strip()
                self.msg_queue.put(
                    ("status", f"Downloading... {d.get('_percent_str', '').strip()} "
                               f"| Speed: {speed} | ETA: {eta}")
                )
            elif d.get("status") == "finished":
                self.msg_queue.put(("status", "Processing file..."))
                self.msg_queue.put(("progress", 1.0))

        quality = self.quality_var.get()
        is_audio = self.format_var.get().startswith("Audio only")

        outtmpl = os.path.join(out_dir, "%(title)s.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "progress_hooks": [progress_hook],
            "noplaylist": self.playlist,
            "quiet": True,
            "no_warnings": True,
        }

        if is_audio:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        else:
            if quality == "Best quality":
                ydl_opts["format"] = "bestvideo+bestaudio/best"
            else:
                height = quality.replace("p", "")
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
                )
            ydl_opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "video")
            self.msg_queue.put(("done", title))
        except Exception as exc:
            self.msg_queue.put(("error", str(exc)))

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.msg_queue.get_nowait()
                if kind == "progress":
                    self.progress_bar.set(payload)
                elif kind == "status":
                    self._set_status(payload)
                elif kind == "done":
                    self._log(f"Done: {payload}")
                    self._set_status("Download completed")
                    self.progress_bar.set(1.0)
                    self._finish_download()
                elif kind == "error":
                    self._log(f"Error: {payload}")
                    self._set_status("Download error")
                    self._finish_download()
        except queue.Empty:
            pass
        self.after(150, self._poll_queue)

    def _finish_download(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text="Download")


def main():
    app = DownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
