![version](https://img.shields.io/badge/version-0.1.0-blue)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

# moyscrape

Firecrawl-style scraping engine. Kasih URL → dapet clean markdown / HTML / JSON. Multi-site, extensible, jalan via **CLI + cron + Telegram**.

## Flow

```
INPUT → RESOLVE → FETCH → EXTRACT → STORE → OUTPUT/PUSH
```

- **RESOLVE**: ada plugin buat domain? → pakai plugin. Ada YAML preset? → selector extract. Else → generic (trafilatura clean markdown).
- **FETCH**: `httpx` dulu; kalau ketahuan JS/anti-bot → fallback **Playwright** (stealth).
- **EXTRACT**: markdown (trafilatura) · JSON via selector YAML · JSON via LLM (opt-in).
- **STORE**: SQLite + export JSON/CSV.
- **PUSH**: Telegram / webhook (opt-in).

## Install (deploy di BF VPS)

```bash
git clone https://github.com/mocasus/moyscrape.git
cd moyscrape
bash deploy.sh          # venv + pip + playwright + systemd bot
# edit .env (TELEGRAM_BOT_TOKEN, dll)
```

## CLI

```bash
python -m moyscrape scrape <url> --format markdown
python -m moyscrape scrape <url> --browser          # paksa Playwright
python -m moyscrape crawl <url> --depth 2 --limit 50
python -m moyscrape map <url> --depth 1 --limit 30
python -m moyscrape extract <url> --schema schema.json
python -m moyscrape batch url1 url2 url3
python -m moyscrape sites        # list plugin + preset
python -m moyscrape validate
```

## Telegram

```
/scrape <url>
/crawl <url>
/map <url>
```

## Cron (contoh: crawl tiap 1 jam)

```cron
0 * * * * cd /root/moyscrape && venv/bin/python -m moyscrape crawl https://news.example.com --depth 1 --limit 20 >> crawl.log 2>&1
```

## Extend

**Plugin** (situx bandel / anti-bot / login) — `moyscrape/plugins/<nama>.py`:

```python
DOMAIN = "shopee.co.id"
def scrape(url, opts, cfg):
    from moyscrape.core import browser, extract
    html = browser.fetch_browser(url, proxy=opts.get("proxy"))
    return {"content": extract.to_markdown(html, url), "metadata": {}}
```

**Preset YAML** (selector tanpa LLM) — `moyscrape/sites/<nama>.yaml`:

```yaml
domain: example.com
selectors:
  title: "h1::text"
  links: "a::href"
```

Plugin & preset auto-discovery — gak perlu edit registry.

## Test

```bash
venv/bin/pip install pytest && venv/bin/pytest
```

---
v0.1.0
