from playwright.sync_api import sync_playwright

STEALTH = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "locale": "en-US",
}


def fetch_browser(url: str, proxy: str | None = None) -> str:
    """Render page with Playwright + light stealth. Returns full HTML."""
    proxy = proxy or None
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = browser.new_context(
            user_agent=STEALTH["user_agent"],
            locale=STEALTH["locale"],
            proxy={"server": proxy} if proxy else None)
        page = ctx.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        browser.close()
        return html
