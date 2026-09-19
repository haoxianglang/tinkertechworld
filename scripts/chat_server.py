#!/usr/bin/env python3
"""Local-only dev proxy for a Gemini-backed Tinker chatbot.

Not part of the deployed static site. Runs on the developer's machine only,
so the Gemini API key never reaches the browser or the repository. Grounds
every answer in the markdown files under knowledge/ (see build_context()
below) to keep it from inventing prices, policies or schedules TTW hasn't
published. Edit those files to update what Tinker knows — no code change
needed; the server rereads them on every start.

Usage:
    export GEMINI_API_KEY=...           # from https://aistudio.google.com/apikey
    python3 scripts/chat_server.py       # serves http://127.0.0.1:8787

Then open the static site (python3 -m http.server 4173) in a browser on
127.0.0.1 or localhost — assets/site.js auto-detects those hosts and calls
this server; on any other host (the deployed site) it never does.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _chat_context import build_system_instruction  # noqa: E402

HOST = '127.0.0.1'
PORT = int(os.environ.get('CHAT_PORT', '8787'))
MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
API_KEY = os.environ.get('GEMINI_API_KEY')
ALLOWED_ORIGINS = {f'http://127.0.0.1:{p}' for p in ('4173',)} | {f'http://localhost:{p}' for p in ('4173',)}
MAX_MESSAGE_CHARS = 500

SYSTEM_INSTRUCTION = build_system_instruction()


def call_gemini(message, lang):
    if not API_KEY:
        raise RuntimeError('GEMINI_API_KEY is not set in the environment')
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}'
    lang_hint = {'zh': '\n\n(Reply in Chinese.)', 'en': '\n\n(Reply in English.)'}.get(lang, '')
    payload = {
        'systemInstruction': {'parts': [{'text': SYSTEM_INSTRUCTION}]},
        'contents': [{'role': 'user', 'parts': [{'text': message + lang_hint}]}],
        'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 300},
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    candidates = data.get('candidates') or []
    if not candidates:
        raise RuntimeError('Gemini returned no candidates (possibly blocked by safety filters)')
    parts = candidates[0].get('content', {}).get('parts') or []
    text = ''.join(p.get('text', '') for p in parts).strip()
    if not text:
        raise RuntimeError('Gemini returned an empty response')
    return text


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))

    def _cors_origin(self):
        origin = self.headers.get('Origin', '')
        return origin if origin in ALLOWED_ORIGINS else ''

    def _send_json(self, status, body):
        payload = json.dumps(body).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        origin = self._cors_origin()
        if origin:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        origin = self._cors_origin()
        if origin:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/chat':
            self._send_json(404, {'error': 'not found'})
            return
        length = int(self.headers.get('Content-Length', '0') or '0')
        if length <= 0 or length > 4000:
            self._send_json(400, {'error': 'invalid request body'})
            return
        try:
            body = json.loads(self.rfile.read(length).decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {'error': 'invalid JSON'})
            return
        message = str(body.get('message', '')).strip()
        lang = str(body.get('lang', '')).strip()
        if not message:
            self._send_json(400, {'error': 'message is required'})
            return
        if len(message) > MAX_MESSAGE_CHARS:
            message = message[:MAX_MESSAGE_CHARS]
        try:
            reply = call_gemini(message, lang)
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', 'replace')[:300]
            print(f'Gemini API error {e.code}: {detail}', file=sys.stderr)
            self._send_json(502, {'error': 'upstream Gemini API error'})
            return
        except Exception as e:  # noqa: BLE001 - report to the local console, not the client
            print(f'chat_server error: {e}', file=sys.stderr)
            self._send_json(500, {'error': 'chat backend error'})
            return
        self._send_json(200, {'reply': reply})


def main():
    if not API_KEY:
        print(
            'GEMINI_API_KEY is not set.\n'
            'Get a key at https://aistudio.google.com/apikey, then run:\n'
            '  export GEMINI_API_KEY=your-key-here\n'
            '  python3 scripts/chat_server.py',
            file=sys.stderr,
        )
        raise SystemExit(1)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f'Tinker/Gemini dev proxy on http://{HOST}:{PORT} (model: {MODEL})')
    print('This server is for local testing only — do not deploy it as-is.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
