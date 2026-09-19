# Technical Architecture

## Approach
Continue the existing static GitHub Pages-compatible site, with generated HTML at the site root. The current working copy is the TTW workspace’s `05_website/` directory; the original Dropbox repository is retained as a source copy and is not automatically synchronized. No frontend framework migration, external fonts or client-side router. Static pages now have a Cloudflare Pages chat Function; local full-stack preview requires Node 20.12+ and Python 3, with no production npm dependencies. SEO/content/navigation work before JavaScript loads.

- `content/site.json`: business settings and bilingual program/age records.
- `scripts/build_site.py`: Python 3 standard-library renderer with shared layout, navigation, footer, cards, CTA, FAQ, program/age layouts and inquiry layout.
- `assets/site.css`: responsive design tokens, layouts, form states, print and reduced-motion rules.
- `assets/site.js`: mobile menu and private inquiry preparation.
- `assets/chat.js`: Tinker AI UI; calls the same-origin `/api/chat` endpoint and keeps recent chat only in memory.
- `server/chat-core.mjs`: shared Gemini backend; `server/knowledge.mjs`: generated knowledge bundle.
- `dist/`: public deployment output, excluding backend sources and local secrets.
- `assets/*.webp`: optimized derivatives of existing logo and illustration. Original `image/` assets stay intact.
- HTML, sitemap.xml, robots.txt, .nojekyll: generated deployable assets. CSS/JS receive content-hash cache keys.
- `tests/check_site.py`: source/HTML/link/schema/size validation.
- `tests/browser.cjs`: responsive, keyboard and request-flow browser verification.
- `tests/accessibility.cjs`: optional axe-core audit; set `TTW_AXE_PATH` to the installed `axe.min.js`. Both Playwright and axe are QA-only, not production runtime dependencies.

## Commands
```sh
python3 scripts/build_site.py
python3 tests/check_site.py
node scripts/chat_server.mjs  # website + chat API on 127.0.0.1:8787
# In another terminal, with Playwright installed:
node tests/browser.cjs
```
`TTW_PLAYWRIGHT_PATH` can point to an existing Playwright package directory; `TTW_BROWSER` can point to a Chrome/Chromium executable. Browser tests write screenshots under `/tmp/ttw-qa` by default, keeping them outside the published site.

## Hosting
Cloudflare Pages is the recorded current host. The current source working copy is `05_website/`; the deployable public asset root is now `05_website/dist/`. Run `python3 scripts/build_site.py` to generate both static assets and the server knowledge bundle. Pages compiles `functions/api/chat.js` and its `server/` imports separately. The browser uses `/api/chat` on the same origin.

Use the existing Cloudflare `GEMINI_API_KEY` secret, plus optional `GEMINI_MODEL`. Git builds use the site source as project root and `dist` as output. Wrangler deployments must run from the source root so it discovers `functions/`. Ordinary dashboard drag-and-drop of static files cannot deploy Pages Functions. Original `CNAME` and `.nojekyll` remain for compatibility. This implementation does not publish or change DNS.

## Inquiry behaviour and privacy boundary
No transport backend is configured. Form data lives only in the DOM. Validated request is rendered through `.value` / `.textContent`, never `innerHTML`; mailto fields use URI encoding. Copy and local text download provide alternatives to mailto length/client limitations. Editing invalidates a prior request. Consent is for this inquiry only. A working email client/user send action is necessary; the website never claims delivery.

Real slot booking or reliable server delivery requires a confirmed booking provider/API, domain-appropriate server credentials held server-side, spam controls, error/retry states, retention policy and delivery testing. Do not fabricate an endpoint or write “sent” because a mailto link was opened.

## Tinker (Gemini knowledge assistant)
The former quick-answer/keyword helper is replaced by a bilingual Gemini conversation UI. It includes up to four successful exchanges, source links validated against known documents, clear/reset, pending status, explicit failure and retry. There is no silent keyword fallback. Messages and recent history are sent to Google through the backend; no Key reaches the browser. The application does not persist chat transcripts or log message bodies.

Knowledge is compiled from six `knowledge/*.md` files during every site build. The backend applies conflict-handling rules for program prices vs old FAQ text, sample schedules vs generic confirmed claims, and future opening dates. These are grounding instructions, not a guarantee of factual correctness. Provider/model errors fail explicitly. Input bounds, abort timeouts, same-origin checks and a best-effort instance-local burst guard are implemented; an optional distributed rate-limit binding can be added.

See [Chatbot_Guide.md](Chatbot_Guide.md) for local startup, environment variables, knowledge maintenance, deployment, tests and data-handling details. Current development validation uses simulated provider responses; the Cloudflare production Key was reported configured by the user but not read or independently exercised in this task.

## Maintenance
Edit the content source and/or shared renderer, then regenerate; avoid hand-editing output HTML. Run structural checks after every regeneration. Keep the two languages synchronized. Public generated files remain directly reviewable, and history supplies rollback. Legacy product assets and manifest are retained. `/store.html` was retired 2026-09-17 once its listed services (3D printing, DTF, UV) became taught courses; the route now 404s and is not in the sitemap.

## Source code formatting
`scripts/build_site.py` and `assets/site.css` were reformatted 2026-09-17 from dense single-line output (some lines were several thousand characters) into human-readable, multi-line source, at the user's explicit request for long-term maintainability. This is now the standing convention — new code and edits should follow it, not reintroduce single-line blobs:

- **CSS**: one selector (or one selector per line for comma-separated groups) per rule opener, one declaration per line, a blank line between top-level rules, and `@media` blocks with their nested rules indented one level further. Property and value separated by `: ` (space after the colon), matching standard CSS style. Re-run this convention by hand when adding rules; there is no build-time formatter.
- **`build_site.py` HTML-generating f-strings**: Python concatenates adjacent string literals with nothing inserted between them, so a long f-string can always be split into several shorter f-string literals placed on their own (indented) lines inside parentheses, at natural HTML tag or attribute boundaries, **with zero effect on the generated output** — this is the safe way to shorten a line, and is strongly preferred over letting one statement grow past ~200 characters. Do not insert literal whitespace *inside* an inline text run that currently has none (e.g. between two adjacent inline elements meant to sit flush together) — that changes rendered spacing. Splitting is safe between block-level tags, before/after opening and closing tags, and around `{...}` expressions.
- Long Python literals (lists, dicts, comprehensions, function-call argument lists) should be wrapped across lines using the enclosing brackets/parens rather than left on one line — this never changes behaviour, only source layout.
- Prefer breaking a large page-building function into a few named local variables (e.g. `header = (...)`, `footer = (...)`) that are concatenated at the end, over one monolithic expression — see `render()` and `booking()` in `scripts/build_site.py` for the pattern.
- After any such reformatting, verify safety by rebuilding and diffing the generated HTML against a pre-change copy (whitespace-only or zero differences confirm the change was purely cosmetic) rather than relying on a visual check alone.

## Accessibility / performance strategy
Semantic landmarks and native details/select/input controls. Labels and explicit required states; visible focus; skip link; no keyboard traps. Responsive navigation remains fully displayed without JS. Mobile CTA does not cover the page bottom; focus targets scroll below the header. System fonts; local responsive WebP hero; below-fold logo lazy-loaded; dimensions reserve image space. Deferred JS only. Verify actual performance against the deployed host; local asset sizes are not Lighthouse or field Core Web Vitals scores.
