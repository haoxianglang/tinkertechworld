# Information Architecture

All routes below have a matching `/zh/` route. The header prioritizes Programs, Age Groups, FIRST LEGO League, WRO, Camps and About, with Membership as the header's rightmost button (changed from Book a Trial on 2026-09-17 at the user's request). The site's primary CTA itself was renamed the same day, everywhere it appears — hero, footer, every page's closing CTA banner, program/age-page "ask about this" buttons and the mobile sticky bar — from "Book a Trial Class / 预约体验课" to "Contact Us / 联系我们", and its page moved from `/book-a-trial.html` to `/contact-us.html` (the old route now 404s; the request-builder form, its fields and validation are unchanged, only the label and URL). This is a distinct page from `/contact.html` ("Contact TTW"), which was not touched — the footer now shows both "Contact TTW" and "Contact Us →" next to each other; flag this to the user if it reads as confusing. Footer and contextual links expose Gallery, FAQ, Contact and Join without overcrowding mobile navigation. Home is reachable from the brand and breadcrumbs.

| Area | URL | Role |
|---|---|---|
| Home | `/index.html` | Value proposition, age/subject discovery, primary conversion |
| Programs | `/programs/index.html` | All subjects, uniform availability labels |
| LEGO Robotics | `/programs/lego-robotics.html` | Foundational learning / trial inquiry |
| 3D Design & Printing | `/programs/3d-design-printing.html` | Future design / fabrication pathway |
| Distilled Series | `/programs/distilled.html` | High-school engineering/CS major exploration, future pathway / interest |
| World Robot Olympiad | `/programs/wro.html` | Category overview (RoboMission, RoboSports, Future Innovators, Future Engineers) as a course, kept in the main navigation; readiness inquiry, official-source citation, no team/registration claim |
| DTF Printing | `/programs/dtf-printing.html` | Teaches the DTF transfer process; future pathway / interest |
| UV Printing | `/programs/uv-printing.html` | Teaches direct-to-surface UV printing; future pathway / interest |
| Robotics for Adults | `/programs/robotics-for-adults.html` | Adult-beginner robotics workshop; future pathway / interest |
| IELTS Preparation | `/programs/ielts.html` | Four-section exam prep for high school/adult learners; future pathway / interest |
| Age Groups | `/age-groups/index.html` | Four entry paths |
| Grades 3–6 | `/age-groups/grades-3-6.html` | Explore & build |
| Grades 7–9 | `/age-groups/grades-7-9.html` | Control & integrate |
| High School | `/age-groups/high-school.html` | Future advanced pathway |
| Adult | `/age-groups/adult.html` | Future workshop interest |
| FIRST LEGO League | `/first-lego-league.html` | Information / readiness inquiry |
| Camps | `/camps.html` | Future school-break interest |
| Project Gallery | `/project-gallery.html` | Illustrative learning examples |
| About TTW | `/about.html` | Values, mission, founder roles |
| FAQ | `/faq.html` | Questions about selection and enrollment |
| Contact Us | `/contact-us.html` | Request builder, review and email handoff (renamed from Book a Trial 2026-09-17; same form/logic) |
| Membership | `/membership.html` | Planned membership benefits (interest only, not launched); linked from the header's rightmost button |
| Join | `/join.html` | Program interest using shared request flow |
| Contact | `/contact.html` | Direct email and local context |
| Learning Approach | `/makerspace.html` | Reuses existing URL for learning method |
| Competition Pathways | `/competitions.html` | Reuses existing URL; FLL info page and a link into the WRO course page |
| Privacy | `/privacy.html` | Actual website data handling |
| Not Found | `/404.html` | Recovery links, noindex |

`/store.html` (the prior "we make it for you" DTF/UV/3D-printing fabrication inquiry page) was retired on 2026-09-17: all three services it listed are now taught as courses (3D Design & Printing already was one; DTF Printing and UV Printing were added). Its route now 404s; nothing links to it. `/wro.html` was retired the same day in favour of `/programs/wro.html`, which carries over its category detail, official-source citation and trademark disclaimer.

Subject page → preselected trial or join. Age page → preselected grade inquiry or relevant subject pages. Future offerings lead to interest discussions rather than false checkout. Header/footer/home CTA always resolves to the inquiry page. Language switching retains the same content route and validated selections on inquiry pages.
