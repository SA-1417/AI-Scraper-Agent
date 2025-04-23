# markdown.py

import asyncio
from typing import List
from api_management import get_supabase_client
from utils import generate_unique_name
from playwright.async_api import async_playwright
import html2text
from datetime import datetime

supabase = get_supabase_client()

class BrowserSession:
    def __init__(self, *, headless=True):
        self.browser = None
        self.pw = None
        self.headless = headless
        self.context = None

    async def __aenter__(self):
        self.pw = await async_playwright().start()
        # extra flags: safer on macOS
        chromium_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-background-timer-throttling",
        ]
        self.browser = await self.pw.chromium.launch(
            headless=self.headless,
            args=chromium_args,
        )
        self.context = await self.browser.new_context()
        return self

    async def fetch(self, url: str) -> str:
        page = await self.context.new_page()
        await page.goto(url, wait_until="load", timeout=40_000)
        html = await page.content()
        await page.close()
        return html

    async def __aexit__(self, *exc):
        await self.context.close()
        await self.browser.close()
        await self.pw.stop()

async def get_fit_markdown_async(url: str) -> str:
    """
    Async function using BrowserSession to produce the regular raw markdown.
    """
    try:
        async with BrowserSession(headless=True) as session:
            html = await session.fetch(url)
            # Convert HTML to markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_tables = False
            h.body_width = 0  # Disable line wrapping
            markdown = h.handle(html)
            return markdown
    except Exception as e:
        print(f"Error during crawling: {str(e)}")
        return ""

def fetch_fit_markdown(url: str) -> str:
    """
    Synchronous wrapper around get_fit_markdown_async().
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(get_fit_markdown_async(url))
    finally:
        loop.close()

def read_raw_data(unique_name: str) -> str:
    """
    Query the 'scraped_data' table for the row with this unique_name,
    and return the 'raw_data' field.
    """
    response = supabase.table("scraped_data").select("raw_data").eq("unique_name", unique_name).execute()
    data = response.data
    if data and len(data) > 0:
        return data[0]["raw_data"]
    return ""

def save_raw_data(unique_name: str, url: str, raw_data: str) -> None:
    """
    Save or update the row in supabase with unique_name, url, and raw_data.
    If a row with unique_name doesn't exist, it inserts; otherwise it updates.
    """
    supabase.table("scraped_data").upsert({
        "unique_name": unique_name,
        "url": url,
        "raw_data": raw_data,
        "created_at": datetime.now().isoformat()
    }, on_conflict="unique_name").execute()
    
    BLUE = "\033[34m"
    RESET = "\033[0m"
    print(f"{BLUE}INFO:Raw data stored for {unique_name}{RESET}")

def fetch_and_store_markdowns(urls: List[str]) -> List[str]:
    """
    For each URL:
      1) Generate unique_name
      2) Check if there's already a row in supabase with that unique_name
      3) If not found or if raw_data is empty, fetch fit_markdown
      4) Save to supabase
    Return a list of unique_names (one per URL).
    """
    unique_names = []

    for url in urls:
        unique_name = generate_unique_name(url)
        MAGENTA = "\033[35m"
        RESET = "\033[0m"
        RED = "\033[31m"
        
        # check if we already have raw_data in supabase
        raw_data = read_raw_data(unique_name)
        if raw_data:
            print(f"{MAGENTA}Found existing data in supabase for {url} => {unique_name}{RESET}")
        else:
            print(f"{MAGENTA}No existing data found for {url}, attempting to scrape...{RESET}")
            try:
                # fetch fit markdown
                fit_md = fetch_fit_markdown(url)
                if fit_md:
                    save_raw_data(unique_name, url, fit_md)
                    print(f"{MAGENTA}Successfully scraped and stored data for {url}{RESET}")
                else:
                    print(f"{RED}Failed to scrape data for {url}{RESET}")
            except Exception as e:
                print(f"{RED}Error scraping {url}: {str(e)}{RESET}")
        
        unique_names.append(unique_name)

    return unique_names
