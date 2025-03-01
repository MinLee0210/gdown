from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Union

from gdown.downloader._download import download
from gdown.downloader.factory import BaseDownloader, DownloaderFactory
from gdown.helpers import setup_logger
from gdown.models import GdownRsp

logger = setup_logger("[FilesDownloader]")


@DownloaderFactory.register_class(type_names="file(s)")
class FilesDownloader(BaseDownloader):
    def download(
        self,
        url: Union[str, list[str]],
        output: str,
        proxy: Optional[str] = None,
        use_cookies: bool = True,
        verify: bool = True,
        user_agent: Optional[str] = None,
    ) -> Optional[GdownRsp]:
        """
        Downloads a file or multiple files from a given URL using gdown.

        :param url: Single URL or list of URLs.
        :param output: Output file path or directory.
        :param proxy: Proxy setting.
        :param use_cookies: Whether to use cookies.
        :param verify: SSL verification.
        :param user_agent: Custom user agent string.
        :return: Output GdownRsp object(s) of the downloaded file(s), or None if failed.
        """
        try:
            if isinstance(url, str):
                return download(url, output, proxy, use_cookies, verify, user_agent)
            elif isinstance(url, list):
                with ThreadPoolExecutor() as executor:
                    results = list(
                        executor.map(
                            lambda u: download(
                                u, output, proxy, use_cookies, verify, user_agent
                            ),
                            url,
                        )
                    )
                return results
            else:
                logger.error("Invalid URL type. Expected str or list[str].")
                return None
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
