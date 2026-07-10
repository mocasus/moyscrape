import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from moyscrape.core.engine import Engine


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "moyscrape ready.\n/scrape <url> | /crawl <url> | /map <url>")


async def _reply(update: Update, text: str):
    await update.message.reply_text(text[:4000], parse_mode="Markdown")


async def scrape_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text("pakai: /scrape <url>")
    eng = Engine()
    rec = eng.scrape(ctx.args[0])
    await _reply(update, f"*{rec['domain']}*\n{rec['content']}")


async def crawl_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text("pakai: /crawl <url>")
    eng = Engine()
    res = eng.crawl(ctx.args[0], depth=1, limit=10)
    await update.message.reply_text(f"crawled {len(res)} pages")


async def map_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text("pakai: /map <url>")
    eng = Engine()
    urls = eng.map_urls(ctx.args[0], depth=1, limit=30)
    await update.message.reply_text("\n".join(urls[:50]) or "no urls")


def main():
    from moyscrape.config import load_config
    cfg = load_config()
    if not cfg.get("tg_token"):
        raise SystemExit("TELEGRAM_BOT_TOKEN belum di-set di .env")
    app = Application.builder().token(cfg["tg_token"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scrape", scrape_cmd))
    app.add_handler(CommandHandler("crawl", crawl_cmd))
    app.add_handler(CommandHandler("map", map_cmd))
    app.run_polling()


if __name__ == "__main__":
    main()
