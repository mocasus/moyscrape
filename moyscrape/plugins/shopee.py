# Example plugin: override fetch/parse for a stubborn domain.
# Add a new file in this folder with DOMAIN + scrape() to register it.
# Engine auto-discovers it — no central registry to edit.

DOMAIN = "shopee.co.id"


def scrape(url: str, opts: dict, cfg: dict) -> dict:
    """Force browser render + custom parse. Replace with real selectors."""
    from moyscrape.core import browser, extract
    html = browser.fetch_browser(url, proxy=opts.get("proxy"))
    content = extract.to_markdown(html, url)
    return {"content": content, "metadata": {"plugin": "shopee", "len": len(content)}}
