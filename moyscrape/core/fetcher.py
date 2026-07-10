import httpx

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url: str, proxy: str | None = None, timeout: int = 20,
          headers: dict | None = None):
    """Fast HTTP fetch via httpx. Returns (html, status, headers)."""
    h = {**DEFAULT_HEADERS, **(headers or {})}
    with httpx.Client(headers=h, proxy=proxy, follow_redirects=True,
                      timeout=timeout, verify=False) as c:
        r = c.get(url)
        return r.text, r.status_code, dict(r.headers)


def looks_blocked(html: str, status: int) -> bool:
    """Heuristic detection of CAPTCHA / bot-check / empty body."""
    if status >= 400:
        return True
    if not html or len(html) < 500:
        return True
    low = html.lower()
    signals = ["captcha", "are you a robot", "please verify",
               "access denied", "just a moment", "enable javascript and cookies"]
    return any(s in low for s in signals)
