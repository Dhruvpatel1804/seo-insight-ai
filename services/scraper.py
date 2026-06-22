import httpx
from bs4 import BeautifulSoup

from core.config import settings
from core.exceptions import ScrapingError
from models.report import PageDetails
from util.http_client import create_http_client


def parse_html(html: str) -> PageDetails:
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    meta_description = ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    if description_tag and description_tag.get("content"):
        meta_description = description_tag["content"].strip()
    else:
        og_description = soup.find("meta", attrs={"property": "og:description"})
        if og_description and og_description.get("content"):
            meta_description = og_description["content"].strip()

    canonical_url = ""
    canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value.lower())
    if canonical_tag and canonical_tag.get("href"):
        canonical_url = canonical_tag["href"].strip()

    h1_tags = [tag.get_text(strip=True) for tag in soup.find_all("h1") if tag.get_text(strip=True)]
    h2_tags = [tag.get_text(strip=True) for tag in soup.find_all("h2") if tag.get_text(strip=True)]

    images = soup.find_all("img")
    image_count = len(images)
    missing_alt_count = sum(
        1 for image in images if not image.get("alt") or not str(image.get("alt")).strip()
    )

    word_count = _count_words(soup)

    return PageDetails(
        title=title,
        meta_description=meta_description,
        canonical_url=canonical_url,
        h1_tags=h1_tags,
        h2_tags=h2_tags,
        image_count=image_count,
        missing_alt_count=missing_alt_count,
        word_count=word_count,
    )


def _count_words(soup: BeautifulSoup) -> int:
    content = BeautifulSoup(soup.decode_contents(), "html.parser")
    for tag in content(["script", "style", "noscript"]):
        tag.decompose()

    text = content.get_text(separator=" ")
    return len([word for word in text.split() if word.strip()])


async def scrape_page(url: str, client: httpx.AsyncClient | None = None) -> PageDetails:
    owns_client = client is None
    client = client or create_http_client()

    try:
        html = await _fetch_html(client, url)
        return parse_html(html)
    except httpx.TimeoutException as exc:
        raise ScrapingError("Request timed out while fetching the webpage") from exc
    except httpx.HTTPStatusError as exc:
        raise ScrapingError(
            f"Website returned HTTP {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise ScrapingError(f"Unable to fetch webpage: {exc}") from exc
    except Exception as exc:
        raise ScrapingError(f"Failed to scrape webpage: {exc}") from exc
    finally:
        if owns_client:
            await client.aclose()


async def _fetch_html(client: httpx.AsyncClient, url: str) -> str:
    async with client.stream("GET", url) as response:
        response.raise_for_status()

        chunks: list[bytes] = []
        total_bytes = 0
        max_bytes = settings.MAX_RESPONSE_BYTES

        async for chunk in response.aiter_bytes():
            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                raise ScrapingError("Response exceeds maximum size limit")
            chunks.append(chunk)

        encoding = response.encoding or "utf-8"
        return b"".join(chunks).decode(encoding, errors="replace")
