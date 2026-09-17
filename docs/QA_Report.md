# TTW Website Verification Record

Verified 2026-09-16 (America/Toronto) / 2026-09-17 UTC.

## Scope and results
- 50 static HTML pages: 25 English and 25 Simplified Chinese, including 404 and the retained legacy store inquiry route.
- 46 indexable sitemap entries; 404 and store excluded in both languages.
- Structural checks passed: local links and fragments, single H1/main/title, unique IDs, labeled form controls, image alt/dimensions, descriptions, canonical/hreflang, valid JSON-LD and asset budgets.
- Responsive browser checks passed for all 50 pages at 320, 390, 768, 1024 and 1440px: 250 page/viewport combinations, no horizontal document overflow or broken images.
- Browser behaviour checks passed: keyboard skip link, mobile menu Enter/Escape and focus, native FAQ expansion, invalid and required fields, preselected course/grade, safe rejection of unknown selections, language switch, trial vs join intent, consent, encoded email message, plain-text handling of HTML-like input, text download, clipboard/fallback feedback, and invalidation after editing.
- JavaScript-disabled checks passed for readable content, usable navigation and direct-email inquiry fallback.
- No JavaScript errors, failed local asset responses or POST submissions in the browser test run.
- axe-core 4.10.3: 50 pages at 390 and 1440px, 100 page/viewport combinations, **zero detected WCAG 2.1 A/AA rule violations**. This is an automated check, not a claim of comprehensive conformance or a substitute for assistive-technology testing.
- Desktop/mobile English home, Chinese home, program and inquiry screenshots visually reviewed. Fixed mobile brand/header wrapping, language-link wrapping and low-contrast dark-banner eyebrow text.
- Python/JavaScript syntax and `git diff --check` passed. Static site builds with Python standard library only.

## Asset sizes
| Resource | Bytes |
|---|---:|
| Shared JavaScript | 5,545 |
| Shared CSS | approximately 15 KB |
| Logo WebP | 10,704 |
| Desktop hero WebP | 175,768 |
| Mobile hero WebP | 73,980 |

Responsive local images, system fonts and deferred JS reduce transfer/rendering cost. These are measured file sizes, not Lighthouse or deployed Core Web Vitals results.

## Evidence
Automated scripts: `tests/check_site.py`, `tests/browser.cjs`, `tests/accessibility.cjs`. Local machine evidence was saved in `/tmp/ttw-qa`; durable copies of selected clean screenshots and JSON results are in the Obsidian TTW workspace under `06_testing/website/`.

Browser: installed Google Chrome through Playwright, headless. No Safari/Firefox or real-device screen-reader test was performed. No external emails were sent. The existing mailbox's actual receipt/deliverability was not verified.

## Release limitations
The site is a deployable static inquiry site. It does not reserve times, send a server-side form or process payments. A visitor must send the prepared email; TTW must confirm the request. Phone, street address, dates, fees, refund terms and active course/team availability remain unverified and are not fabricated. FLL is an information/inquiry page; official season details are linked to FIRST. Future programs and illustrative imagery/projects are explicitly labeled.

The implementation has not been committed, pushed or deployed. CNAME, existing original brand images, product assets and unrelated working-tree changes were retained.
