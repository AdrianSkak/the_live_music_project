import requests

from app.config import REQUEST_TIMEOUT_SECONDS, USER_AGENT


def fetch_html(url: str) -> tuple[str, str]:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text, response.url