BrowserType.launch: Target page, context or browser has been closed means the Playwright browser you just started vanished before the next URL could be processed.
Because the first URL (fbbcapitalpartners.com) succeeds and the very next one fails, the most common culprits are:


Root cause	What's happening in your log
You launch a fresh browser for every URL and immediately exit the async with block after a single page. The browser closes → next call tries to reuse it → crash.	async with AsyncWebCrawler() as crawler: fires once per URL. After __aexit__ the browser is gone, but the outer code keeps the same crawler object.
Unhandled exception inside the first crawl kills the event‑loop context. Playwright's teardown runs, so the next launch() finds a dead connection.	The stack trace shows Playwright raising inside its wrap_api_call()—typical when the previous browser closed unexpectedly.
Mac sandbox / GUI permissions kill headless Chromium after one launch. The first run grabs the GPU/process slot; the second gets rejected.	Only happens on macOS when permissions (Screen Recording, Automation) are missing.
Below is a battle‑tested pattern that fixes all three issues. Integrate the parts you need.

1. Hold one browser per session
python
Copy
Edit
# crawler.py
from playwright.async_api import async_playwright

class BrowserSession:
    def __init__(self, *, headless=True):
        self.browser = None
        self.pw = None
        self.headless = headless

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
Usage:

python
Copy
Edit
async def scrape_many(urls):
    async with BrowserSession(headless=True) as s:
        for u in urls:
            try:
                raw = await s.fetch(u)
                store_raw(u, raw)
                print(f"✓  {u}")
            except Exception as e:
                print(f"✗  {u} — {e}")
Result: one Chromium instance lives for all URLs; it closes after the loop.

2. Remove manual loop.run_until_complete in Streamlit
streamlit already runs an event loop. Wrap every async call in asyncio.run() will clash.

python
Copy
Edit
import asyncio
import streamlit as st

# ❌ BAD
# loop.run_until_complete(get_fit_markdown_async(url))

# ✅ GOOD
async def gather_markdowns(urls):
    async with BrowserSession() as s:
        return {u: await s.fetch(u) for u in urls}

# Call from Streamlit
if st.button("Run"):
    data = asyncio.run(gather_markdowns(st.session_state["urls_splitted"]))
If you must stay synchronous, push async work into a thread:

python
Copy
Edit
from concurrent.futures import ThreadPoolExecutor

def sync_scrape(urls):
    return asyncio.run(gather_markdowns(urls))

with ThreadPoolExecutor(max_workers=1) as ex:
    data = ex.submit(sync_scrape, urls).result()
3. Grant macOS permissions once
System Settings ▸ Privacy & Security

Screen Recording → add Terminal / VS Code.

Automation → allow it to control "System Events".

Accessibility → add Terminal / VS Code.

Disable App Nap for CLI tools:

bash
Copy
Edit
defaults write NSGlobalDomain NSAppSleepDisabled -bool YES
Prevent sleep while crawling:

bash
Copy
Edit
caffeinate -dimsu python streamlit_app.py
4. Retry anti‑bot pages separately
Some sites (a‑mcapital.com) block headless Chromium. Detect the failure and re‑try with another engine:

python
Copy
Edit
try:
    html = await s.fetch(url)
except TargetClosedError:
    print("Retrying in Firefox…")
    await s.context.close()
    s.browser = await s.pw.firefox.launch(headless=True)
    s.context = await s.browser.new_context()
    html = await s.fetch(url)
Quick checklist
 Consolidate browser lifecycle (async with only once per batch).

 Remove nested event‑loop calls in Streamlit.

 Add macOS privacy permissions.

 Launch with --no-sandbox --disable-dev-shm-usage flags.

 Retry on alternative engine for stubborn sites.

Apply these and the "Target page ... closed" error should disappear. If you still see it, enable Playwright debug logging:

bash
Copy
Edit
export DEBUG=pw:browser*  # then run your script
That will reveal exactly where the browser dies.