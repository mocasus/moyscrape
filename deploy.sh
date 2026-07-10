#!/usr/bin/env bash
set -e
cd /root/moyscrape
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
playwright install chromium
[ -f .env ] || cp .env.example .env
echo "== edit /root/moyscrape/.env (TELEGRAM_BOT_TOKEN, dll) =="
sudo cp deploy/moyscrape-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now moyscrape-bot
echo "deployed."
