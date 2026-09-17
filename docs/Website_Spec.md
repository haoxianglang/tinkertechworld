# TTW Website Specification

Status: implementation specification derived from the user's current website brief and the source files below. No pre-existing approved website specification, or separately approved website-recommendations file, was found. This document must not be represented as a previously signed-off business plan.

## Purpose and scope
Improve the existing `tinkertechworld` repository and retain its domain, recognizable TTW logo, existing email and static-hosting compatibility. Help a parent understand what their learner could build, identify a suitable starting point, and request a trial. The initial public experience is an inquiry site, not an automated reservation or payment system.

Primary conversion: **Book a Trial Class**. Secondary: View Programs, Contact TTW, Join a Program. All paths are real HTML pages. Every new public page has an equivalent Simplified Chinese page, including enrollment and privacy information.

## Source hierarchy and conflicts
1. Current user instruction: exact five subject categories, four age bands, FLL page and conversion priorities. This overrides conflicting historical navigation proposals.
2. Existing website: `image/logo.png`, `image/Makerspace.png`, `CNAME`, contact email, founder names and roles. Historical web copy is not sufficient evidence of current operational readiness or professional credentials.
3. `Tinker Tech World.md`: brand values, capable makers, physical/software integration, learning cycle, four audience stages; no implied university affiliation.
4. `TTW Market Research Business Positioning Report.md` (2026-09-16), especially §§1, 9, 15–16; `TTW Market Intelligence Package/Program Recommendations.md` and `Marketing Recommendations.md`: narrow launch focus, visible availability, parent evidence, bilingual end-to-end flow, consistent product cards.
5. `Claude_课程体系重新规划_2026-09-13.md`: subject pathways and sample learning objectives. Proposed projects are illustrative, not delivered results.
6. `Internal Website/TTW_WRO_FLL_Program_Plan.html`: educational background only; its expansion from WRO to FLL is explicitly marked as requiring founder confirmation.
7. `00_context/final_review_disposition.md`: financial-review disposition; does not approve website claims or FLL operations.

The root `TTW_Ground_Truth.md` says core business facts are missing; `00_context/TTW_Ground_Truth.md` contains an evolving, different age/tier scheme. Neither silently overrides the current user brief. No prices, street address, opening date, real-time availability or instructor qualifications are asserted from these conflicting drafts.

The current brief requires FLL; strategy recommends WRO-first. Implement FLL as an inquiry/information page with no registered-team or affiliation claim. Keep `/competitions.html` as a current pathway overview acknowledging WRO planning. Official FLL overview checked 2026-09-17: https://www.firstinspires.org/programs/fll/. It now describes 2026–27 transition details; do not copy obsolete season names or fixed ages from the old instructor manual.

## Public content decisions
- Focus: LEGO Robotics / Grades 3–6 and Grades 7–9; do not claim current seats are available.
- Coding: block coding within robotics, advanced Python as planned.
- Electronics, 3D Design & Printing, Maker Engineering, high-school and adult pathways: clearly marked as future / interest only.
- Camps: dates, fees, location and registration unconfirmed; inquiries only.
- Project Gallery: clearly marked illustrative project ideas. No fabricated student photos, awards, results, testimonials or attendance metrics.
- Existing makerspace illustration is retained and optimized, with a visible concept-image caption. It is not advertised as a photo of TTW's facility.
- Retain founder names and roles from the prior About page; omit unverified credentials and any suggestion those people teach every class.
- Remove placeholder phone, broken WeChat QR and unsupported course breadth from the redesigned public journey.

## Design and UX
Warm off-white, dark blue-green text, and controlled blue/orange/green accents from the existing TTW logo. Large clear headings, generous spacing, restrained diagrams, no stock-photo claims or childish visual clutter. System fonts and no remote font calls. Shared cards, navigation, footer, CTA, FAQ, age paths, program details and inquiry form.

Home order: proposition + trial / programs → age paths → five subject cards → learning method → evidence of progress → parent FAQ → trial CTA. Visible availability is part of every course card. Learners can navigate by either grade or subject.

Mobile: responsive menu with expanded state, Escape close and keyboard operation; persistent trial CTA except on inquiry pages; minimum 44px principal controls; 320px+ layout. Content and navigation remain usable without JavaScript. Inquiry pages provide direct email fallback.

## Inquiry contract
Collect adult contact name and email, grade group, program interest, optional preferred time, three-character postal area, discovery source and a short question. Explicit inquiry consent, separate from marketing. Do not collect child name, birthday, health details or payments.

Validate → preview → open email / copy / download. Preparing or opening an email is never reported as delivery or confirmed booking. No data is stored in localStorage, cookies or a website backend. Editing fields invalidates the old preview. Prefill only known program/grade values; never render user input as HTML.

## Acceptance criteria
- Requested routes, bilingual counterparts, metadata, canonical/hreflang, sitemap and valid internal links.
- No horizontal scrolling at 320, 390, 768, 1024 or 1440px in generated pages.
- Accessible labels, one H1, semantic landmarks, focus visibility, native required-field validation, keyboard menu/FAQ, reduced-motion support.
- Trial and join paths can prepare accurate messages without network submission; injection-like text remains plain text; invalid inputs rejected.
- Optimized local hero with responsive sources, explicit image dimensions, deferred small JavaScript, no framework runtime or third-party tracking.
- Business launch status remains distinct from technical completion. True server-side booking requires a real booking service or endpoint and verified operational information.
