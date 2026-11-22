import ipaddress
import os
import socket
from urllib.parse import urljoin, urlsplit

import requests
from langchain_core.tools import tool
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup
from rich import print
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0 Safari/537.36"
)


def _validate_public_url(url: str) -> None:
    """Allow only public HTTP(S) destinations, including after redirects."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only public HTTP and HTTPS URLs can be scraped.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing embedded credentials cannot be scraped.")

    host = parsed.hostname.rstrip(".")
    try:
        addresses = {
            ipaddress.ip_address(result[4][0])
            for result in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
        }
    except (OSError, ValueError) as exc:
        raise ValueError(f"Could not resolve the public URL host: {host}") from exc

    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Only publicly routable websites can be scraped.")


def _get_public_page(url: str):
    """Fetch a page while validating each redirect destination."""
    current_url = url
    for _ in range(6):
        _validate_public_url(current_url)
        response = requests.get(
            current_url,
            timeout=10,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=False,
        )
        if response.is_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise requests.exceptions.InvalidURL("Redirect response did not include a Location header.")
            current_url = urljoin(current_url, location)
            continue
        response.raise_for_status()
        return current_url, response

    raise requests.exceptions.TooManyRedirects(f"Too many redirects while requesting {url}")


def _render_with_browser(url: str) -> tuple[str, str]:
    """Render a public page so JavaScript-generated content is included."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(user_agent=USER_AGENT)

            def guard_request(route):
                request_url = route.request.url
                if request_url.startswith(("data:", "blob:", "about:")):
                    route.continue_()
                    return
                try:
                    _validate_public_url(request_url)
                except ValueError:
                    route.abort()
                    return
                route.continue_()

            context.route("**/*", guard_request)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(1500)
            title = page.title()
            page.locator("script, style, nav, footer, header, aside, form, iframe").evaluate_all(
                "(elements) => elements.forEach((element) => element.remove())"
            )
            text = page.locator("body").inner_text(timeout=5000)
            return title, text
        finally:
            browser.close()


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Return Titles, URLs and detailed snippets."""
    results = tavily.search(query=query, max_results=8, include_raw_content=False)

    out=[]
    for i, r in enumerate(results.get("results", []), 1):
        snippet = r.get("content", "")[:800]
        entry = (
            f"[Source {i}]\n"
            f"Title: {r.get('title', 'N/A')}\n"
            f"URL: {r.get('url', 'N/A')}\n"
            f"Snippet: {snippet}\n"
        )
        out.append(entry)
    return "\n---\n".join(out) if out else "No search results found."    

@tool  
def scrape_url(url:str) -> str:
    """Scrape the content of a URL and return the text content."""
    try:
        page_url, resp = _get_public_page(url)
        with resp:
            soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style","nav","footer","header","aside","form","iframe"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)

        if len(text.strip()) < 300:
            title, rendered_text = _render_with_browser(page_url)
            if len(rendered_text.strip()) > len(text.strip()):
                text = f"{title}\n\n{rendered_text}"

        text = text[:5000]
        if len(text.strip()) < 100:
            return f"Page at {url} returned very little readable content (possibly blocked or paywalled)."
        return f"[Scraped from: {url}]\n\n{text}"
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code in {403, 429, 503}:
            try:
                title, rendered_text = _render_with_browser(url)
            except PlaywrightError as browser_error:
                return (
                    f"HTTP error scraping {url}: {e.response.status_code} {e.response.reason}. "
                    f"Browser rendering also failed: {browser_error}"
                )
            if len(rendered_text.strip()) >= 100:
                return f"[Scraped from: {url}]\n\n{title}\n\n{rendered_text[:5000]}"
        return f"HTTP error scraping {url}: {e.response.status_code} {e.response.reason}"
    except PlaywrightError as e:
        return f"Browser rendering failed for {url}: {e}"
    except requests.exceptions.Timeout:
        return f"Timeout: {url} did not respond within 10 seconds."
    except ValueError as e:
        return f"URL could not be scraped: {e}"
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

if __name__ == "__main__":
    print(scrape_url.invoke({"url": "https://www.nature.com/articles/s41586-020-2649-2"}))