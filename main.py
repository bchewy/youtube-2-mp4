"""
Created by: Ibn Aleem (ibnaleem@outlook.com)
LICENSE: This script is under the MIT License.
GitHub: https://github.com/ibnaleem/youtube-2-mp4
PGP Fingerprint: 2024 7EC0 23F2 769E 6618  1C0F 581B 4A2A 862B BADE
PGP Key: https://github.com/ibnaleem/ibnaleem/blob/main/public_key.asc
"""

import os
from tqdm import tqdm
from pytubefix import YouTube
from datetime import datetime
from rich.console import Console

ascii_art = """
██╗   ██╗ ██████╗ ██╗   ██╗████████╗██╗   ██╗██████╗ ███████╗    ██████╗     ███╗   ███╗██████╗ ██╗  ██╗
╚██╗ ██╔╝██╔═══██╗██║   ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝    ╚════██╗    ████╗ ████║██╔══██╗██║  ██║
 ╚████╔╝ ██║   ██║██║   ██║   ██║   ██║   ██║██████╔╝█████╗       █████╔╝    ██╔████╔██║██████╔╝███████║
  ╚██╔╝  ██║   ██║██║   ██║   ██║   ██║   ██║██╔══██╗██╔══╝      ██╔═══╝     ██║╚██╔╝██║██╔═══╝ ╚════██║
   ██║   ╚██████╔╝╚██████╔╝   ██║   ╚██████╔╝██████╔╝███████╗    ███████╗    ██║ ╚═╝ ██║██║          ██║
   ╚═╝    ╚═════╝  ╚═════╝    ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝    ╚══════╝    ╚═╝     ╚═╝╚═╝          ╚═╝
                                                                                                        
"""

