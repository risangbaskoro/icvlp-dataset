import logging
import os
import random
import time
from typing import List, Union

from icvlp.object import ICVLP, Video


class VideoDownloader:
    r"""Video downloader for ICVLP dataset.

    This class can be used to download video from :py:class:object.ICVLP instance or a list of py:class:object.Video
    instances.

        >>> icvlp = ICVLP.from_json('icvlp_v0.1.json')
        >>> downloader = VideoDownloader(videos=icvlp)
        >>> downloader.downloads()

    Args:
        videos (ICVLP, List[Video]): List of videos to download.
        directory (str): Download directory.
        youtube_downloader (str, optional): YouTube downloader used to download YouTube video:
            ``'yt-dlp'`` | ``'youtube-dl'``.
            Default: ``'yt-dlp'``.
        downloaded_videos_log (str, optional): File to log which videos has ever downloaded.
            Default: ``'downloaded_videos.txt'``
    """

    def __init__(self,
                 videos: Union[ICVLP, List[Video]],
                 directory: str = "videos",
                 youtube_downloader: str = "yt-dlp",
                 downloaded_videos_log: str = "downloaded_videos.txt") -> None:
        self.youtube_downloader = youtube_downloader
        self._check_youtube_dl_version()
        self.downloaded_videos_log = downloaded_videos_log

        if isinstance(videos, Video):
            videos = [videos]
        if isinstance(videos, ICVLP):
            videos = videos.videos
        self.videos = videos

        self.directory = directory

    def __getitem__(self, index: int) -> Video:
        return self.videos[index]

    def download(self, index: int) -> None:
        r"""Download a video from ``videos`` attribute.

        Args:
            index (int): The index of the video to download.

        Returns:
            None
        """
        self._download_video(index)

    def downloads(self) -> None:
        r"""Download all videos from ``videos`` attribute.

        Returns:
            None
        """
        for video in self.videos:
            self._download_video(video)

    def _check_youtube_dl_version(self) -> None:
        r"""Check and assert YouTube downloader version.

        Returns:
            None
        """
        assert self.youtube_downloader in ["yt-dlp", "youtube-dl"], \
            f"Youtube downloader must be either yt-dlp or youtube-dl. Got {self.youtube_downloader}."
        version = os.popen(f'{self.youtube_downloader} --version').read()
        assert version, f"{self.youtube_downloader} cannot be found in PATH. Please verify your installation."

    def _download_video(self, index: Union[Video, int]) -> None:
        r"""Download a video from ``videos`` attribute.

        Args:
            index (Video or int): The index of the video to download.

        Returns:
            None
        """
        if isinstance(index, int):
            video = self[index]
        else:
            video = index
        # Video filename based on video_id
        video_id = video.video_id
        filename = video_id + ".mp4"
        download_path = os.path.join(self.directory, filename)

        if not os.path.exists(self.downloaded_videos_log):
            with open(self.downloaded_videos_log, 'w') as logfile:
                logfile.write("")
                logfile.close()

        with open(self.downloaded_videos_log, 'r') as logfile:
            if f"{download_path}" in logfile.read():
                logging.info(
                    f"Video {download_path} already logged to '{self.downloaded_videos_log}'. "
                    f"Remove the line in the file to download again."
                )
                return

        if os.path.exists(download_path):
            logging.info(f'YouTube video {download_path} is already exists.')
        else:
            url = video.url
            logging.info(f"Downloading video to {download_path} from URL {url}")
            if 'youtube' in url or 'youtu.be' in url:
                self._download_youtube_video(url, download_path)
            else:
                logging.error(f"Downloader not implemented for URL {url}")

        logging.debug(f"Adding {download_path} to {self.downloaded_videos_log}")
        with open(self.downloaded_videos_log, 'a') as f:
            f.write(f"{download_path}\n")

    def _download_youtube_video(self, url: str, download_path: str) -> None:
        r"""Download a YouTube video and save it to download path using instance's YouTube downloader.

        Args:
            url (str): The url of the video to download.
            download_path (str): The path to save the video to.

        Returns:
            None
        """
        cmd = [
            self.youtube_downloader,
            url,
            f"-o {download_path}",
            "-f 248/mp4"
        ]
        cmd = ' '.join(cmd)

        rv = os.system(cmd)

        if not rv:
            logging.info(f'Finish downloading YouTube video URL {url}')
        else:
            logging.error(f'Unsuccessful downloading YouTube video URL {url}')
        # Reduce the download frequency, avoid spam
        time.sleep(random.uniform(0.5, 1.0))
