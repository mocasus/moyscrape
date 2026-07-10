import json
import httpx
from parsel import Selector
import trafilatura


def to_markdown(html: str, url: str | None = None) -> str:
    """Clean main-content extraction -> markdown (Firecrawl-style)."""
    md = trafilatura.extract(
        html, url=url, output_format="markdown",
        include_comments=False, include_tables=True)
    return md or ""


def extract_selectors(html: str, selectors: dict) -> dict:
    """Declarative field extraction. expr = 'css' or 'css::attr'.

    mode 'text' (default) -> text; 'href' -> href attr;
    any other mode -> that attribute name.
    """
    sel = Selector(text=html)
    out = {}
    for field, expr in selectors.items():
        parts = expr.split("::")
        css = parts[0]
        mode = parts[1] if len(parts) > 1 else "text"
        nodes = sel.css(css)
        if mode == "text":
            out[field] = nodes.get() if len(nodes) == 1 else [n.get() for n in nodes]
        elif mode == "href":
            out[field] = [n.attrib.get("href") for n in nodes]
        else:
            out[field] = [n.attrib.get(mode) for n in nodes]
    return out


def extract_llm(html: str, schema: dict, cfg: dict) -> str:
    """Optional structured extraction via OpenAI-compatible chat API."""
    if not cfg.get("llm_key"):
        raise RuntimeError("LLM_API_KEY not set in .env")
    prompt = (
        "Extract data from the HTML according to this JSON schema. "
        "Return ONLY valid JSON.\nSchema:\n" + json.dumps(schema, indent=2) +
        "\nHTML:\n" + html[:20000]
    )
    r = httpx.post(
        cfg["llm_base"].rstrip("/") + "/chat/completions",
        headers={"Authorization": f"Bearer {cfg['llm_key']}",
                 "Content-Type": "application/json"},
        json={"model": cfg["llm_model"],
              "messages": [{"role": "user", "content": prompt}],
              "response_format": {"type": "json_object"}},
        timeout=60,
    )
    return r.json()["choices"][0]["message"]["content"]
