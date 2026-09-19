"""Shared grounding-context builder for the Gemini-backed Tinker backends.

Used by scripts/chat_server.py (local dev proxy), scripts/generate_worker.py
(standalone Cloudflare Worker) and scripts/generate_pages_function.py
(Cloudflare Pages Function) so all three stay in sync with knowledge/*.md.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / 'knowledge'
MODEL = 'gemini-2.5-flash'
MAX_MESSAGE_CHARS = 500


def build_context():
    """Concatenate every knowledge/*.md file into one grounding text for Gemini."""
    files = sorted(KNOWLEDGE_DIR.glob('*.md'))
    if not files:
        raise RuntimeError(f'No knowledge base files found in {KNOWLEDGE_DIR}')
    parts = [f'--- {f.name} ---\n' + f.read_text(encoding='utf-8') for f in files]
    return '\n\n'.join(parts)


def build_system_instruction():
    return (
        'You are Tinker, the chat assistant on the Tinker Tech World (TTW) website, a Markham, Ontario '
        'robotics/STEM learning studio. Answer only using the knowledge base given below — '
        "never invent prices, dates, policies, safety claims or availability that aren't stated there. "
        "If the answer isn't covered by this content, say you're not sure and suggest contacting TTW "
        'directly, rather than guessing. Keep answers short (2-4 sentences), warm and plain-spoken. '
        "Reply in the same language as the visitor's question (English or Chinese) unless told otherwise.\n\n"
        '=== KNOWLEDGE BASE ===\n' + build_context()
    )