class YouTubeDownloader:
    def __init__(self) -> None:
        self.url = None
        self.youtube = None
        self.streams = None
        self.console = Console()
        self.multi_vid_array = []
        self.progress_bar = None
        self.downloaded_bytes = 0

    def styled_input(self, prompt: str, style=None):
        if style:
            self.console.print(prompt, style=style, end="")
        else:
            self.console.print(prompt, end="")
        return input()

    def get_video_url(self) -> None:
        url = self.styled_input("Enter YouTube Video URL: ", style="bold blue")

        # Normalize URL - add https:// if missing
        if url.startswith("youtube.com") or url.startswith("www.youtube.com"):
            url = "https://" + url
        elif not url.startswith("http"):
            self.console.print("[bold red]Invalid URL. Please try again.[/bold red]")
            self.get_video_url()
            return

        if not ("youtube.com" in url or "youtu.be" in url):
            self.console.print("[bold red]Invalid URL. Please try again.[/bold red]")
            self.get_video_url()
            return

        try:
            self.url = url
            self.youtube = YouTube(self.url, on_progress_callback=self.on_progress)
            self.streams = self.youtube.streams
        except Exception as e:
            self.console.print(f"[bold red]Error loading video: {str(e)}[/bold red]")
            self.console.print("[bold yellow]If this persists, try updating pytubefix: pip install --upgrade pytubefix[/bold yellow]")
            self.get_video_url()

    def main_menu(self):
        while True:
            os.system("clear" if not os.name == "nt" else "cls")
            self.console.print(ascii_art, justify="center", style="#D3869B bold")
            self.console.print(
                "[cyan]:: Download YouTube Videos ::[cyan]\n", justify="center", end=""
            )
            self.console.print(
                "1. Download Single Video      2. Download Multiple Videos     3. Exit",
                justify="center",
            )
            choice = self.styled_input("Enter your choice: ", style="bold green")
            if choice == "1":
                self.download_single_video()
            elif choice == "2":
                self.download_multiple_videos()
            elif choice == "3":
                break
            else:
                self.console.print(
                    "[bold red]Invalid choice. Please try again.[/bold red]"
                )

    def convert_seconds_to_hms(self, seconds) -> str:
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        if self.progress_bar is None:
            self.progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading")
        
        chunk_size = len(chunk)
        self.downloaded_bytes += chunk_size
        self.progress_bar.update(chunk_size)
        
        if bytes_remaining == 0:
            self.progress_bar.close()
            self.progress_bar = None
            self.downloaded_bytes = 0

    def convert_to_english_date(self, date_input) -> str:
        # Handle both datetime objects and strings
        if isinstance(date_input, datetime):
            date_object = date_input
        else:
            date_string = str(date_input)
            # Remove timezone offset if present (e.g., "-07:00" or "+00:00")
            import re
            date_string = re.sub(r'[+-]\d{2}:\d{2}$', '', date_string).strip()
            # Try parsing with seconds first, then without
            try:
                date_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    date_object = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
                except ValueError:
                    # Just parse the date part
                    date_object = datetime.strptime(date_string.split()[0], '%Y-%m-%d')
        
        english_date = date_object.strftime('%B %d %Y')
        return english_date

    def download_single_video(self, args: str = None):

        if not args:
            self.get_video_url()
        highest_resolution_stream = self.streams.get_highest_resolution()

        self.console.print(
            f"[bold red]:: {self.youtube.title} ::[bold red]\n",
            justify="center",
            end="",
        )
        video_length = self.convert_seconds_to_hms(self.youtube.length)
        video_views = "{:,}".format(self.youtube.views)
        pub_date = self.convert_to_english_date(self.youtube.publish_date)

        self.console.print(
            f"Views: {video_views}      Length: {video_length}      Published on {pub_date}",
            justify="center",
            end="",
            style="bold blue",
        )
        proceed = self.styled_input("Is this correct? (y/n) ", style="bold red")
        if proceed.lower() != "y" and proceed.lower() != "n":
            self.console.print("[bold red]Invalid choice. Please try again.[/bold red]")
            proceed = self.styled_input("Is this correct? (y/n) ", style="bold red")
        if proceed.lower() == "n":
            self.download_single_video()
            return
        elif proceed.lower() == "y":
            path = self.styled_input("Enter download path: ", style="bold red")
            highest_resolution_stream.download(path, filename=f"{self.youtube.title}.mp4")

    def download_multiple_videos(self):
        check = self.styled_input("Are the YouTube video links in a text file? (y/n) ", style="bold red")

        if check.lower() == "y":
            file = self.styled_input("Enter path to text file: ", style="bold red")
            if os.path.isfile(file):
                with open(file, "r") as f:
                    for url in f.readlines():
                        self.multi_vid_array.append(url)
            else:
                self.console.print("Invalid filepath. Please provide a valid filepath.", style="bold red")
        elif check.lower() == "n":
            num_of_vids = self.styled_input("How many videos? ")
            try:
                if int(num_of_vids) > 0:
                    for _ in range(int(num_of_vids)):
                        url = self.styled_input("Enter YouTube Video Link: ", style="bold blue")
                        self.multi_vid_array.append(url)
                    
                    for url in self.multi_vid_array:
                        # Normalize URL
                        url = url.strip()
                        if url.startswith("youtube.com") or url.startswith("www.youtube.com"):
                            url = "https://" + url
                        elif not url.startswith("http"):
                            self.console.print(f"[bold red]Skipping invalid URL: {url}[/bold red]")
                            continue
                        
                        try:
                            self.url = url
                            self.youtube = YouTube(self.url, on_progress_callback=self.on_progress)
                            self.streams = self.youtube.streams
                            self.download_single_video("args")
                        except Exception as e:
                            self.console.print(f"[bold red]Error with video {url}: {str(e)}[/bold red]")
                            continue

            except TypeError:
                self.console.print("Invalid input. Please provide an integer value greater than 0.", style="bold red")
                
if __name__ == "__main__":
    downloader = YouTubeDownloader()
    downloader.main_menu()
