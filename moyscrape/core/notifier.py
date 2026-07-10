import httpx


def push_telegram(cfg: dict, text: str, chat_id: str | None = None) -> bool:
    token = cfg.get("tg_token")
    cid = chat_id or cfg.get("tg_chat")
    if not token or not cid:
        return False
    httpx.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": cid, "text": text[:4000], "parse_mode": "Markdown"},
        timeout=20)
    return True


def push_webhook(cfg: dict, payload: dict) -> bool:
    url = cfg.get("webhook")
    if not url:
        return False
    httpx.post(url, json=payload, timeout=20)
    return True
