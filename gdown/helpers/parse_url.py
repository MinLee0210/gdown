import re
import urllib.parse
import warnings
from typing import Tuple, Union

from gdown.constants import PARSING_PATTERNS


def is_google_drive_url(url: str) -> bool:
    """Check if a given URL belongs to Google Drive.

    Parameters
    ----------
    url : str
        The URL to be checked.

    Returns
    -------
    bool
        True if the URL is a Google Drive or Google Docs URL, otherwise False.
    """
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname in ["drive.google.com", "docs.google.com"]


def parse_url(url: str, warning: bool = True) -> Tuple[Union[str, None], bool]:
    """Parse a URL to extract Google Drive file ID and check if it is a download link.

    Parameters
    ----------
    url : str
        The URL to be parsed.
    warning : bool, optional
        If True, warns the user if the link is not a direct download link.

    Returns
    -------
    tuple
        file_id : str or None
            The extracted file ID from the Google Drive URL, if available.
        is_download_link : bool
            True if the URL is a direct download link, otherwise False.
    """
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    is_gdrive = is_google_drive_url(url=url)
    is_download_link = parsed.path.endswith("/uc")

    if not is_gdrive:
        return None, is_download_link

    file_id: Union[str, None] = None
    if "id" in query:
        file_ids = query["id"]
        if len(file_ids) == 1:
            file_id = file_ids[0]
    else:
        for pattern in PARSING_PATTERNS:
            match = re.match(pattern, parsed.path)
            if match:
                file_id = match.groups()[0]
                break

    if warning and not is_download_link:
        warnings.warn(
            "You specified a Google Drive link that is not the correct link "
            "to download a file. You might want to try `--fuzzy` option "
            "or the following url: {url}".format(
                url=f"https://drive.google.com/uc?id={file_id}"
            )
        )

    return file_id, is_download_link
