import email.utils
import re
import shutil
import sys
import tempfile
import textwrap
import time
import urllib.parse
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Optional, Tuple

import bs4
import httpx
import tqdm

from gdown.constants import CHUNK_SIZE, USER_AGENT
from gdown.exceptions import FileURLRetrievalError
from gdown.helpers import indent, parse_url, setup_logger
from gdown.models import GdownRsp

logger = setup_logger(name="[gdown-logger|>")


def get_url_from_gdrive_confirmation(contents: str) -> str:
    """Extracts the direct download URL from Google Drive's confirmation page.

    Parameters:
    contents (str): The HTML content of the Google Drive confirmation page.

    Returns:
    str: The extracted download URL.

    Raises:
    FileURLRetrievalError: If the file URL cannot be retrieved.
    """
    url = ""
    for line in contents.splitlines():
        m = re.search(r'href="(\/uc\?export=download[^"]+)', line)
        if m:
            url = "https://docs.google.com" + m.groups()[0]
            url = url.replace("&amp;", "&")
            break

        soup = bs4.BeautifulSoup(line, features="html.parser")
        form = soup.select_one("#download-form")
        if form is not None:
            url = form["action"].replace("&amp;", "&")
            url_components = urllib.parse.urlsplit(url)
            query_params = urllib.parse.parse_qs(url_components.query)
            for param in form.findChildren("input", attrs={"type": "hidden"}):
                query_params[param["name"]] = param["value"]
            query = urllib.parse.urlencode(query_params, doseq=True)
            url = urllib.parse.urlunsplit(url_components._replace(query=query))
            break

        m = re.search('"downloadUrl":"([^"]+)', line)
        if m:
            url = m.groups()[0]
            url = url.replace("\\u003d", "=").replace("\\u0026", "&")
            break

        m = re.search('<p class="uc-error-subcaption">(.*)</p>', line)
        if m:
            error = m.groups()[0]
            raise FileURLRetrievalError(error)

    if not url:
        raise FileURLRetrievalError(
            "Cannot retrieve the public link of the file. "
            "You may need to change the permission to "
            "'Anyone with the link', or have had many accesses. "
        )
    return url


def _get_filename_from_response(response: httpx.Response) -> Optional[str]:
    """Extracts the filename from the HTTP response headers."""
    content_disposition = urllib.parse.unquote(
        response.headers.get("Content-Disposition", "")
    )

    m = re.search(r"filename\*=UTF-8''(.*)", content_disposition)
    if m:
        return m.groups()[0].replace("/", "_")

    m = re.search('attachment; filename="(.*?)"', content_disposition)
    if m:
        return m.groups()[0]

    return None


def _get_modified_time_from_response(
    response: httpx.Response,
) -> Optional[email.utils.datetime]:
    """Extracts the last modified time from the HTTP response headers."""
    if "Last-Modified" not in response.headers:
        return None
    return email.utils.parsedate_to_datetime(response.headers["Last-Modified"])


def _get_session(
    proxy: Optional[str], use_cookies: bool, user_agent: str, verbose: bool = True
) -> Tuple[httpx.Client, Path]:
    """Creates an HTTP session for downloading files.

    Parameters:
    proxy (Optional[str]): Proxy URL.
    use_cookies (bool): Whether to use stored cookies.
    user_agent (str): The user-agent string for the request.
    verbose (bool): Whether to log session details.

    Returns:
    Tuple[httpx.Client, Path]: An HTTP client session and the path to the cookies file.
    """
    if verbose:
        logger.info(f"Proxy: {proxy} Cookies: {use_cookies} User-Agent: {user_agent} ")
    client = httpx.Client(headers={"User-Agent": user_agent}, proxies=proxy)

    cookies_file = Path.home() / ".cache/gdown/cookies.txt"
    if use_cookies and cookies_file.exists():
        cookie_jar = MozillaCookieJar(str(cookies_file))
        cookie_jar.load()
        client.cookies.update(cookie_jar)

    return client, cookies_file


def download(
    url: str,
    output: Optional[Path] = None,
    proxy: Optional[str] = None,
    use_cookies: bool = True,
    verify: bool = True,
    user_agent: Optional[str] = None,
) -> GdownRsp:
    """Downloads a file from a given URL and saves it to a specified location.

    Parameters:
    url (str): The file URL.
    output (Optional[Path]): The output filename or directory.
    verbose (bool): Whether to print progress information.
    proxy (Optional[str]): Proxy URL.
    use_cookies (bool): Whether to use stored cookies.
    verify (bool): Whether to verify SSL certificates.
    user_agent (Optional[str]): The user-agent string for the request.

    Returns:
    GdownRsp: The path of the downloaded file.
    """
    if not user_agent:
        user_agent = USER_AGENT

    try:
        start_time = time.perf_counter()
        client, cookies_file = _get_session(proxy, use_cookies, user_agent)
        response = client.get(url, stream=True, verify=verify)
        response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Failed to connect to {url}: {e}")
        raise FileURLRetrievalError(f"Failed to retrieve file from {url}")
    total_time = time.perf_counter() - start_time
    try:
        filename_from_url = _get_filename_from_response(response) or Path(url).name
        last_modified = _get_modified_time_from_response(response)
        output = Path(output or filename_from_url)

        if output.is_dir():
            output /= filename_from_url

        temp_file = output.with_suffix(".part")

        with temp_file.open("wb") as f, tqdm.tqdm(
            total=int(response.headers.get("Content-Length", 0)),
            unit="B",
            unit_scale=True,
        ) as pbar:
            for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                f.write(chunk)
                pbar.update(len(chunk))

        temp_file.rename(output)

        if use_cookies:
            cookie_jar = MozillaCookieJar(str(cookies_file))
            for cookie in client.cookies:
                cookie_jar.set_cookie(cookie)
            cookie_jar.save()

        resp = GdownRsp(
            url=url,
            output=str(output),
            last_modified=last_modified,
            total_time=str(total_time),
        )
        logger.info(f"Download successful: {output}")

        return resp
    except Exception as e:
        logger.error(f"Download failed: {e}")
        if temp_file.exists():
            temp_file.unlink()
        raise FileURLRetrievalError(f"Download failed due to {e}")
