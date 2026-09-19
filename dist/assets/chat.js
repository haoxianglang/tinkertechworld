'use strict';
// The browser only sees the same-origin endpoint. Keys and grounding documents stay server-side.
(() => {
  const launcher = document.querySelector('#tinker-launcher');
  if (!launcher) return;
  const panel = document.querySelector('#tinker-panel');
  const messages = document.querySelector('#tinker-messages');
  const form = document.querySelector('#tinker-form');
  const input = document.querySelector('#tinker-input');
  const sendButton = form.querySelector('button');
  const status = document.querySelector('#tinker-status');
  const suggestions = document.querySelector('#tinker-suggestions');
  const labels = JSON.parse(document.querySelector('#tinker-data').textContent);
  let history = [], busy = false, greeted = false, controller, version = 0;
  const scroll = () => { messages.scrollTop = messages.scrollHeight; };
  function message(text, role) {
    const bubble = document.createElement('div');
    bubble.className = 'tinker-msg ' + role; bubble.textContent = text;
    messages.appendChild(bubble); scroll(); return bubble;
  }
  function setBusy(value) {
    busy = value; sendButton.disabled = value; input.readOnly = value;
    form.setAttribute('aria-busy', String(value));
    status.textContent = value ? labels.thinking : '';
  }
  function greet() { if (!greeted) { message(labels.greeting, 'bot'); greeted = true; } }
  function open() {
    panel.hidden = false; launcher.setAttribute('aria-expanded', 'true'); greet(); input.focus();
  }
  function close() { panel.hidden = true; launcher.setAttribute('aria-expanded', 'false'); launcher.focus(); }
  launcher.addEventListener('click', () => panel.hidden ? open() : close());
  document.querySelector('#tinker-close').addEventListener('click', close);
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && !panel.hidden) close(); });
  document.querySelector('#tinker-reset').addEventListener('click', () => {
    version++; controller?.abort(); history = []; messages.replaceChildren(); greeted = false;
    setBusy(false); input.value = ''; suggestions.hidden = false; greet();
    status.textContent = labels.resetStatus; input.focus();
  });
  function sourcesFor(bubble, sources) {
    if (!Array.isArray(sources)) return;
    const valid = sources.filter(s => s && typeof s.title === 'string' && typeof s.href === 'string' && /^\/(?:zh\/)?[a-z0-9/-]+\.html$/.test(s.href)).slice(0, 4);
    if (!valid.length) return;
    const list = document.createElement('div'); list.className = 'tinker-sources';
    const label = document.createElement('span'); label.textContent = labels.sources + ': '; list.append(label);
    for (const source of valid) { const a = document.createElement('a'); a.href = source.href; a.textContent = source.title; list.append(a); }
    bubble.append(list); scroll();
  }
  async function ask(value, echo = true, previousError = null) {
    if (busy || !value.trim() || value.length > 1000) return;
    previousError?.remove();
    suggestions.hidden = true;
    if (echo) message(value, 'user');
    input.value = ''; setBusy(true);
    const current = ++version;
    controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 27000);
    let errorText = labels.unavailable;
    // Bound the UTF-8 request as well as the number of turns (Chinese uses more bytes).
    let recent = history;
    const body = () => JSON.stringify({message: value, lang: document.body.dataset.language, history: recent});
    while (new TextEncoder().encode(body()).byteLength > 18000 && recent.length) recent = recent.slice(2);
    try {
      const response = await fetch('/api/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, credentials: 'same-origin',
        body: body(), signal: controller.signal,
      });
      if (response.status === 429) errorText = labels.rateLimited;
      if (response.status === 504) errorText = labels.timeout;
      if (!response.ok) throw new Error('chat_unavailable');
      const data = await response.json();
      if (typeof data.reply !== 'string' || !data.reply.trim() || data.reply.length > 4000) throw new Error('invalid_reply');
      if (current !== version) return;
      const bubble = message(data.reply, 'bot'); sourcesFor(bubble, data.sources);
      history = [...history, {role: 'user', text: value}, {role: 'model', text: data.reply}].slice(-8);
    } catch (error) {
      if (current !== version) return;
      if (error.name === 'AbortError') errorText = labels.timeout;
      const bubble = message(errorText, 'bot error');
      const actions = document.createElement('div'); actions.className = 'tinker-error-actions';
      const retry = document.createElement('button'); retry.type = 'button'; retry.textContent = labels.retry;
      retry.addEventListener('click', () => ask(value, false, bubble));
      const contact = document.createElement('a'); contact.href = labels.contactHref; contact.textContent = labels.contact;
      actions.append(retry, contact); bubble.append(actions); scroll();
      input.value = value; // Keep the failed question available for editing.
    } finally {
      clearTimeout(timer);
      if (current === version) setBusy(false);
    }
  }
  form.addEventListener('submit', event => { event.preventDefault(); ask(input.value.trim()); });
  suggestions.querySelectorAll('button').forEach(button => button.addEventListener('click', () => ask(button.textContent)));
})();
