# Technical Architecture

## Approach
Continue the existing static GitHub Pages-compatible site, with generated HTML at the site root. The current working copy is the TTW workspace’s `05_website/` directory; the original Dropbox repository is retained as a source copy and is not automatically synchronized. No framework migration, production Node server, runtime dependencies, external fonts or client-side router. SEO/content/navigation work before JavaScript loads.

- `content/site.json`: business settings and bilingual program/age records.
- `scripts/build_site.py`: Python 3 standard-library renderer with shared layout, navigation, footer, cards, CTA, FAQ, program/age layouts and inquiry layout.
- `assets/site.css`: responsive design tokens, layouts, form states, print and reduced-motion rules.
- `assets/site.js`: optional mobile menu and private inquiry preparation; no fetch, tracking or browser persistence.
- `assets/*.webp`: optimized derivatives of existing logo and illustration. Original `image/` assets stay intact.
- HTML, sitemap.xml, robots.txt, .nojekyll: generated deployable assets. CSS/JS receive content-hash cache keys.
- `tests/check_site.py`: source/HTML/link/schema/size validation.
- `tests/browser.cjs`: responsive, keyboard and request-flow browser verification.
- `tests/accessibility.cjs`: optional axe-core audit; set `TTW_AXE_PATH` to the installed `axe.min.js`. Both Playwright and axe are QA-only, not production runtime dependencies.

## Commands
```sh
python3 scripts/build_site.py
python3 tests/check_site.py
python3 -m http.server 4173 --bind 127.0.0.1
# In another terminal, with Playwright installed:
node tests/browser.cjs
```
`TTW_PLAYWRIGHT_PATH` can point to an existing Playwright package directory; `TTW_BROWSER` can point to a Chrome/Chromium executable. Browser tests write screenshots under `/tmp/ttw-qa` by default, keeping them outside the published site.

## Hosting
Retain `CNAME` = `tinkertechworld.com`. The deployable root is `05_website/`: publish its contents through the hosting repository, not the entire TTW Obsidian workspace or the `docs/` directory. This copied folder does not include the original `.git` history; no deployment repository synchronization has been performed. `.nojekyll` disables unintended Jekyll processing. Configure HTTPS in the host. Domain DNS and publication were not changed by this implementation. Run build/check/browser verification before committing and publishing. A GitHub Pages deployment remains a separate release action.

## Inquiry behaviour and privacy boundary
No transport backend is configured. Form data lives only in the DOM. Validated request is rendered through `.value` / `.textContent`, never `innerHTML`; mailto fields use URI encoding. Copy and local text download provide alternatives to mailto length/client limitations. Editing invalidates a prior request. Consent is for this inquiry only. A working email client/user send action is necessary; the website never claims delivery.

Real slot booking or reliable server delivery requires a confirmed booking provider/API, domain-appropriate server credentials held server-side, spam controls, error/retry states, retention policy and delivery testing. Do not fabricate an endpoint or write “sent” because a mailto link was opened.

## Maintenance
Edit the content source and/or shared renderer, then regenerate; avoid hand-editing output HTML. Run structural checks after every regeneration. Keep the two languages synchronized. Public generated files remain directly reviewable, and history supplies rollback. Legacy product assets and manifest are retained. The store route is kept as a low-priority inquiry page, noindex and excluded from sitemap.

## Accessibility / performance strategy
Semantic landmarks and native details/select/input controls. Labels and explicit required states; visible focus; skip link; no keyboard traps. Responsive navigation remains fully displayed without JS. Mobile CTA does not cover the page bottom; focus targets scroll below the header. System fonts; local responsive WebP hero; below-fold logo lazy-loaded; dimensions reserve image space. Deferred JS only. Verify actual performance against the deployed host; local asset sizes are not Lighthouse or field Core Web Vitals scores.
