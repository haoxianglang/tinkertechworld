#!/usr/bin/env python3
"""Regenerate server-side knowledge and the same-origin Cloudflare Pages adapter."""
from pathlib import Path
from _chat_context import generate_knowledge
ROOT = Path(__file__).resolve().parent.parent

def main():
    revision = generate_knowledge()
    dest = ROOT / 'functions/api/chat.js'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text('// Generated adapter. Business logic lives in server/chat-core.mjs.\n'
                    "import {handleChat} from '../../server/chat-core.mjs';\n"
                    'export const onRequest = ({request, env}) => handleChat(request, env);\n')
    print(f'Built Gemini knowledge bundle: {revision}')
if __name__ == '__main__':
    main()
