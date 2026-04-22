import os
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN is missing")
    sys.exit(1)

if not WEBHOOK_URL:
    print("ERROR: WEBHOOK_URL is missing")
    sys.exit(1)
