# config.py — Railway Environment

import os

# ============ RAILWAY ============
PORT = int(os.environ.get("PORT", 8080))
RAILWAY_PUBLIC_URL = os.environ.get("RAILWAY_PUBLIC_URL", f"http://localhost:{PORT}")
CALLBACK_URL = f"{RAILWAY_PUBLIC_URL}/callback"

# ============ TELEGRAM ============
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

# ============ C2 ============
C2_HOST = "0.0.0.0"
C2_PORT = PORT
C2_ENABLED = True