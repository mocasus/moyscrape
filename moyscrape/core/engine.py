import importlib
import json
import pkgutil
from pathlib import Path
from urllib.parse import urlparse, urljoin

import yaml
from parsel import Selector

from moyscrape.config import load_config
from moyscrape.core import fetcher, extract, store, notifier


class Engine:
    """Firecrawl-style orchestrator: URL -> clean data, with plugin + preset layers."""

    def __init__(self):
        self.cfg = load_config()
        self._plugins = self._load_plugins()
        self._presets = self._load_presets()

    # ---- discovery -------------------------------------------------------
    def _load_plugins(self) -> dict:
        from moyscrape import plugins as plug_pkg
        reg = {}
        for mod in pkgutil.iter_modules(plug_pkg.__path__):
            if mod.name.startswith("_"):
                continue
            m = importlib.import_module(f"moyscrape.plugins.{mod.name}")
            dom = getattr(m, "DOMAIN", None)
            if dom and hasattr(m, "scrape"):
                reg[dom] = m
        return reg

    def _load_presets(self) -> dict:
        reg = {}
        sites_dir = Path(__file__).resolve().parent.parent / "sites"
        for f in sites_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(f.read_text())
            except Exception:
                continue
            if data and data.get("domain"):
                reg[data["domain"]] = data
        return reg

    def plugin_domains(self):
        return list(self._plugins)

    def preset_domains(self):
        return list(self._presets)

    def validate(self) -> bool:
        try:
            self._load_plugins()
            self._load_presets()
            return True
        except Exception:
            return False

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _domain(url: str) -> str:
        return urlparse(url).netloc.replace("www.", "")

    @staticmethod
    def _title(html: str) -> str:
        return (Selector(text=html).css("title::text").get() or "").strip()

    def _fetch(self, url: str, proxy: str | None, force_browser: bool) -> str:
        proxy = proxy or None
        html, status, _ = fetcher.fetch(url, proxy=proxy)
        if force_browser or fetcher.looks_blocked(html, status):
            try:
                from moyscrape.core import browser
                html = browser.fetch_browser(url, proxy=proxy)
            except Exception as e:
                print(f"[warn] browser fetch failed: {e}")
        return html

    # ---- modes -----------------------------------------------------------
    def scrape(self, url: str, fmt: str = "markdown", schema: dict | None = None,
               proxy: str | None = None, force_browser: bool = False) -> dict:
        proxy = proxy or self.cfg.get("proxy")
        dom = self._domain(url)

        if dom in self._plugins:
            data = self._plugins[dom].scrape(
                url, {"fmt": fmt, "proxy": proxy}, self.cfg)
            content, meta = data.get("content", ""), data.get("metadata", {})
        elif dom in self._presets and fmt == "json":
            html = self._fetch(url, proxy, force_browser)
            sel = self._presets[dom].get("selectors", {})
            content = json.dumps(extract.extract_selectors(html, sel), default=str)
            meta = {"selectors": list(sel)}
        else:
            html = self._fetch(url, proxy, force_browser)
            if fmt == "html":
                content = html
            elif fmt == "json":
                content = json.dumps(
                    {"url": url, "markdown_len": len(extract.to_markdown(html, url))},
                    default=str)
            else:
                content = extract.to_markdown(html, url)
            meta = {"title": self._title(html)}

        rec = {"url": url, "domain": dom, "mode": "scrape",
               "format": fmt, "content": content, "metadata": meta}
        store.save(self.cfg["db"], url, dom, "scrape", fmt, content, meta)
        return rec

    def crawl(self, start_url: str, depth: int = 1, limit: int = 20,
              proxy: str | None = None, fmt: str = "markdown") -> list:
        seen, results, queue = set(), [], [(start_url, 0)]
        while queue and len(results) < limit:
            url, d = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            try:
                rec = self.scrape(url, fmt=fmt, proxy=proxy)
            except Exception as e:
                rec = {"url": url, "error": str(e)}
            results.append(rec)
            if d < depth:
                html = self._fetch(url, proxy, False)
                for link in Selector(text=html).css("a::attr(href)").getall():
                    nxt = urljoin(url, link)
                    if nxt.startswith("http") and nxt not in seen:
                        queue.append((nxt, d + 1))
        return results

    def map_urls(self, start_url: str, depth: int = 1, limit: int = 50) -> list:
        seen, out, queue = set(), [], [(start_url, 0)]
        while queue and len(out) < limit:
            url, d = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            out.append(url)
            if d < depth:
                html = self._fetch(url, None, False)
                for link in Selector(text=html).css("a::attr(href)").getall():
                    nxt = urljoin(url, link)
                    if nxt.startswith("http") and nxt not in seen:
                        queue.append((nxt, d + 1))
        return out

    def extract(self, url: str, schema: dict, proxy: str | None = None) -> dict:
        html = self._fetch(url, proxy or self.cfg.get("proxy"), False)
        raw = extract.extract_llm(html, schema, self.cfg)
        try:
            data = json.loads(raw)
        except Exception:
            data = raw
        store.save(self.cfg["db"], url, self._domain(url),
                   "extract", "json", json.dumps(data, default=str), {})
        return {"url": url, "extracted": data}
