#!/usr/bin/env python3
"""Optional Worker adapter using the same backend as Cloudflare Pages."""
from pathlib import Path
from _chat_context import generate_knowledge
ROOT = Path(__file__).resolve().parent.parent

def main():
    generate_knowledge()
    (ROOT / 'cloudflare-worker/worker.js').write_text('''// Generated. Optional standalone Worker; Pages is the primary deployment.
import {handleChat} from '../server/chat-core.mjs';
export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname === '/api/chat') return handleChat(request, env);
    return env.ASSETS ? env.ASSETS.fetch(request) : new Response('Not found', {status: 404});
  }
};
''')
if __name__ == '__main__':
    main()
