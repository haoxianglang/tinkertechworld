#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build TTW's bilingual, dependency-free static site. Run from any directory.

Formatting convention for this file (see 04_website_spec/Technical_Architecture.md):
- Long HTML f-strings are split into adjacent string-literal fragments, one
  HTML tag or logical chunk per line, joined inside parentheses. Python
  concatenates adjacent literals with nothing in between, so this is purely
  a source-readability change and never alters the generated output.
- Long Python literals (lists, dicts, comprehensions) are wrapped across
  lines the same way, using the enclosing brackets/parens.
- Keep line length reasonable so the file can be read without horizontal
  scrolling; prefer another split point over a long line.
"""
import json, html, hashlib
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'content/site.json').read_text())
LANG = 'en'
ROUTE = ''
pages = []
written = set()


# ============================================================
# Small content helpers: translation, escaping, links, buttons
# ============================================================

def t(en, zh=None):
    """Return the string for the current LANG. `en` may be [en, zh] or a plain string."""
    if isinstance(en, list):
        return en[LANG == 'zh']
    return zh if LANG == 'zh' and zh is not None else en


def esc(value):
    return html.escape(str(value), quote=True)


def url(route='index.html', lang=None):
    return ('/zh/' if (lang or LANG) == 'zh' else '/') + route


def link(route, label, cls='', **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{esc(v)}"' for k, v in attrs.items())
    return f'<a href="{esc(url(route))}" class="{cls}" {extra}>{label}</a>'


def button(label=None, route='contact-us.html', cls='primary'):
    return link(route, label or t('Contact Us', '联系我们'), 'button ' + cls)


def eye(en, zh):
    return f'<p class="eyebrow">{t(en, zh)}</p>'


def section(body, cls=''):
    return f'<section class="section {cls}"><div class="wrap">{body}</div></section>'


# ============================================================
# Program-card icons (inline SVG, shared line-art style)
# ============================================================

def icon(kind):
    shapes = {
        'robot': (
            '<path d="M65 38V24m70 14V24"/>'
            '<circle cx="65" cy="20" r="5" fill="#faac45"/>'
            '<circle cx="135" cy="20" r="5" fill="#faac45"/>'
            '<rect x="43" y="39" width="114" height="77" rx="18" fill="#bfe6f1"/>'
            '<rect x="59" y="54" width="82" height="46" rx="12" fill="#fff"/>'
            '<circle cx="82" cy="75" r="5" fill="#152f3b"/>'
            '<circle cx="118" cy="75" r="5" fill="#152f3b"/>'
            '<path d="M90 88q10 9 20 0M31 67v25m138-25v25M67 117v15m66-15v15"/>'
            '<rect x="48" y="130" width="35" height="13" rx="4" fill="#faac45"/>'
            '<rect x="117" y="130" width="35" height="13" rx="4" fill="#faac45"/>'
        ),
        'code': (
            '<rect x="24" y="29" width="152" height="103" rx="12" fill="#fff"/>'
            '<path d="M24 49h152"/>'
            '<circle cx="38" cy="40" r="2"/><circle cx="48" cy="40" r="2"/>'
            '<path d="m73 69-20 20 20 20m54-40 20 20-20 20m-16-47-19 56" stroke="#187a5a"/>'
            '<path d="M58 143h84"/>'
        ),
        'circuit': (
            '<rect x="64" y="48" width="72" height="65" rx="7" fill="#faac45"/>'
            '<path d="M78 34v14m22-14v14m22-14v14M78 113v16m22-16v16m22-16v16'
            'M64 65H34V35m30 62H27v34m109-66h35V35m-35 62h36v34"/>'
            '<rect x="83" y="65" width="34" height="31" rx="3" fill="#fff"/>'
            '<circle cx="34" cy="29" r="6" fill="#fff"/><circle cx="171" cy="29" r="6" fill="#fff"/>'
            '<circle cx="27" cy="136" r="6" fill="#fff"/><circle cx="172" cy="136" r="6" fill="#fff"/>'
        ),
        'cube': (
            '<path d="m100 19 64 36v69l-64 36-64-36V55Z" fill="#e1d8f7"/>'
            '<path d="m36 55 64 37 64-37M100 92v68M67 38l65 36v67"/>'
            '<path d="M18 38v99m-5-94 5-5 5 5m-10 89 5 5 5-5" stroke="#8a76b5"/>'
        ),
        'gear': (
            '<path d="M33 115 73 44l74 12 25 65-76 28Z" fill="#d2e8df"/>'
            '<circle cx="94" cy="86" r="30" fill="#fff"/>'
            '<circle cx="94" cy="86" r="12" fill="#faac45"/>'
            '<path d="M94 45v11m0 60v11m-41-41h11m60 0h11'
            'M65 57l8 8m42 42 8 8m0-58-8 8m-42 42-8 8"/>'
            '<circle cx="33" cy="115" r="8" fill="#faac45"/>'
            '<circle cx="147" cy="56" r="8" fill="#bfe6f1"/>'
        ),
        'signpost': (
            '<ellipse cx="99" cy="152" rx="24" ry="7" fill="#ede4f7"/>'
            '<rect x="93" y="45" width="10" height="107" rx="4" fill="#8a76b5"/>'
            '<path d="M99 56h54l17 16-17 16H99Z" fill="#faac45"/>'
            '<path d="M99 96H44l-17 16 17 16h55Z" fill="#bfe6f1"/>'
            '<circle cx="99" cy="72" r="6" fill="#fff"/><circle cx="99" cy="112" r="6" fill="#fff"/>'
        ),
        'exam': (
            '<rect x="50" y="20" width="100" height="135" rx="10" fill="#dceaf5"/>'
            '<rect x="66" y="42" width="68" height="8" rx="4" fill="#fff"/>'
            '<rect x="66" y="62" width="68" height="8" rx="4" fill="#fff"/>'
            '<rect x="66" y="82" width="44" height="8" rx="4" fill="#fff"/>'
            '<circle cx="138" cy="120" r="28" fill="#faac45"/>'
            '<path d="m125 120 9 9 18-19" fill="none" stroke="#fff" stroke-width="6" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        ),
        'compass': (
            '<circle cx="100" cy="87" r="58" fill="#e5f0e9"/>'
            '<circle cx="100" cy="87" r="42" fill="#fff"/>'
            '<path d="M100 32v20m0 70v20m-58-58h20m70 0h20"/>'
            '<path d="m100 58 16 29-16 29-16-29Z" fill="#bfe6f1"/>'
            '<circle cx="100" cy="87" r="8" fill="#faac45"/>'
        ),
        'medal': (
            '<path d="M76 26h48l22 40-46 22-46-22Z" fill="#fde3c0"/>'
            '<circle cx="100" cy="110" r="38" fill="#fff"/>'
            '<path d="m100 88 8 16 18 3-13 12 3 18-16-9-16 9 3-18-13-12 18-3Z" fill="#faac45"/>'
        ),
        'shirt': (
            '<path d="M72 32 46 52l13 23 19-13v84h80V62l19 13 13-23-26-20-19 13H91Z" fill="#e1d8f7"/>'
            '<rect x="80" y="70" width="40" height="30" rx="5" fill="#fff"/>'
            '<path d="M88 78h24m-24 8h24m-18 8h12"/>'
        ),
        'sticker': (
            '<circle cx="100" cy="100" r="46" fill="#fde3c0"/>'
            '<path d="M100 40v16m0 88v16m-60-60h16m88 0h16'
            'M58 58l11 11m62 62 11 11M142 58l-11 11M69 131l-11 11"/>'
            '<circle cx="100" cy="100" r="20" fill="#faac45"/>'
        ),
        'speech': (
            '<path d="M35 45h130a12 12 0 0 1 12 12v55a12 12 0 0 1-12 12H95l-30 25v-25H35'
            'a12 12 0 0 1-12-12V57a12 12 0 0 1 12-12Z" fill="#dceaf5"/>'
            '<path d="M55 75h90M55 95h60"/>'
        ),
        'arm': (
            '<rect x="42" y="132" width="116" height="22" rx="6" fill="#e1d8f7"/>'
            '<circle cx="100" cy="122" r="12" fill="#fff"/>'
            '<path d="M100 122 66 76"/><circle cx="66" cy="76" r="10" fill="#fff"/>'
            '<path d="M66 76 133 48"/><circle cx="133" cy="48" r="8" fill="#faac45"/>'
            '<path d="M133 48 118 27M133 48 150 33"/>'
        ),
        'brick': (
            '<rect x="37" y="76" width="126" height="46" rx="9" fill="#d2e8df"/>'
            '<circle cx="65" cy="76" r="13" fill="#d2e8df"/>'
            '<circle cx="100" cy="76" r="13" fill="#d2e8df"/>'
            '<circle cx="135" cy="76" r="13" fill="#d2e8df"/>'
            '<circle cx="65" cy="76" r="6" fill="#fff"/>'
            '<circle cx="100" cy="76" r="6" fill="#fff"/>'
            '<circle cx="135" cy="76" r="6" fill="#fff"/>'
            '<rect x="57" y="122" width="86" height="34" rx="8" fill="#fde3c0"/>'
            '<circle cx="80" cy="122" r="10" fill="#fde3c0"/>'
            '<circle cx="120" cy="122" r="10" fill="#fde3c0"/>'
            '<circle cx="80" cy="122" r="5" fill="#fff"/>'
            '<circle cx="120" cy="122" r="5" fill="#fff"/>'
        ),
    }
    return (
        f'<svg viewBox="0 0 200 175" fill="none" stroke="#244956" stroke-width="3" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{shapes[kind]}</svg>'
    )


# ============================================================
# Repeated card / grid blocks
# ============================================================

def program_card_html(p):
    status_badge = '' if p['slug'] == 'lego-robotics' else f'''<span class="status">{t(p['status'])}</span>'''
    return (
        f'''<article class="card program-card {p['color']}">'''
        f'''<div class="card-visual">{icon(p['icon'])}</div>'''
        f'''<p class="meta">{t(p['grade'])}</p>'''
        f'''<h3>{link('programs/' + p['slug'] + '.html', t(p['name']), 'title')}</h3>'''
        f'''{status_badge}'''
        f'''<p>{t(p['description'])}</p>'''
        f'''{link('programs/' + p['slug'] + '.html', t('Explore this program →', '了解此课程 →'), 'text-link')}'''
        f'''</article>'''
    )


def program_cards(items=None, extra=''):
    rows = items or DATA['programs']
    return '<div class="grid program-grid">' + ''.join(program_card_html(p) for p in rows) + extra + '</div>'


def fll_card():
    return (
        f'''<article class="card program-card green">'''
        f'''<div class="card-visual">{icon('brick')}</div>'''
        f'''<p class="meta">{t('Grades 4–12 · Team-based', '4–12 年级 · 团队制')}</p>'''
        f'''<h3>{link('first-lego-league.html', 'FIRST LEGO League', 'title')}</h3>'''
        f'''<span class="status">{t(
            'Future pathway · Ask about team opportunities',
            '未来学习方向 · 咨询战队机会',
        )}</span>'''
        f'''<p>{t(
            'A team challenge that brings building, coding and problem solving together. '
            'Ask TTW about readiness and potential team opportunities.',
            '将搭建、编程和解决问题结合在一起的团队挑战。欢迎向 TTW 咨询能力准备及潜在战队机会。',
        )}</p>'''
        f'''{link('first-lego-league.html', t('Explore this program →', '了解此课程 →'), 'text-link')}'''
        f'''</article>'''
    )


def age_cards():
    cards = (
        f'''<a class="card age-card" href="{url('age-groups/' + a['slug'] + '.html')}">'''
        f'''<span class="age-number">0{i + 1}</span>'''
        f'''<h3>{t(a['name'])}</h3><p>{t(a['verb'])}</p>'''
        f'''<span class="arrow" aria-hidden="true">↗</span></a>'''
        for i, a in enumerate(DATA['ages'])
    )
    return '<div class="grid four">' + ''.join(cards) + '</div>'


def cta():
    return section(
        f'''<div class="banner"><div>'''
        f'''{eye('A good place to begin', '从这里开始')}'''
        f'''<h2>{t('A little curiosity.<br>A world of possibilities.', '一点好奇心，<br>开启无限可能。')}</h2>'''
        f'''<p>{t(
            'Tell us about your learner. We’ll help you explore a suitable starting point and confirm trial availability.',
            '告诉我们孩子的兴趣与经验，一起寻找合适起点，并确认体验课安排。',
        )}</p>'''
        f'''</div>{button()}</div>'''
    )


# ============================================================
# Program pages: a showcase photo in place of the illustrative-
# project text block, for specific program slugs only.
# Each value: (webp filename, alt text en, alt text zh)
# ============================================================

PROGRAM_SHOWCASE_PHOTOS = {
    '3d-design-printing': ('3d-print-showcase.webp', 'Examples of 3D printed objects', '3D 打印作品示例'),
    'dtf-printing': ('dtf-showcase.webp', 'Examples of DTF printed transfers', 'DTF 转印作品示例'),
    'uv-printing': ('uv-showcase.webp', 'Examples of UV printed stickers and objects', 'UV 打印贴纸与作品示例'),
}


# ============================================================
# Program pages: an "About this class" intro + Learning Outcomes
# list, in place of the generic shared skills checklist, for
# specific program slugs only.
# Each value: (about en, about zh, [(outcome en, outcome zh), ...])
# ============================================================

PROGRAM_LEARNING_OUTCOMES = {
    '3d-design-printing': (
        'Learners move from a sketch to a digital model using beginner-friendly CAD tools, then take that '
        'design through slicing and printing. Along the way, they practise measuring for a purpose, checking '
        'fit against a real object, and revising a design based on what the printed result shows.',
        '学生从草图出发，使用适合初学者的 CAD 工具建立数字模型，再将设计经过切片、打印等步骤变成实物。'
        '在此过程中，练习有目的地测量、将作品与真实物体的配合效果进行比对，并根据打印结果修改设计。',
        [
            ('Sketch an idea and translate it into a simple 3D digital model', '将想法草图转化为简单的三维数字模型'),
            ('Use measurements and scale to design a part that fits a real object', '使用测量与比例设计出符合真实物体尺寸的零件'),
            ('Prepare a model for printing, including basic slicing settings', '为打印准备模型，了解基本的切片设置'),
            ('Compare a printed prototype with its intended fit and identify what to change',
             '将打印原型与预期配合效果比较，找出需要改进之处'),
            ('Revise a design through more than one iteration based on test results',
             '根据测试结果，对设计进行不止一轮的修改迭代'),
        ],
    ),
    'dtf-printing': (
        'Learners work through the direct-to-film printing process end to end: preparing artwork, seeing how '
        'film, powder and curing work together, and pressing a finished transfer onto fabric. Along the way, '
        'they build judgment around file prep, safe handling of heat and pressure, and evaluating a finished '
        'press for quality.',
        '学生完整走一遍 DTF 转印流程：准备设计稿，理解转印膜、粉浆与固化如何配合，并将成品转印图案压烫到织物上。'
        '在此过程中，练习文件准备的判断力，安全操作高温与压力设备，并评估压烫成品的质量。',
        [
            ('Prepare a design file for DTF printing: resolution, colour and file format',
             '为 DTF 打印准备设计文件：分辨率、色彩与文件格式'),
            ('Explain how the DTF process works: printing, powder application and curing',
             '说明 DTF 工艺流程：打印、上粉与固化'),
            ('Press a transfer correctly using the right temperature, pressure and timing',
             '使用合适的温度、压力与时间正确压烫转印'),
            ('Follow safety steps when working with heat and printing equipment',
             '在操作高温与打印设备时遵循安全规范'),
            ('Compare a finished press against the original design and adjust settings for a cleaner result',
             '将压烫成品与原设计比较，调整参数以获得更好效果'),
        ],
    ),
    'uv-printing': (
        'Learners see how a UV printer applies ink directly onto a surface such as acrylic, wood or metal and '
        'cures it instantly with UV light. Along the way, they prepare a design file for a specific material '
        'and print area, test settings on samples, and compare a finished print against the original design.',
        '学生了解 UV 打印机如何将油墨直接印在亚克力、木材、金属等表面，并用紫外光即时固化。'
        '在此过程中，为特定材质与印刷范围准备设计文件，在样品材料上测试打印参数，并将成品与原设计进行比较。',
        [
            ('Prepare a design file sized and formatted for a specific surface and print area',
             '为特定材质与印刷范围准备设计文件'),
            ('Explain how UV-cured ink layers, gloss and texture affect a finished piece',
             '说明 UV 固化油墨的层次、光泽与质感如何影响成品'),
            ('Test print settings on sample materials before running a final print',
             '在样品材料上测试打印参数，再进行正式打印'),
            ('Follow safety steps when operating UV printing equipment',
             '在操作 UV 打印设备时遵循安全规范'),
            ("Compare a finished print's colour and finish against the original design and adjust",
             '将成品的颜色与效果与原设计比较并作出调整'),
        ],
    ),
}


# ============================================================
# Program pages: "Format" / "Schedule & tuition" facts-card
# overrides, for specific program slugs only.
# Each value: (format en, format zh, tuition en, tuition zh)
# ============================================================

PROGRAM_FACTS_OVERRIDES = {
    'wro': (
        'Pre-Team and Competition Team', 'Pre-Team 和 Competition Team',
        'Starts every January, Pre-Team $60/class, Competition Team $80/class',
        '每年1月开始，Pre-Team $60每节课，Competition Team $80每节课',
    ),
    'distilled': (
        'Guided, project-based learning (Mechanical, Electrical, Computer Engineering)',
        '指导下开展项目学习（机械工程，电子工程，计算机工程）',
        'One class per week, 16 classes total, $60/class',
        '每星期1节课，总共16节课，$60 每节课',
    ),
}


# ============================================================
# News updates (Home "News & Updates" section)
# Each entry: (color class, tag, title, description, date fields)
# ============================================================

NEWS_UPDATES = [
    ('highlight', 'Highlight', '精彩时刻',
     'TTW officially launches', 'TTW 正式上线',
     'Tinker Tech World opens its doors in Markham.',
     'Tinker Tech World 万锦校区正式开放。',
     'November 1, 2026', '2026年11月1日'),
    ('events', 'Events', '活动',
     'Open House Day', '开放日',
     'Details to be announced.',
     '详情稍后公布。',
     'November 22, 2026', '2026年11月22日'),
]


# ============================================================
# Parent FAQ content (shared by Home preview and the full FAQ page)
# ============================================================

FAQ = [
    ['Does my child need experience?', '孩子需要有基础吗？',
     'No prior robotics experience is needed to ask about the Grades 3–6 starting pathway. '
     'For older learners, share their interests and experience so TTW can discuss a suitable entry point.',
     '咨询 3–6 年级入门方向不需要机器人基础。对于高年级学生，请提供兴趣与经验，以便沟通合适的学习起点。'],
    ['Which program should we choose?', '应该选择哪门课程？',
     'Start with the learner’s grade and what they enjoy making. LEGO Robotics connects building and block coding; '
     '3D design and, for high schoolers, the Distilled series can extend those interests as these pathways become available.',
     '可从学生的年级和创作兴趣出发。LEGO 机器人结合搭建与图形化编程；3D 设计以及面向高中生的 Distilled 系列可在开放后延伸这些兴趣。'],
    ['What does a trial request include?', '体验申请包含什么？',
     'Share a grade group, program interest and preferred timing. TTW will discuss the activity, location, duration '
     'and any fee before confirming a place. An inquiry does not reserve a seat.',
     '提供年级、课程兴趣和希望的时间。TTW 将在确认席位前沟通活动、地点、时长及费用。提交咨询不等于预留席位。'],
    ['What are the fees and class times?', '费用和上课时间是什么？',
     'Schedules, session counts, fees, tax treatment and equipment inclusions are not yet published. '
     'Ask for the current details in writing before deciding to enroll.',
     '排期、课次、费用、税费及设备是否包含尚未公布。请在决定报名前索取当前书面信息。'],
    ['Can we learn without joining a competition?', '不参加比赛也可以学习吗？',
     'Yes. The learning approach values building, testing and explaining a project in its own right. '
     'Competition is an optional direction, subject to a suitable group and current eligibility.',
     '可以。学习方向重视搭建、测试和解释项目本身。竞赛属于可选路径，需结合合适的班组与当季参赛资格。'],
    ['Are all listed programs running now?', '网站上所有课程都已开班吗？',
     'No. Core robotics pathways are the initial focus. Advanced CAD, the Distilled series, high school pathways '
     'and adult workshops include future offerings. Each page identifies its status; confirm availability with TTW.',
     '并非所有课程都已开班。初期重点是核心机器人路径；进阶 CAD、Distilled 系列、高中及成人工作坊包含未来计划。'
     '各页面会标明状态，请向 TTW 确认可用课程。'],
    ['Where will classes take place?', '课程在哪里上？',
     'TTW is located at 15A, 20 Crown Steel Drive, Markham, ON L3R 9X8. '
     'Confirm parking and arrival instructions with TTW before your visit.',
     'TTW 地址为 15A, 20 Crown Steel Drive, Markham, ON L3R 9X8。到访前请向 TTW 确认停车及到达指引。'],
    ['What about supervision, pickup and missed classes?', '安全指导、接送和缺课如何安排？',
     'Before enrollment, request the class supervision arrangements, authorized-pickup procedure, equipment guidance, '
     'and written refund and makeup terms. These details will depend on the confirmed offering.',
     '报名前，请索取课堂指导安排、授权接送流程、设备使用指导，以及退款和补课的书面条款。具体安排取决于最终确认的课程。'],
]


def faqs(all=False):
    rows = FAQ if all else FAQ[:4]
    items = (f'<details><summary>{t(x[0], x[1])}</summary><p>{t(x[2], x[3])}</p></details>' for x in rows)
    return '<div class="faq">' + ''.join(items) + '</div>'


def heading(title, desc, kicker=None, desc_cls='lead'):
    return (
        f'''<div class="wrap"><div class="page-hero">'''
        f'''{eye(*(kicker or ["Build skills. Make discoveries.", "积累技能，探索新知。"]))}'''
        f'''<h1>{title}</h1><p class="{desc_cls}">{desc}</p>'''
        f'''</div></div>'''
    )


# ============================================================
# Tinker: lightweight, client-side FAQ chat widget.
# No backend, no third-party API, no fetch — the current language's
# FAQ pairs are inlined as JSON on every page and matched in the
# browser by assets/site.js. See Technical_Architecture.md.
# ============================================================

def tinker_widget():
    tinker_data = {
        'greeting': t(
            'Hi, I’m Tinker! Ask me about programs, trials or how TTW works.',
            '你好，我是 Tinker！可以问我课程、体验课或 TTW 的相关问题。',
        ),
        'fallback': t(
            'I’m not sure about that one yet — ask TTW directly and they’ll help.',
            '这个问题我暂时还不确定，直接联系 TTW，他们会帮你解答。',
        ),
        'fallbackLinkText': t('Contact TTW →', '联系 TTW →'),
        'fallbackLinkHref': url('contact-us.html'),
        'qa': [{'q': t(x[0], x[1]), 'a': t(x[2], x[3])} for x in FAQ],
    }
    return (
        f'''<div class="tinker">'''
        f'''<button class="tinker-launcher" id="tinker-launcher" type="button" '''
        f'''aria-expanded="false" aria-controls="tinker-panel" '''
        f'''aria-label="{t('Chat with Tinker', '和 Tinker 聊聊')}">'''
        f'''<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" '''
        f'''stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'''
        f'''<path d="M21 11.5a8.38 8.38 0 0 1-4.55 7.46 8.5 8.5 0 0 1-8.31-.08L3 21l2.12-5.14 '''
        f'''a8.38 8.38 0 0 1-.9-3.86 8.5 8.5 0 0 1 12.72-7.36A8.48 8.48 0 0 1 21 11.5Z"/>'''
        f'''</svg>'''
        f'''</button>'''
        f'''<section class="tinker-panel" id="tinker-panel" hidden aria-label="Tinker">'''
        f'''<div class="tinker-head">'''
        f'''<div><h2>Tinker</h2><span>{t('TTW’s quick-answer helper', 'TTW 快速问答助手')}</span></div>'''
        f'''<button class="tinker-close" id="tinker-close" type="button" '''
        f'''aria-label="{t('Close chat', '关闭聊天')}">✕</button>'''
        f'''</div>'''
        f'''<div class="tinker-messages" id="tinker-messages" role="log" aria-live="polite"></div>'''
        f'''<form class="tinker-form" id="tinker-form">'''
        f'''<label for="tinker-input" class="sr-only">{t('Ask Tinker a question', '向 Tinker 提问')}</label>'''
        f'''<input id="tinker-input" name="tinker-input" type="text" autocomplete="off" '''
        f'''maxlength="200" placeholder="{t('Ask a question…', '请输入问题…')}">'''
        f'''<button type="submit" class="button primary">{t('Send', '发送')}</button>'''
        f'''</form>'''
        f'''<script type="application/json" id="tinker-data">{json.dumps(tinker_data, ensure_ascii=False)}</script>'''
        f'''</section>'''
        f'''</div>'''
    )


# ============================================================
# Page shell: <head>, header/nav, footer, mobile CTA
# ============================================================

def render(route, title, desc, body, nav='', noindex=False):
    global ROUTE
    ROUTE = route
    navs = [
        ('index.html', t('Home', '首页'), 'home'),
        ('programs/index.html', t('Programs', '课程'), 'programs'),
        ('schedule.html', t('Schedule', '课程安排'), 'schedule'),
        ('camps.html', t('Camps', '营地'), 'camps'),
        ('about.html', t('About', '关于'), 'about'),
    ]
    navigation = ''.join(
        link(r, l, aria_current='page') if n == nav else link(r, l)
        for r, l, n in navs
    )
    canonical = DATA['url'] + url(route)
    og = DATA['url'] + '/image/Makerspace.png'
    schema = {
        '@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'description': desc,
        'url': canonical, 'inLanguage': t('en-CA', 'zh-Hans'),
        'isPartOf': {'@type': 'WebSite', 'name': DATA['name'], 'url': DATA['url']},
    }
    if route == 'index.html':
        schema = {
            '@context': 'https://schema.org', '@type': 'EducationalOrganization',
            'name': DATA['name'], 'url': DATA['url'], 'logo': DATA['url'] + '/image/logo.png',
            'email': DATA['email'],
            'address': {
                '@type': 'PostalAddress', 'streetAddress': '15A, 20 Crown Steel Drive',
                'addressLocality': 'Markham', 'addressRegion': 'ON', 'postalCode': 'L3R 9X8',
                'addressCountry': 'CA',
            },
            'areaServed': {'@type': 'City', 'name': 'Markham'},
        }
    prefix = t('en', 'zh-Hans')
    csshash = hashlib.sha256((ROOT / 'assets/site.css').read_bytes()).hexdigest()[:10]
    jshash = hashlib.sha256((ROOT / 'assets/site.js').read_bytes()).hexdigest()[:10]

    head = (
        f'''<!doctype html>\n'''
        f'''<html lang="{prefix}"><head>'''
        f'''<meta charset="utf-8">'''
        f'''<meta name="viewport" content="width=device-width,initial-scale=1">'''
        f'''<title>{esc(title)} | Tinker Tech World</title>'''
        f'''<meta name="description" content="{esc(desc)}">'''
        f'''<meta name="theme-color" content="#152f3b">'''
        f'''<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow'}">'''
        f'''<link rel="canonical" href="{canonical}">'''
        f'''<link rel="alternate" hreflang="en-CA" href="{DATA['url'] + url(route, 'en')}">'''
        f'''<link rel="alternate" hreflang="zh-Hans" href="{DATA['url'] + url(route, 'zh')}">'''
        f'''<link rel="alternate" hreflang="x-default" href="{DATA['url'] + url(route, 'en')}">'''
        f'''<meta property="og:type" content="website">'''
        f'''<meta property="og:title" content="{esc(title)} | Tinker Tech World">'''
        f'''<meta property="og:description" content="{esc(desc)}">'''
        f'''<meta property="og:url" content="{canonical}">'''
        f'''<meta property="og:image" content="{og}">'''
        f'''<meta property="og:image:alt" content="{t('TTW makerspace concept illustration', 'TTW 创客空间概念示意图')}">'''
        f'''<meta name="twitter:card" content="summary_large_image">'''
        f'''<link rel="icon" type="image/webp" href="/assets/logo.webp">'''
        f'''<link rel="stylesheet" href="/assets/site.css?v={csshash}">'''
        f'''<script src="/assets/site.js?v={jshash}" defer></script>'''
        f'''<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'''
        f'''</head>\n'''
    )

    topbar = (
        f'''<body data-language="{LANG}">'''
        f'''<a class="skip" href="#main">{t('Skip to content', '跳到正文')}</a>'''
        f'''<div class="topbar"><div class="wrap">'''
        f'''<span>{t('Markham, Ontario', '安大略省万锦市')}</span>'''
        f'''</div></div>\n'''
    )

    header = (
        f'''<header class="site-header"><div class="wrap header-row">'''
        f'''<a class="brand" href="{url()}" aria-label="Tinker Tech World">'''
        f'''<img src="/assets/logo.webp" width="90" height="75" alt="Tinker Tech World">'''
        f'''<span class="brand-tagline">{t('Building skills for a changing world', '为不断变化的世界培养技能')}</span>'''
        f'''</a>'''
        f'''<button class="menu-toggle" aria-expanded="false" aria-controls="navigation">'''
        f'''{t('Menu', '菜单')} <span aria-hidden="true">☰</span></button>'''
        f'''<nav class="nav" id="navigation" aria-label="{t('Main navigation', '主导航')}">{navigation}</nav>'''
        f'''<div class="header-trial"><a class="button primary" href="{url(route, 'zh' if LANG == 'en' else 'en')}" '''
        f'''lang="{'zh-Hans' if LANG == 'en' else 'en'}" '''
        f'''hreflang="{'zh-Hans' if LANG == 'en' else 'en-CA'}">{t('中文', 'English')}</a></div>'''
        f'''</div></header>\n'''
    )

    breadcrumb = (
        '' if route == 'index.html' else
        '<nav class="wrap breadcrumbs" aria-label="' + t('Breadcrumb', '面包屑导航') + '">'
        + link('index.html', t('Home', '首页')) + ' / <span>' + esc(title) + '</span></nav>'
    )
    main = f'''<main id="main" tabindex="-1">{breadcrumb}{body}</main>\n'''

    footer = (
        f'''<footer class="footer"><div class="wrap"><div class="footer-grid">'''
        f'''<div>'''
        f'''<a class="brand" href="{url()}" aria-label="Tinker Tech World">'''
        f'''<img src="/assets/logo.webp" width="90" height="75" loading="lazy" alt="Tinker Tech World"></a>'''
        f'''<p>{t('A place for curious minds<br>and capable makers.', '让好奇的头脑，<br>成长为有能力的创客。')}</p>'''
        f'''<p>{t(DATA['location'])}</p>'''
        f'''</div>'''
        f'''<div><h3>{t('Explore', '探索')}</h3>'''
        f'''{link('programs/index.html', t('All Programs', '全部课程'))}'''
        f'''{link('age-groups/index.html', t('Find Your Age Group', '按年龄选课'))}'''
        f'''{link('first-lego-league.html', 'FIRST LEGO League')}'''
        f'''{link('programs/wro.html', 'World Robot Olympiad')}'''
        f'''{link('camps.html', t('Camps', '营地'))}'''
        f'''{link('project-gallery.html', t('Project Gallery', '项目展示'))}'''
        f'''</div>'''
        f'''<div><h3>{t('Get to know TTW', '了解 TTW')}</h3>'''
        f'''{link('about.html', t('About TTW', '关于 TTW'))}'''
        f'''{link('makerspace.html', t('Our Learning Approach', '学习方式'))}'''
        f'''{link('faq.html', t('Parent FAQ', '家长常见问题'))}'''
        f'''{link('contact.html', t('Contact TTW', '联系 TTW'))}'''
        f'''{link('privacy.html', t('Privacy', '隐私说明'))}'''
        f'''</div>'''
        f'''<div><h3>{t('Start a conversation', '开启对话')}</h3>'''
        f'''<a href="mailto:{DATA['email']}">{DATA['email']}</a>'''
        f'''<div class="footer-qr-row">'''
        f'''<div class="footer-qr"><img src="/assets/cs-qr.webp" width="400" height="400" loading="lazy" '''
        f'''alt="{t('WeChat customer service QR code', '客服微信二维码')}"><span>{t('WeChat CS', '客服微信')}</span></div>'''
        f'''</div>'''
        f'''</div>'''
        f'''</div>'''
        f'''<div class="footer-bottom">'''
        f'''<span>© 2026 Tinker Tech World</span>'''
        f'''<span>{t('Imagine · Build · Test · Improve', '构思 · 搭建 · 测试 · 改进')}</span>'''
        f'''</div></div></footer>\n'''
    )

    mobile_cta = (
        '' if route == 'contact-us.html' else
        '<aside class="mobile-cta" aria-label="' + t('Contact', '联系') + '">'
        '<span>' + t('Find their starting point.', '找到适合孩子的起点。') + '</span>'
        + button() + '</aside>'
    )

    tinker = tinker_widget()

    content = head + topbar + header + main + footer + mobile_cta + tinker + '</body></html>'

    dest = ROOT / (('zh/' if LANG == 'zh' else '') + route)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
    written.add(dest)
    if not noindex:
        pages.append(canonical)


# ============================================================
# Home page
# ============================================================

def home():
    hero = (
        f'''<section class="hero"><div class="wrap"><div class="hero-grid">'''
        f'''<div class="hero-copy">'''
        f'''{eye('Hands-on STEM learning in Markham', '万锦市 · 动手实践 STEM 学习')}'''
        f'''<h1>{t('Little sparks.<br><em>Big discoveries.</em>', '小小灵感，<br><em>大大发现。</em>')}</h1>'''
        f'''<p class="lead">{t(
            'Welcome to Tinker Tech World – Where Learning Gets Real',
            '欢迎来到 Tinker Tech World —— 让学习变得真实',
        )}</p>'''
        f'''<div class="actions">'''
        f'''{button(t('Membership Info ↗', '会员说明 ↗'), 'membership.html')}'''
        f'''{button(t('Member Login / Booking', '会员登录/预约'), 'booking.html', 'outline')}'''
        f'''{button(t('Browse Programs →', '课程浏览 →'), 'programs/index.html', 'outline')}'''
        f'''</div>'''
        f'''</div>'''
        f'''<figure class="hero-visual">'''
        f'''<img class="hero-photo" src="/assets/makerspace.webp" '''
        f'''srcset="/assets/makerspace-small.webp 640w, /assets/makerspace.webp 1200w" '''
        f'''sizes="(max-width:760px) 92vw, 50vw" width="1200" height="800" fetchpriority="high" '''
        f'''alt="{t('Concept illustration of learners exploring robotics in a makerspace', '学生在创客空间探索机器人的概念示意图')}">'''
        f'''<div class="photo-label">'''
        f'''<b>{t('Less watching. More wondering.', '动手尝试，主动探索。')}</b>'''
        f'''<span>{t('Imagine → Build → Test → Improve', '构思 → 搭建 → 测试 → 改进')}</span>'''
        f'''</div>'''
        f'''<figcaption>{t(
            'TTW learning-space concept illustration; not a facility photograph.',
            'TTW 学习空间概念示意图，并非实际场地照片。',
        )}</figcaption>'''
        f'''</figure>'''
        f'''</div>'''
        f'''</div></section>'''
    )
    body = hero
    body += section(
        f'''<div class="section-head"><div>'''
        f'''{eye('Find their starting point', '找到适合的起点')}'''
        f'''<h2>{t('Big possibilities.<br>The right next step.', '广阔可能，<br>从合适的一步开始。')}</h2>'''
        f'''</div></div>'''
        f'''{age_cards()}''',
        'tinted',
    )
    body += section(
        f'''<div class="section-head"><div>'''
        f'''{eye('Recent', '近期动态')}'''
        f'''<h2>{t('News & Updates', '新闻与动态')}</h2>'''
        f'''</div></div>'''
        f'''<div class="grid four">'''
        f'''<div class="news-cards-col grid two">{''.join(
            f'<article class="card news-item {cls}">'
            f'<h3>{t(title_en, title_zh)}</h3><p>{t(desc_en, desc_zh)}</p>'
            f'<p class="date">{t(date_en, date_zh)}</p>'
            f'</article>'
            for cls, tag_en, tag_zh, title_en, title_zh, desc_en, desc_zh, date_en, date_zh in NEWS_UPDATES
        )}</div>'''
        f'''<div class="follow-panel">'''
        f'''<h3>{t('Follow along', '关注我们')}</h3>'''
        f'''<p>{t(
            'See projects and updates on Instagram, Xiaohongshu and our WeChat Official Account.',
            '在 Instagram、小红书与微信公众号上，看看更多项目与更新。',
        )}</p>'''
        f'''<div class="footer-qr-row">'''
        f'''<div class="footer-qr"><img src="/assets/instagram-qr.webp" width="400" height="400" loading="lazy" '''
        f'''alt="{t('Instagram QR code, tinkertechworld', 'Instagram 二维码，tinkertechworld')}"><span>Instagram</span></div>'''
        f'''<div class="footer-qr"><img src="/assets/rednote-qr.webp" width="400" height="400" loading="lazy" '''
        f'''alt="{t('Xiaohongshu (Rednote) QR code, account 7436531708', '小红书二维码，小红书号 7436531708')}"><span>{t('Xiaohongshu', '小红书')}</span></div>'''
        f'''<div class="footer-qr"><img src="/assets/wechat-qr.webp" width="400" height="400" loading="lazy" '''
        f'''alt="{t('WeChat Official Account QR code', '微信公众号二维码')}"><span>{t('WeChat', '微信公众号')}</span></div>'''
        f'''</div>'''
        f'''</div>'''
        f'''</div>'''
    )
    body += section(
        f'''<div class="split"><div>'''
        f'''{eye('The TTW approach', 'TTW 学习方式')}'''
        f'''<h2>{t('The best part?<br>“I figured it out.”', '最棒的时刻？<br>“我想明白了！”')}</h2>'''
        f'''<p class="lead">{t(
            'A working robot is a beginning. Understanding why it works—and knowing what to try when it doesn’t—'
            'is where deeper learning happens.',
            '机器人动起来，只是开始。理解它为什么能工作，知道失败时该尝试什么，才是更深入的学习。',
        )}</p>'''
        f'''</div><div class="process">{process()}</div></div>''',
        'tinted',
    )
    body += section(
        f'''<div class="split"><div>'''
        f'''{eye('Make progress visible', '让进步看得见')}'''
        f'''<h2>{t('A project tells<br>a bigger story.', '每个项目背后，<br>都有成长故事。')}</h2>'''
        f'''<p class="lead">{t(
            'Look beyond the finished object. Notice the questions, tests and small improvements that show '
            'how a learner’s thinking is growing.',
            '不只看完成的作品，也关注其中的问题、测试和小小改进，理解孩子的思考如何成长。',
        )}</p>'''
        f'''{link('project-gallery.html', t('Explore project ideas →', '探索项目创意 →'), 'text-link')}'''
        f'''</div>'''
        f'''<div class="notebook">'''
        f'''{eye('Inside an engineering notebook', '工程笔记本里')}'''
        f'''<h3>{t('The questions behind the build', '作品背后的问题')}</h3>'''
        f'''<ul>'''
        f'''<li>{t('What am I trying to make?', '我想做出什么？')}</li>'''
        f'''<li>{t('What happened when I tested it?', '测试时发生了什么？')}</li>'''
        f'''<li>{t('What did I change, and why?', '我改了什么，为什么？')}</li>'''
        f'''<li>{t('How can I show it works better?', '如何证明它变得更好了？')}</li>'''
        f'''</ul>'''
        f'''<p class="line">{t('A learning approach grounded in the TTW curriculum.', '源于 TTW 课程理念的学习方式。')}</p>'''
        f'''</div></div>'''
    )
    body += section(
        f'''<div class="section-head"><div>'''
        f'''{eye('For parents', '给家长')}'''
        f'''<h2>{t('A few good questions.', '您可能想了解。')}</h2>'''
        f'''</div>{link('faq.html', t('All parent questions →', '查看全部常见问题 →'), 'text-link')}</div>'''
        f'''{faqs()}''',
        'tinted',
    ) + cta()
    render(
        'index.html',
        t('Robotics & Hands-on STEM in Markham', '万锦机器人与 STEM 实践学习'),
        t(
            'Explore TTW robotics and STEM learning pathways in Markham. Find a program by grade and request a trial class.',
            '探索 TTW 万锦机器人与 STEM 学习路径。按年级了解课程，申请体验课。',
        ),
        body,
        'home',
    )


# ============================================================
# Program detail pages
# ============================================================

PROGRAM_HIDE_STATUS_ACTIONS = {
    'lego-robotics', '3d-design-printing', 'dtf-printing', 'uv-printing', 'wro', 'distilled', 'ielts',
    'robotics-for-adults',
}


def program_page(p):
    route = 'programs/' + p['slug'] + '.html'
    wro_link = (
        f'''<a class="text-link" href="https://wro-association.org/" target="_blank" rel="noopener">'''
        f'''{t("Official WRO Association site ↗", "WRO 官方协会网站 ↗")}</a>'''
        if p['slug'] == 'wro' else ''
    )
    body = (
        f'''<div class="wrap page-hero"><div class="detail-hero"><div>'''
        f'''{eye(t(p['name']), t(p['name']))}'''
        f'''<h1>{t(p['intro'])}</h1>'''
        f'''<p class="lead">{t(p['description'])}</p>'''
        + ('' if p['slug'] in PROGRAM_HIDE_STATUS_ACTIONS else f'''<span class="status">{t(p['status'])}</span>''')
        + f'''<div class="actions">'''
        + (
            '' if p['slug'] in PROGRAM_HIDE_STATUS_ACTIONS else
            f'''{button(t('Ask about this program ↗', '咨询此课程 ↗'), 'contact-us.html?program=' + p['slug'])}'''
            f'''{link('programs/index.html', t('All programs', '全部课程'), 'text-link')}'''
        )
        + f'''{wro_link}'''
        f'''</div></div>'''
        f'''<div class="detail-art">{icon(p['icon'])}</div>'''
        f'''</div>'''
    )
    if p['slug'] == 'lego-robotics':
        body += ''.join(
            f'''<dl class="facts">'''
            f'''<div><dt>{t('Suggested learners', '建议学习阶段')}</dt><dd>{t(grade_en, grade_zh)}</dd></div>'''
            f'''<div><dt>{t('Format', '学习形式')}</dt><dd>{t('Guided, project-based learning', '指导下开展项目学习')}</dd></div>'''
            f'''<div><dt>{t('Schedule & tuition', '排期与学费')}</dt><dd>{t(tuition_en, tuition_zh)}</dd></div>'''
            f'''</dl>'''
            for grade_en, grade_zh, tuition_en, tuition_zh in [
                ('Grades 3–6', '3–6 年级', 'One class per week, 16 classes, $40/class', '每周一节课，16节课，$40每节课'),
                ('Grades 7–9', '7–9 年级', 'One class per week, 16 classes, $50/class', '每周一节课，16节课，$50每节课'),
            ]
        ) + '</div>'
    else:
        format_en, format_zh, tuition_en, tuition_zh = PROGRAM_FACTS_OVERRIDES.get(
            p['slug'],
            (
                'Guided, project-based learning', '指导下开展项目学习',
                'Confirm with TTW before enrollment', '报名前请向 TTW 确认',
            ),
        )
        body += (
            f'''<dl class="facts">'''
            f'''<div><dt>{t('Suggested learners', '建议学习阶段')}</dt><dd>{t(p['grade'])}</dd></div>'''
            f'''<div><dt>{t('Format', '学习形式')}</dt><dd>{t(format_en, format_zh)}</dd></div>'''
            f'''<div><dt>{t('Schedule & tuition', '排期与学费')}</dt><dd>{t(tuition_en, tuition_zh)}</dd></div>'''
            f'''</dl></div>'''
        )
    if p['slug'] == 'lego-robotics':
        lego_learning = [
            ('Grades 3–6', '3–6 年级',
             'A hands-on first step into robotics. Learners build sturdy LEGO structures, connect motors and '
             'sensors, and use block-based coding to bring their robot to life. Each session pairs a short '
             'building challenge with a coding lesson, so ideas keep moving from block diagram to working machine.',
             '机器人学习的动手入门课程。学生搭建稳固的 LEGO 结构，连接电机与传感器，并使用图形化编程让机器人动起来。'
             '每节课将短小的搭建挑战与编程环节结合，帮助想法从设计图逐步变成能运行的机器。',
             [
                 ('Build stable, functional structures using gears, axles and motors',
                  '使用齿轮、轴与电机搭建稳固且实用的结构'),
                 ('Use block-based coding to control movement: forward, turn, stop',
                  '使用图形化编程控制机器人前进、转向与停止'),
                 ('Read and respond to a simple sensor input, such as touch or colour',
                  '读取并响应简单传感器输入（如触碰或颜色传感器）'),
                 ('Test one change at a time and explain what happened', '每次只测试一个改动，并解释结果'),
                 ('Practise teamwork and problem-solving during a build challenge', '在搭建挑战中练习团队协作与解决问题'),
             ]),
            ('Grades 7–9', '7–9 年级',
             'Building on core construction and coding skills, learners take on more advanced control '
             'challenges—combining multiple sensors, writing longer sequences and loops, and refining a '
             'robot’s reliability through repeated testing. Sessions move from guided challenges toward '
             'more open-ended problems that reward planning and debugging.',
             '在打好搭建与编程基础后，学生将迎接更进阶的控制挑战——结合多个传感器、编写更长的顺序与循环程序，'
             '并通过反复测试提高机器人运行的可靠性。课程逐步从有引导的挑战过渡到更开放式的问题，考验规划与调试能力。',
             [
                 ('Combine multiple sensor inputs to control robot behaviour', '结合多个传感器输入，控制机器人的行为'),
                 ('Write and debug longer coding sequences, including loops and conditionals',
                  '编写并调试更长的程序，包括循环与条件判断'),
                 ('Calibrate a robot’s response for more consistent, repeatable results',
                  '校准机器人的响应，获得更一致、可重复的结果'),
                 ('Break a complex task down into smaller, testable steps', '将复杂任务拆解为可逐步测试的小步骤'),
                 ('Explain design decisions and propose improvements based on test results',
                  '解释设计决策，并根据测试结果提出改进方案'),
             ]),
        ]
        lego_projects = [
            ('Grades 3–6', '3–6 年级',
             'Build a delivery robot', '搭建运送机器人',
             'Design a robot to carry an object to a target. Compare routes, adjust the mechanism and record '
             'what improves each attempt.',
             '设计一个将物品运到目标位置的机器人。比较路线、调整机构，记录每次尝试的改进。'),
            ('Grades 7–9', '7–9 年级',
             'Program an obstacle-avoiding robot', '编写自动避障机器人程序',
             'Add a sensor to detect obstacles, then program the robot to stop, turn or reroute automatically. '
             'Test in different layouts and refine the response.',
             '为机器人加装传感器以检测障碍物，编程实现自动停止、转向或绕行，并在不同场地布局中测试与优化响应逻辑。'),
        ]
        example_block = '<div style="display:flex;flex-direction:column;gap:22px">' + ''.join(
            f'''<div class="notebook">'''
            f'''{eye('Illustrative project · Not a student result', '项目示例 · 非学生实际成果')}'''
            f'''<h3>{t(title_en, title_zh)}</h3>'''
            f'''<p>{t(desc_en, desc_zh)}</p>'''
            f'''<p class="line">{t(grade_en, grade_zh)}</p>'''
            f'''</div>'''
            for grade_en, grade_zh, title_en, title_zh, desc_en, desc_zh in lego_projects
        ) + '</div>'
    elif p['slug'] in PROGRAM_SHOWCASE_PHOTOS:
        photo, alt_en, alt_zh = PROGRAM_SHOWCASE_PHOTOS[p['slug']]
        example_block = (
            f'''<figure class="detail-photo">'''
            f'''<img src="/assets/{photo}" width="900" height="600" loading="lazy" '''
            f'''alt="{t(alt_en, alt_zh)}">'''
            f'''</figure>'''
        )
    else:
        example_block = (
            f'''<div class="notebook">'''
            f'''{eye('Illustrative project · Not a student result', '项目示例 · 非学生实际成果')}'''
            f'''<h3>{t(p['project'])}</h3>'''
            f'''<p>{t(p['challenge'])}</p>'''
            f'''<p class="line">{t('Activities depend on the learner’s level and confirmed course.', '具体活动取决于学生水平和最终确认的课程。')}</p>'''
            f'''</div>'''
        )
    if p['slug'] == 'lego-robotics':
        skills_block = ''.join(
            f'''<div style="margin-top:26px">'''
            f'''<h3>{t(grade_en, grade_zh)}</h3>'''
            f'''<p>{t(about_en, about_zh)}</p>'''
            f'''<p class="small" style="margin-top:16px;font-weight:700;text-transform:uppercase;'''
            f'''letter-spacing:.06em">{t('Learning outcomes', '学习成果')}</p>'''
            f'''<ul class="check-list">{''.join(f"<li>{t(oe, oz)}</li>" for oe, oz in outcomes)}</ul>'''
            f'''</div>'''
            for grade_en, grade_zh, about_en, about_zh, outcomes in lego_learning
        )
    elif p['slug'] in PROGRAM_LEARNING_OUTCOMES:
        about_en, about_zh, outcomes = PROGRAM_LEARNING_OUTCOMES[p['slug']]
        skills_block = (
            f'''<p>{t(about_en, about_zh)}</p>'''
            f'''<p class="small" style="margin-top:16px;font-weight:700;text-transform:uppercase;'''
            f'''letter-spacing:.06em">{t('Learning outcomes', '学习成果')}</p>'''
            f'''<ul class="check-list">{''.join(f"<li>{t(oe, oz)}</li>" for oe, oz in outcomes)}</ul>'''
        )
    else:
        skills_block = f'''<ul class="check-list">{''.join('<li>' + t(s) + '</li>' for s in p['skills'])}</ul>'''
    body += section(
        f'''<div class="split"><div>'''
        f'''{eye('What learning looks like', '学习内容')}'''
        f'''<h2>{t('Skills with a purpose.', '让技能发挥作用。')}</h2>'''
        f'''{skills_block}'''
        f'''</div>'''
        f'''{example_block}</div>''',
        'tinted',
    )
    body += section(
        f'''<div><h2>{t('A starting point that fits.', '适合自己的学习起点。')}</h2>'''
        f'''<p class="lead entry-oneline">{t(p['entry'])}</p></div>'''
    )
    if p['slug'] == 'wro':
        wro_season_steps = [
            ('Learn the category', '了解比赛类别',
             'Study the official rules for RoboMission, Future Engineers or Future Innovators, including the '
             'judging focus and equipment allowed.',
             '研读 RoboMission、Future Engineers 或 Future Innovators 的官方规则，了解评分重点及允许使用的设备。'),
            ('Build & test', '搭建与测试',
             'Design and build a robot or project for the challenge, then test it repeatedly, refining it based '
             'on what each run reveals.',
             '针对挑战任务设计并搭建机器人或项目，反复测试，并根据每次演练结果不断改进。'),
            ('Local & national tournaments', '地区与全国赛',
             'Teams register and compete through their country’s WRO National Organizer at qualifying '
             'tournaments; local rules can vary by country.',
             '队伍通过所在国家的 WRO 国家组织方注册并参加地区、全国资格赛；各地具体规则可能有所不同。'),
            ('International Final', '国际总决赛',
             'Top-performing teams from national tournaments can advance to the WRO International Final.',
             '全国赛中表现优异的队伍有机会晋级 WRO 国际总决赛。'),
        ]
        body += section(
            f'''<div class="section-head"><div>'''
            f'''{eye('The season', '赛季流程')}'''
            f'''<h2>{t('How WRO works', 'WRO 赛事如何进行')}</h2>'''
            f'''</div></div>'''
            f'''<div class="process">{''.join(
                f'<div class="process-item"><div><h3>{t(en, zh)}</h3><p>{t(desc, zd)}</p></div></div>'
                for en, zh, desc, zd in wro_season_steps
            )}</div>''',
            'tinted',
        )
        body += section(
            f'''<div class="callout">{t(
                'Categories, age ranges and formats are set by the World Robot Olympiad Association and can '
                'change by season. TTW will need to confirm the current format, local eligibility and coaching '
                'capacity before offering a team place.',
                '类别、年龄范围和赛制由 World Robot Olympiad Association 制定，并可能随赛季调整。'
                'TTW 需确认当前形式、本地参赛资格及教练安排后，才能提供战队席位。',
            )} <a href="https://wro-association.org/">{t('Check the official WRO Association information →', '查看 WRO 官方信息 →')}</a></div>'''
            f'''<p class="small">{t(
                'Official overview checked September 16, 2026. World Robot Olympiad and WRO are trademarks of '
                'their respective owner; this page does not claim TTW affiliation, endorsement or team registration.',
                '官方概览核对日期：2026 年 9 月 16 日。World Robot Olympiad 及 WRO 为其权利人的商标；'
                '本页不表示 TTW 已获其认可、授权或完成战队注册。',
            )}</p>'''
        )
    body += cta()
    render(route, t(p['name']), t(p['description']), body, 'wro' if p['slug'] == 'wro' else 'programs')


# ============================================================
# Age-group pages
# ============================================================

def age_page(a):
    items = [p for p in DATA['programs'] if p['slug'] in a['programs']]
    body = heading(t(a['name']) + '<br>' + t(a['verb']), t(a['description']))
    body += section(
        f'''<div class="split">'''
        f'''<div><h2>{t('The growth to look for.', '值得关注的成长。')}</h2>'''
        f'''<p class="lead">{t(a['focus'])}</p></div>'''
        f'''<div class="card">'''
        f'''<h3>{t('Grade is a guide, not a placement test.', '年级是参考，能力才是起点。')}</h3>'''
        f'''<p>{t(
            'Share interests and prior experience. The right starting point depends on what the learner '
            'can already do and explain.',
            '请分享兴趣与过往经验。合适的起点取决于学生已经能做什么、能解释什么。',
        )}</p>'''
        f'''{button(t('Discuss a starting point', '咨询学习起点'), 'contact-us.html?grade=' + a['slug'])}'''
        f'''</div></div>''',
        'tinted',
    )
    body += section(
        f'''<div class="section-head"><h2>{t("Explore relevant pathways", "探索相关学习方向")}</h2></div>'''
        + program_cards(items)
    ) + cta()
    render('age-groups/' + a['slug'] + '.html', t(a['name']), t(a['description']), body, 'ages')


def process():
    steps = [
        ('Imagine & build', '构思与搭建',
         'Start with a question. Make a plan, try an idea and connect it to something tangible.',
         '从问题开始，制定计划，尝试想法，把它变成摸得到的作品。'),
        ('Test & improve', '测试与改进',
         'Notice what works, investigate what doesn’t, and make a thoughtful change.',
         '观察成功之处，探究失败原因，并有依据地改进。'),
        ('Explain & connect', '解释与连接',
         'Share the reasoning behind the project and carry those skills into the next challenge.',
         '分享项目背后的思考，将技能带入下一个挑战。'),
    ]
    return ''.join(
        f'<div class="process-item"><div><h3>{t(en, zh)}</h3><p>{t(desc, zd)}</p></div></div>'
        for en, zh, desc, zd in steps
    )


# ============================================================
# Trial / join inquiry builder
# ============================================================

def booking():
    title = t('Contact Us', '联系我们')

    def options(rows):
        opts = '<option value="">' + t('Please select', '请选择') + '</option>'
        opts += ''.join('<option value="' + x['slug'] + '">' + t(x['name']) + '</option>' for x in rows)
        return opts

    def field(id, label, kind='text', req=False):
        return (
            f'''<div class="field"><label for="{id}">{label}'''
            f'''{t(" (required)", "（必填）") if req else t(" (optional)", "（选填）")}</label>'''
            f'''<input id="{id}" name="{id}" type="{kind}" maxlength="{100 if id == "name" else 150}" '''
            f'''{"required" if req else ""} autocomplete="{id if id in ["name", "email"] else "off"}"></div>'''
        )

    body = heading(
        title,
        t(
            'Let’s find a starting point that feels right. Tell us a little about the learner and the program you’re interested in.',
            '一起寻找合适的学习起点。请介绍学生的情况和感兴趣的课程。',
        ),
        ['Your next step', '下一步'],
    )

    form_intro = (
        f'''<div class="form-layout"><div class="form-card">'''
        f'''<noscript><div class="callout">{t(
            'The request builder needs JavaScript. Please email your grade group, interests and preferred timing to',
            '申请生成器需要 JavaScript。请将年级、兴趣及希望的时间发送至',
        )} <a href="mailto:{DATA['email']}">{DATA['email']}</a>.</div></noscript>'''
        f'''<form id="inquiry-form" data-email="{DATA['email']}" hidden>'''
        f'''<h2 style="font-size:1.6rem">{t('Tell us about your learner', '介绍一下学习者')}</h2>'''
        f'''<p class="form-help">{t(
            'For a child, please use a parent or guardian’s contact details. No child’s full name is needed.',
            '如果为孩子咨询，请填写家长或监护人的联系方式，无需填写孩子全名。',
        )}</p>'''
    )

    name_email_fields = (
        f'''<div class="field-grid">'''
        f'''{field('name', t('Parent / adult learner name', '家长 / 成人学习者姓名'), req=True)}'''
        f'''{field('email', t('Contact email', '联系邮箱'), 'email', True)}'''
        f'''</div>'''
    )

    grade_program_fields = (
        f'''<div class="field-grid">'''
        f'''<div class="field"><label for="grade">{t('Grade group (required)', '年级分组（必填）')}</label>'''
        f'''<select name="grade" id="grade" required>{options(DATA['ages'])}</select></div>'''
        f'''<div class="field"><label for="program">{t('Program interest (required)', '课程兴趣（必填）')}</label>'''
        f'''<select name="program" id="program" required>'''
        f'''{options(DATA['programs'])}'''
        f'''<option value="fll">FIRST LEGO League</option>'''
        f'''<option value="camps">{t('Camps', '营地')}</option>'''
        f'''<option value="not-sure">{t('Help me choose', '请帮我选课')}</option>'''
        f'''</select></div>'''
        f'''</div>'''
    )

    timing_field = (
        f'''<div class="field"><label for="timing">{t('Preferred days / times (optional)', '希望的日期 / 时间（选填）')}</label>'''
        f'''<input name="timing" id="timing" maxlength="150" placeholder="{t('e.g. Saturday mornings', '例如：周六上午')}">'''
        f'''<p class="form-help">{t(
            'A preference, not an available time slot. TTW will confirm availability.',
            '这是时间偏好，并非可预约时段。TTW 将确认具体安排。',
        )}</p></div>'''
    )

    source_options = [
        ('search', 'Search engine', '搜索引擎'),
        ('friend', 'Friend / family', '朋友 / 家人'),
        ('school', 'School / community', '学校 / 社区'),
        ('social', 'Social media', '社交媒体'),
        ('other', 'Other', '其他'),
    ]
    area_source_fields = (
        f'''<div class="field-grid">'''
        f'''<div class="field"><label for="area">{t('Postal area (optional)', '邮编区域（选填）')}</label>'''
        f'''<input id="area" name="area" maxlength="3" pattern="[A-Za-z][0-9][A-Za-z]" placeholder="L3R" '''
        f'''aria-describedby="area-help">'''
        f'''<p class="form-help" id="area-help">{t('First 3 characters only. Helps us understand travel needs.', '仅前三位，帮助了解通勤需求。')}</p>'''
        f'''</div>'''
        f'''<div class="field"><label for="source">{t('How did you hear about us? (optional)', '从哪里了解到我们？（选填）')}</label>'''
        f'''<select id="source" name="source"><option value="">{t('Please select', '请选择')}</option>'''
        f'''{''.join(f'<option value="{v}">{t(en, zh)}</option>' for v, en, zh in source_options)}'''
        f'''</select></div>'''
        f'''</div>'''
    )

    notes_consent = (
        f'''<div class="field"><label for="notes">{t('Interests, experience or questions (optional)', '兴趣、经验或问题（选填）')}</label>'''
        f'''<textarea id="notes" name="notes" maxlength="700" aria-describedby="notes-help"></textarea>'''
        f'''<p id="notes-help" class="form-help">{t('Please leave out medical details and other sensitive information.', '请勿填写医疗信息或其他敏感资料。')}</p>'''
        f'''</div>'''
        f'''<label class="checkbox"><input type="checkbox" name="consent" id="consent" required>'''
        f'''<span>{t(
            'I am an adult learner or a parent/guardian. I agree to share this inquiry with TTW for a reply.',
            '我是成人学习者或家长 / 监护人，同意向 TTW 分享此咨询，以便获得回复。',
        )} {link('privacy.html', t('Privacy details', '隐私说明'))}</span></label>'''
        f'''<button class="button primary" type="submit">{t('Review my request →', '核对我的申请 →')}</button>'''
        f'''<p class="form-help">{t(
            'Nothing is sent by this button. You’ll review your message, then send it using your email app.',
            '点击此按钮不会发送资料。您将先核对内容，再通过邮件应用发送。',
        )}</p>'''
        f'''</form>'''
    )

    review_section = (
        f'''<section id="review" class="review" hidden tabindex="-1" aria-labelledby="review-title">'''
        f'''<h2 id="review-title" style="font-size:1.5rem">{t('Review, then send', '核对后发送')}</h2>'''
        f'''<p>{t(
            'Your request has not been sent. Open your email app and send the message to TTW. '
            'A place is only booked after TTW confirms it with you.',
            '您的申请尚未发送。请打开邮件应用并将信息发送至 TTW。只有收到 TTW 确认后，预约才成立。',
        )}</p>'''
        f'''<label for="request-preview" class="small">{t('Your message', '您的消息')}</label>'''
        f'''<textarea id="request-preview" readonly></textarea>'''
        f'''<div class="actions">'''
        f'''<a id="send-email" class="button primary" href="mailto:{DATA['email']}">{t('Open email to send ↗', '打开邮件发送 ↗')}</a>'''
        f'''<button type="button" class="button outline" id="copy-request">{t('Copy message', '复制消息')}</button>'''
        f'''</div>'''
        f'''<a id="download-request" class="text-link" download="TTW-inquiry.txt">{t('Download your request', '下载申请内容')}</a>'''
        f'''<p class="form-help">{t(
            'No email app? Copy the message into your webmail and send it to',
            '没有邮件应用？请将消息复制到网页邮箱并发送至',
        )} <a href="mailto:{DATA['email']}">{DATA['email']}</a>.</p>'''
        f'''<p id="form-status" class="form-status" role="status"></p>'''
        f'''</section></div>'''
    )

    process_steps = [
        ('Share an interest', '分享兴趣',
         'Tell us what the learner enjoys and what they have tried.', '告诉我们学习者喜欢什么、尝试过什么。'),
        ('Discuss the fit', '讨论适合的起点',
         'TTW can clarify the starting level, timing, location and any fees.', 'TTW 将沟通起点、时间、地点和相关费用。'),
        ('Confirm together', '共同确认',
         'A trial or enrollment is confirmed directly with TTW. No payment is collected here.',
         '体验课或报名需与 TTW 直接确认。本页面不收取任何费用。'),
    ]
    aside = (
        f'''<aside><div class="process">{''.join(
            '<div class="process-item"><div><h3>' + t(e, z) + '</h3><p>' + t(d, zd) + '</p></div></div>'
            for e, z, d, zd in process_steps
        )}</div>'''
        f'''<div class="callout">{t(
            'Some pathways are still in development. An interest request does not mean a course or team is currently open.',
            '部分方向仍在开发中。登记意向不代表相关课程或战队已经开放。',
        )}</div>'''
        f'''<h3>{t('Prefer a direct conversation?', '想直接联系？')}</h3>'''
        f'''<a class="text-link" href="mailto:{DATA['email']}">{DATA['email']}</a>'''
        f'''</aside></div>'''
    )

    body += section(
        form_intro + name_email_fields + grade_program_fields + timing_field
        + area_source_fields + notes_consent + review_section + aside
    )
    render(
        'contact-us.html',
        title,
        t(
            'Request a TTW trial or program conversation. Review your inquiry and email the team to confirm availability.',
            '申请 TTW 体验课或课程咨询。核对信息并通过邮件联系团队确认安排。',
        ),
        body,
    )


# ============================================================
# Schedule page: calendar-grid view (below the existing table)
# One pixel per minute, so px offsets can be computed directly
# from "HH:MM – HH:MM" time-range strings.
# ============================================================

def _schedule_time_range(slot):
    start_s, end_s = (part.strip() for part in slot.split('–'))
    start_h, start_m = (int(part) for part in start_s.split(':'))
    end_h, end_m = (int(part) for part in end_s.split(':'))
    return start_h * 60 + start_m, end_h * 60 + end_m, start_s, end_s


def schedule_calendar(rows, days, day_indices, range_start_h, range_end_h, title_en, title_zh):
    range_start = range_start_h * 60
    total = (range_end_h - range_start_h) * 60
    body_height = total + 22  # room for the last hour label to sit below its line
    hour_labels = ''.join(
        f'''<div class="cal-hour" style="top:{h * 60 - range_start}px">{h:02d}:00</div>'''
        for h in range(range_start_h, range_end_h + 1)
    )
    day_heads = ''
    day_bodies = ''
    for day_idx in day_indices:
        day_en, day_zh = days[day_idx]
        events = ''
        for prog_en, prog_zh, color, slots in rows:
            slot = slots[day_idx]
            if not slot:
                continue
            start_m, end_m, start_s, end_s = _schedule_time_range(slot)
            events += (
                f'''<div class="cal-event slot-{color}" '''
                f'''style="top:{start_m - range_start}px;height:{end_m - start_m}px">'''
                f'''<span class="cal-event-title">{t(prog_en, prog_zh)}</span>'''
                f'''<span class="cal-event-time">{start_s}–{end_s}</span>'''
                f'''</div>'''
            )
        day_heads += f'''<div class="cal-day-head">{t(day_en, day_zh)}</div>'''
        day_bodies += f'''<div class="cal-day-body" style="height:{body_height}px">{events}</div>'''
    cols = len(day_indices)
    return (
        f'''<div class="cal-block">'''
        f'''{eye(title_en, title_zh)}'''
        f'''<div class="cal-scroll"><div class="cal-grid" style="grid-template-columns:64px repeat({cols},minmax(120px,1fr))">'''
        f'''<div class="cal-corner"></div>{day_heads}'''
        f'''<div class="cal-axis" style="height:{body_height}px">{hour_labels}</div>{day_bodies}'''
        f'''</div></div></div>'''
    )


# ============================================================
# Remaining static pages (Programs/Age Groups index, FLL, Camps,
# Membership, Gallery, About, Learning Approach, Competitions,
# FAQ, Contact, Privacy, legacy store redirect target, 404)
# ============================================================

def other_pages():
    body = heading(
        t('Find what sparks<br>their curiosity.', '找到点燃<br>好奇心的方向。'),
        t(
            'Connected areas of learning. Start with the core robotics pathway and explore future directions as skills grow.',
            '相互连接的学习领域。从核心机器人路径开始，随着技能成长，探索未来方向。',
        ),
        ['Programs', '课程'],
    )
    programs_by_slug = {p['slug']: p for p in DATA['programs']}
    programs_grid = '<div class="grid program-grid">' + ''.join([
        program_card_html(programs_by_slug['lego-robotics']),
        program_card_html(programs_by_slug['wro']),
        fll_card(),
        program_card_html(programs_by_slug['distilled']),
        program_card_html(programs_by_slug['robotics-for-adults']),
        program_card_html(programs_by_slug['ielts']),
        program_card_html(programs_by_slug['3d-design-printing']),
        program_card_html(programs_by_slug['dtf-printing']),
        program_card_html(programs_by_slug['uv-printing']),
    ]) + '</div>'
    body += section(programs_grid) + section(
        '<h2>' + t('Not sure where to start?', '不确定从哪里开始？') + '</h2>'
        '<p class="lead">' + t(
            'Grade groups help you explore. Experience and interests help us choose a starting point together.',
            '年级分组帮助探索方向，经验与兴趣帮助我们一起确定起点。',
        ) + '</p>' + age_cards(),
        'tinted',
    ) + cta()
    render(
        'programs/index.html', t('Programs', '课程'),
        t(
            'Explore LEGO robotics, 3D design and printing, and the Distilled pathway at TTW.',
            '探索 TTW 的 LEGO 机器人、3D 设计与打印，以及 Distilled 学习路径。',
        ),
        body, 'programs',
    )

    ages_body = heading(
        t('Room to grow.<br>At every stage.', '每个阶段，<br>都有成长空间。'),
        t(
            'A clear starting point today, with a view of what could come next. Read each pathway’s availability before making plans.',
            '了解今天的起点，也看见未来的方向。做计划前，请阅读各路径的开放情况。',
        ),
    ) + section(age_cards(), 'tinted') + cta()
    render(
        'age-groups/index.html', t('Age Groups', '年龄分组'),
        t(
            'Find a TTW learning pathway for Grades 3–6, Grades 7–9, high school or adults.',
            '了解适合 3–6 年级、7–9 年级、高中及成人的 TTW 学习路径。',
        ),
        ages_body, 'ages',
    )

    schedule_days = [
        ('Monday', '周一'), ('Tuesday', '周二'), ('Wednesday', '周三'), ('Thursday', '周四'),
        ('Friday', '周五'), ('Saturday', '周六'), ('Sunday', '周日'),
    ]
    schedule_rows = [
        ('LEGO Robotics · Grades 3–6', 'LEGO 机器人 · 3–6 年级', 'blue',
         ['', '17:00 – 18:30', '', '17:00 – 18:30', '', '', '']),
        ('LEGO Robotics · Grades 7–9', 'LEGO 机器人 · 7–9 年级', 'blue2',
         ['17:00 – 18:30', '', '17:00 – 18:30', '', '', '', '']),
        ('Distilled Series', 'Distilled 系列', 'green',
         ['', '', '', '', '17:00 – 18:30', '', '']),
        ('3D Design & Printing', '3D 设计与打印', 'orange',
         ['', '', '', '', '19:00 – 20:30', '', '']),
        ('DTF Printing', 'DTF 转印', 'orange2',
         ['', '', '', '', '', '13:00 – 14:30', '10:00 – 11:00']),
        ('UV Printing', 'UV 打印', 'orange3',
         ['', '', '', '', '', '14:30 – 16:00', '11:00 – 12:00']),
        ('FIRST LEGO League Prep', 'FIRST LEGO League 备赛', 'red',
         ['', '19:00 – 20:30', '19:00 – 20:30', '', '', '', '']),
        ('World Robot Olympiad Prep', 'World Robot Olympiad 备赛', 'red2',
         ['19:00 – 20:30', '', '', '19:00 – 20:30', '', '', '']),
        ('Robotics for Adults', '成人机器人', 'blue3',
         ['', '', '', '', '', '11:30 – 13:00', '13:00 – 14:30']),
        ('IELTS Preparation', '雅思备考', 'green2',
         ['', '', '', '', '', '10:00 – 11:30', '15:00 – 16:30']),
    ]
    schedule = heading(
        t('Weekly Schedule.', '周课表。'),
        '',
        ['Schedule', '课程安排'],
    )
    schedule += section(
        f'''<div class="schedule-table-wrap"><table class="schedule-table">'''
        f'''<thead><tr><th scope="col"></th>{''.join(
            f'<th scope="col">{t(d_en, d_zh)}</th>' for d_en, d_zh in schedule_days
        )}</tr></thead>'''
        f'''<tbody>{''.join(
            f'<tr><th scope="row" class="slot-{color}">{t(prog_en, prog_zh)}</th>'
            + ''.join(f'<td class="slot-{color}">{slot}</td>' if slot else '<td></td>' for slot in slots)
            + '</tr>'
            for prog_en, prog_zh, color, slots in schedule_rows
        )}</tbody></table></div>''',
        'tinted',
    ) + section(
        schedule_calendar(
            schedule_rows, schedule_days, range(0, 5), 16, 21,
            'Weekday view · Mon–Fri, 16:00–21:00', '工作日视图 · 周一至周五，16:00–21:00',
        ) + schedule_calendar(
            schedule_rows, schedule_days, range(5, 7), 10, 21,
            'Weekend view · Sat–Sun, 10:00–21:00', '周末视图 · 周六、周日，10:00–21:00',
        ),
        'tinted',
    ) + cta()
    render(
        'schedule.html', t('Schedule', '课程安排'),
        t(
            'A sample weekly class schedule for TTW programs in Markham. Illustrative only; confirm actual days and times with TTW.',
            'TTW 万锦课程的示例周课表，仅供参考；实际日期与时间请向 TTW 确认。',
        ),
        schedule, 'schedule',
    )

    fll = heading(
        'FIRST LEGO League',
        t(
            'A team challenge that brings building, coding and problem solving together. '
            'Ask TTW about readiness and potential team opportunities.',
            '将搭建、编程和解决问题结合在一起的团队挑战。欢迎向 TTW 咨询能力准备及潜在战队机会。',
        ),
        ['Explore team learning', '探索团队学习'],
    )
    fll += section(
        f'''<div class="split">'''
        f'''<div><h2>{t('Build skills.<br>Learn as a team.', '积累技能，<br>学习团队协作。')}</h2>'''
        f'''<ul class="check-list">'''
        f'''<li>{t('Explore a problem and develop ideas together.', '共同探索问题，发展解决思路。')}</li>'''
        f'''<li>{t('Build, code and test a robot through repeated attempts.', '通过反复尝试搭建、编程和测试机器人。')}</li>'''
        f'''<li>{t('Explain decisions and listen to other perspectives.', '解释自己的决策，倾听不同观点。')}</li>'''
        f'''</ul></div>'''
        f'''<div class="card">'''
        f'''<span class="status">{t('TTW team availability not yet confirmed', 'TTW 战队开放情况尚未确认')}</span>'''
        f'''<h3>{t('Interested in a team?', '对战队感兴趣？')}</h3>'''
        f'''<p>{t(
            'A consultation will clarify experience, grade, family time commitment and any future group options. '
            'Team registration, event entry and fees are not currently offered through this website.',
            '咨询将帮助明确经验、年级、家庭时间投入及未来班组选择。本网站目前不提供战队注册、赛事报名或收费。',
        )}</p>'''
        f'''{button(t('Ask about FIRST LEGO League', '咨询 FIRST LEGO League'), 'contact-us.html?program=fll')}'''
        f'''</div></div>'''
        f'''<div class="callout">{t(
            'Season formats and regional availability can change. TTW will need to confirm the current format, '
            'local eligibility and coaching capacity before offering a team place.',
            '赛季形式和地区安排可能变化。TTW 需确认当前形式、本地参赛资格及教练安排后，才能提供战队席位。',
        )} <a href="https://www.firstinspires.org/programs/fll/">{t('Check the official FIRST program information →', '查看 FIRST 官方项目信息 →')}</a></div>'''
        f'''<p class="small">{t(
            'Official overview checked September 17, 2026. FIRST and LEGO are trademarks of their respective owners; '
            'this page does not claim TTW affiliation, endorsement or team registration.',
            '官方概览核对日期：2026 年 9 月 17 日。FIRST 和 LEGO 为各自权利人的商标；本页不表示 TTW 已获其认可、授权或完成战队注册。',
        )}</p>''',
        'tinted',
    ) + cta()
    render(
        'first-lego-league.html', 'FIRST LEGO League',
        t(
            'Explore FIRST LEGO League interests at TTW. Ask about preparation and possible team opportunities; availability must be confirmed.',
            '了解 TTW 的 FIRST LEGO League 咨询方向。咨询能力准备及潜在战队机会，具体安排需确认。',
        ),
        fll, 'fll',
    )

    camp_ideas = [
        ('Summer discovery', '暑期探索',
         'Project ideas that connect robotics, design and making.', '将机器人、设计与创作联系起来的项目创意。'),
        ('School-break making', '学校假期创作',
         'Explore interest in winter and March Break activities.', '了解寒假及春假活动意向。'),
        ('PA Day possibilities', 'PA Day 活动',
         'A chance to try a focused hands-on challenge.', '尝试专注的动手挑战。'),
    ]
    camps = heading(
        t('School breaks.<br>Fresh discoveries.', '学校假期，<br>探索新发现。'),
        t(
            'Interested in a hands-on break from the usual routine? Tell us which school holiday works for your family.',
            '希望假期里有不一样的动手体验？告诉我们适合您家庭的学校假期。',
        ),
        ['Camps · Future dates', '营地 · 排期待定'],
    )
    camps += section(
        '<div class="grid three">' + ''.join(
            f'<article class="card"><h3>{t(e, z)}</h3><p>{t(d, zd)}</p>'
            f'<span class="status">{t("Dates & fees to be confirmed", "日期与费用待确认")}</span></article>'
            for e, z, d, zd in camp_ideas
        ) + '</div>'
        + '<div class="callout">' + t(
            'Camp registration is not open. Dates, age groups, hours, location, supervision, fees and '
            'policies must be confirmed before any booking.',
            '营地报名尚未开放。任何预约前，需确认日期、年龄、时间、地点、指导安排、费用及政策。',
        ) + '</div>'
        + button(t('Ask about future camps', '咨询未来营地'), 'contact-us.html?program=camps'),
        'tinted',
    ) + cta()
    render(
        'camps.html', t('Camps', '营地'),
        t(
            'Register interest in future TTW STEM camps in Markham. School-break dates, fees and availability are to be confirmed.',
            '登记 TTW 万锦未来 STEM 营地意向。学校假期日期、费用及开班情况待确认。',
        ),
        camps, 'camps',
    )

    membership_benefits = [
        ('Priority course booking — new trial times and course openings before they’re released to the public.',
         '优先定课——新开放的体验课和课程名额，早于公开发布。'),
        ('Bigger member discounts on course tuition, above the general public rate.',
         '课程学费享受更大力度的会员折扣，优于公开价格。'),
        ('Free priority access to Makerspace equipment and workspace, with no usage fee '
         '(reasonable materials costs may apply).',
         '免费优先预约使用创客空间设备与工作区，不收取使用费用（适当耗材费用）。'),
        ('Free access to regular expert talks.',
         '免费参加定期的专家讲座。'),
    ]
    makerspace_equipment = [
        ('AI workstation', 'AI 工作站'),
        ('High-performance computers', '高性能电脑'),
        ('Group workspace', '团体工作区'),
        ('DTF printer and tools', 'DTF 转印机及工具'),
        ('UV printer and tools', 'UV 打印机及工具'),
        ('3D printers', '3D 打印机'),
    ]
    makerspace_notes = [
        ('Other basic tools don’t need a booking (for example: hand/mechanical tools, oscilloscopes, '
         'signal generators and multimeters).',
         '其他基本的工具不需要预约（如：机械工具、示波器、信号发生器、万用表等）。'),
        ('If the total number of people would exceed Makerspace capacity, advance booking is required.',
         '如总人数超过 Makerspace 可容纳的人数，需要提前预约。'),
    ]
    membership = heading(
        t('One membership.<br>Every step forward.', '一个会员身份，<br>陪伴每一步成长。'),
        t(
            'TTW membership is built around priority course booking, bigger discounts, free priority access '
            'to Makerspace equipment and regular expert talks.',
            'TTW 会员围绕优先定课、更大的折扣、免费优先使用创客空间设备，以及定期专家讲座设计。',
        ),
        ['Membership', '会员'],
    )
    membership += section(
        f'''<div class="split"><div>'''
        f'''{eye('Member benefits', '会员权益')}'''
        f'''<h2>{t('Member benefits.', '会员权益。')}</h2>'''
        f'''<ul class="check-list">{''.join(f'<li>{t(en, zh)}</li>' for en, zh in membership_benefits)}</ul>'''
        f'''<p class="small" style="margin-top:16px;font-weight:700;text-transform:uppercase;'''
        f'''letter-spacing:.06em">{t('Membership price: $50/month', '会员价格：$50每月')}</p>'''
        f'''<p class="small">{t(
            '* Completing a course booking comes with one month of membership free; the learner decides when to start using it.',
            '*完成定课免费送一个月会员，学员自行决定开始使用时间。',
        )}</p>'''
        f'''</div>'''
        f'''<div class="notebook">'''
        f'''{eye('Inside the Makerspace', '创客空间设备')}'''
        f'''<h3>{t('Equipment members can book', '会员可预约的设备')}</h3>'''
        f'''<ul>{''.join(f'<li>{t(en, zh)}</li>' for en, zh in makerspace_equipment)}</ul>'''
        f'''<ul class="notes">{''.join(f'<li>{t(en, zh)}</li>' for en, zh in makerspace_notes)}</ul>'''
        f'''<p class="line">{t(
            'Children under 12 must be accompanied by an adult when using the equipment above. '
            'The accompanying adult does not need to pay any extra fee.',
            '12 岁以下孩子使用以上设备需要成人陪同。陪同的成人不需要支付额外费用。',
        )}</p>'''
        f'''<p class="line">{t(
            'Using the DTF and UV printing equipment requires completing safety training and the related course first.',
            '使用 DTF 和 UV 打印设备需完成安全和相关的课程。',
        )}</p>'''
        f'''</div></div>''',
        'tinted',
    )
    membership += cta()
    render(
        'membership.html', t('Membership', '会员'),
        t(
            'Explore what a future TTW membership could include and register interest. Structure and launch date are not yet confirmed.',
            '了解未来 TTW 会员可能包含的权益并登记意向。具体结构及上线时间尚未确认。',
        ),
        membership,
    )

    booking_options = [
        ('Private lessons', '私教课程',
         'One-on-one or small-group sessions scheduled around your learner’s pace.',
         '一对一或小组课程，按孩子的节奏安排。'),
        ('Consultation', '咨询预约',
         'Talk through goals, fit and the right starting point with TTW.',
         '与 TTW 沟通学习目标、匹配度及合适的学习起点。'),
        ('Equipment time', '设备时段',
         'Reserve Makerspace equipment time as a member.',
         '作为会员预约创客空间设备时段。'),
    ]
    booking = heading(
        t('Member booking.<br>Coming soon.', '会员预约，<br>即将上线。'),
        t(
            'Book private lessons, a consultation or Makerspace equipment time as a TTW member. '
            'This online booking portal is still being built.',
            '作为 TTW 会员，预约私教课程、咨询或创客空间设备时段。该在线预约功能仍在开发中。',
        ),
        ['Member booking · Not yet available', '会员预约 · 尚未开放'],
    )
    booking += section(
        '<div class="grid three">' + ''.join(
            f'<article class="card"><h3>{t(en, zh)}</h3><p>{t(d, zd)}</p>'
            f'<span class="status">{t("Coming soon", "即将上线")}</span></article>'
            for en, zh, d, zd in booking_options
        ) + '</div>'
        + '<div class="callout">' + t(
            'Member booking is not yet available online. TTW is building this booking portal—in the '
            'meantime, contact TTW directly to arrange a private lesson, consultation or equipment time.',
            '会员预约功能尚未上线。TTW 正在开发该预约系统——在此之前，请直接联系 TTW 安排私教课程、咨询或设备时段。',
        ) + '</div>',
        'tinted',
    ) + cta()
    render(
        'booking.html', t('Member Booking', '会员预约'),
        t(
            'Register interest in TTW member booking for private lessons, consultations and Makerspace equipment time. Not yet available online.',
            '登记 TTW 会员预约意向，涵盖私教课程、咨询及创客空间设备时段。该功能尚未上线。',
        ),
        booking,
    )

    gallery = heading(
        t('Ideas worth<br>getting your hands into.', '值得亲手<br>探索的创意。'),
        t(
            'Explore the kinds of challenges in TTW’s learning plans. These are illustrative project ideas, not completed student work.',
            '探索 TTW 学习规划中的挑战类型。以下为项目示例，不是已完成的学生作品。',
        ),
        ['Project gallery', '项目展示'],
    )
    gallery_cards = ''.join(
        f'''<article class="card {p["color"]}">'''
        f'''<div class="card-visual">{icon(p["icon"])}</div>'''
        f'''<span class="status">{t("Illustrative project", "项目示例")}</span>'''
        f'''<h3>{t(p["project"])}</h3><p>{t(p["challenge"])}</p>'''
        f'''</article>'''
        for p in DATA['programs']
    )
    gallery += section(
        '<div class="grid three">' + gallery_cards + '</div>'
        '<div class="empty">'
        '<h3>' + t('Student stories will come with real evidence.', '用真实记录呈现学生故事。') + '</h3>'
        '<p>' + t(
            'Future student showcases will explain the challenge, process and learning, and will only be '
            'shared with appropriate permission.',
            '未来学生展示将呈现挑战、过程和学习收获，并在获得相应许可后分享。',
        ) + '</p></div>'
    ) + cta()
    render(
        'project-gallery.html', t('Project Gallery', '项目展示'),
        t(
            'Explore illustrative TTW project ideas connecting robotics, design and engineering exploration.',
            '探索连接机器人、设计与工程探索的 TTW 项目示例。',
        ),
        gallery,
    )

    about = heading(
        t('Curious minds.<br>Capable makers.', '好奇的头脑，<br>有能力的创客。'),
        t(
            'Tinker Tech World is built around a simple idea: learners understand technology more deeply when '
            'they use it to make, test and improve something of their own.',
            'Tinker Tech World 源于一个简单理念：当学习者用技术制作、测试并改进自己的作品时，便能更深入地理解技术。',
        ),
        ['About TTW', '关于 TTW'],
        desc_cls='lead entry-oneline',
    )
    values = [
        ('Tinker', 'var(--orange)', 'Hands-on practice, explore the unknown.', '动手实践，探索未知。'),
        ('Tech', 'var(--blue)', 'Master technology, change the future.', '掌握技术，改变未来。'),
        ('World', 'var(--green)', 'Embrace the world, connect the future.', '面向世界，连接未来。'),
    ]
    about += section(
        '<div class="grid three">' + ''.join(
            f'<article class="card"><h3 style="color:{c}">{e}</h3><p>{t(d, z)}</p></article>' for e, c, d, z in values
        ) + '</div>',
        'tinted',
    )
    program_leads = [
        ('Rice Rao', 'FLL and WRO Program Leader', 'FLL 与 WRO 项目负责人', 'rice-rao.webp', [
            ('M.Sc., Electrical & Computer Engineering, University of Alberta', '阿尔伯塔大学电子与计算机工程硕士'),
            ('B.Sc. Mathematics, Peking University', '北京大学数学学士'),
            ('Head Coach and Founder, <a href="https://www.explorer-robotics.com" target="_blank" '
             'rel="noopener">Explorer Robotics</a>',
             '<a href="https://www.explorer-robotics.com" target="_blank" rel="noopener">Explorer Robotics</a> '
             '创始人兼主教练'),
            ('Led teams in winning multiple national and international robotics awards', '带队多次获得国家级与国际级机器人赛事奖项'),
            ('Over 20 years of IT industry experience as a software engineer working internationally',
             '拥有20余年国际软件工程行业经验'),
        ]),
        ('Lisa Li', 'Language Program Leader', '语言课程负责人', 'lisa-li.webp', [
            ('Master of Education, the University of British Columbia', '英属哥伦比亚大学英语教育学硕士'),
            ('Former New Oriental 20th Anniversary Distinguished Teacher; Group Teaching Trainer',
             '原新东方二十周年功勋教师，集团教学培训师'),
            ('Over 20 years of experience teaching IELTS, TOEFL, GRE and GMAT', '拥有20余年 IELTS、TOEFL、GRE 及 GMAT 教学经验'),
            ('Over 10,000 hours of teaching, nearly 100,000 students across many countries worldwide, '
             'highly rated by students',
             '授课时长超过10000小时，总学员人数近10万人，遍布全球很多国家，深受学员好评'),
        ]),
        ('Kevin Wang', 'Adult Robotics Program Leader', '成人机器人课程负责人', '', [
            ('M.A.Sc, Electrical and Computer Engineering, University of Toronto', '多伦多大学电子与计算机工程应用科学硕士'),
            ('Former Chief Engineer at ESI Robotics Company', '曾任 ESI Robotics 公司首席工程师'),
            ('Over 30 years of experience in the robotics industry', '拥有30余年机器人行业经验'),
        ]),
    ]
    about += section(
        f'''<div><h3>{t('The people behind TTW', 'TTW 创办团队')}</h3>'''
        f'''<div class="split">'''
        f'''<div class="card">'''
        f'''<img class="lead-photo" src="/assets/roland-lang.webp" width="72" height="72" loading="lazy" alt="Roland Lang">'''
        f'''<h3>Roland Lang</h3><p>{t('Founder and Program Director', '创始人兼课程负责人')}</p>'''
        f'''<ul class="check-list">'''
        f'''<li>{t(
            'Ph.D. in Robotics and Automation, the University of British Columbia',
            '英属哥伦比亚大学机器人与自动化博士',
        )}</li>'''
        f'''<li>{t(
            'Registered Professional Engineer (P.Eng.) in Ontario',
            '安大略省注册专业工程师（P.Eng.）',
        )}</li>'''
        f'''<li>{t('Over 20 years of higher education experience', '拥有20余年高等教育经验')}</li>'''
        f'''<li>{t(
            'Former Software Engineer at Motorola Cellular Equipment Company',
            '曾任摩托罗拉蜂窝设备公司软件工程师',
        )}</li>'''
        f'''</ul>'''
        f'''</div>'''
        f'''<div class="notebook">'''
        f'''{eye('Welcome', '欢迎')}'''
        f'''<h3>{t('A note from our founder', '创始人寄语')}</h3>'''
        f'''<p class="lead founder-note">{t(
            'Tinker Tech World is built on a simple belief: young learners understand technology most deeply '
            'when they build, test and improve something of their own. Our programs are shaped around this '
            'cycle—imagine, build, test, explain—so that every learner comes away with more than a working '
            'robot: the confidence and reasoning skills to take on the next problem. As TTW grows, our goal '
            'stays the same—to give young minds in Markham a hands-on, engineering-minded path from curiosity '
            'to capability.',
            'Tinker Tech World 秉持一个朴素的理念：当孩子亲手搭建、测试并改进属于自己的作品时，才能真正理解技术。'
            '我们的课程围绕这一学习循环——构思、搭建、测试、讲解——展开，让每一位学习者收获的不仅是一台能运转的机器人，'
            '更是解决下一个问题的信心与思维能力。随着 TTW 不断成长，我们的目标始终如一：为万锦的孩子们提供一条'
            '从好奇心出发、通向真正能力的动手工程学习路径。',
        )}</p>'''
        f'''<p class="small">— Roland Lang, {t('Founder', '创始人')}</p>'''
        f'''</div>'''
        f'''</div>'''
        f'''<div class="grid three" style="margin-top:22px">{''.join(
            f'<article class="card">'
            + (f'<img class="lead-photo" src="/assets/{photo}" width="72" height="72" loading="lazy" alt="{esc(name)}">'
               if photo else '')
            + f'<h3>{name}</h3><p>{t(en, zh)}</p>'
            + (f'<ul class="check-list">{"".join(f"<li>{t(be, bz)}</li>" for be, bz in bio)}</ul>' if bio else '')
            + '</article>'
            for name, en, zh, photo, bio in program_leads
        )}</div></div>'''
    ) + cta()
    render(
        'about.html', t('About TTW', '关于 TTW'),
        t(
            'Meet the purpose and people behind Tinker Tech World, a hands-on robotics and STEM learning initiative in Markham.',
            '了解 Tinker Tech World 万锦机器人与 STEM 实践学习项目的理念与团队。',
        ),
        about, 'about',
    )

    approach = heading(
        t('Learning that<br>connects the dots.', '让知识<br>相互连接。'),
        t(
            'Robotics, coding and making work best when a learner can connect them. The TTW approach centres on '
            'a project, a question and a reason to try again.',
            '当学生能将机器人、编程与制作联系起来时，学习更有意义。TTW 以项目、问题和继续尝试的动力为核心。',
        ),
        ['The learning approach', '学习方式'],
    )
    approach += section(
        f'''<div class="split"><div class="process">{process()}</div>'''
        f'''<div class="notebook">'''
        f'''<h3>{t("What can a parent look for?", "家长可以关注什么？")}</h3>'''
        f'''<p>{t(
            "Ask the learner to explain the goal, show a test, describe a problem and point to a change. "
            "These small pieces of evidence make progress more meaningful than a finished model alone.",
            "请孩子解释目标、展示一次测试、描述一个问题，并指出一项修改。这些小小的证据，比单独看完成的模型更能体现进步。",
        )}</p>'''
        f'''<p class="line">{t("A progression in understanding, not just a bigger kit.", "关注理解的进阶，而不仅是设备的升级。")}</p>'''
        f'''</div></div>''',
        'tinted',
    ) + cta()
    render(
        'makerspace.html', t('Our Learning Approach', '学习方式'),
        t(
            'See how TTW connects designing, building, testing and explaining through hands-on project learning.',
            '了解 TTW 如何通过实践项目连接设计、搭建、测试与表达。',
        ),
        approach,
    )

    render(
        'faq.html', t('Parent FAQ', '家长常见问题'),
        t(
            'Answers about starting levels, trial requests, program availability, fees and enrollment at TTW.',
            '了解 TTW 学习起点、体验申请、开班状态、费用与报名常见问题。',
        ),
        heading(
            t('Good questions.<br>Clear next steps.', '好问题，<br>清晰的下一步。'),
            t('The details that help you make a confident choice for your learner.', '帮助您为学习者做出合适选择的具体信息。'),
            ['Parent FAQ', '家长常见问题'],
        ) + section(faqs(True)) + cta(),
    )

    contact = heading(
        t('Let’s talk about<br>what comes next.', '一起聊聊，<br>下一步的可能。'),
        t(
            'Ask about a learning pathway, a trial or future workshops. We’ll use your interests to start the conversation.',
            '欢迎咨询学习路径、体验课或未来工作坊。我们从您的兴趣聊起。',
        ),
        ['Contact TTW', '联系 TTW'],
    )
    contact += section(
        f'''<div class="grid two">'''
        f'''<article class="card">'''
        f'''<h2>{t('Email the team', '给团队发邮件')}</h2>'''
        f'''<a class="text-link" style="overflow-wrap:anywhere" href="mailto:{DATA['email']}">{DATA['email']}</a>'''
        f'''<p style="margin-top:20px">{t(
            'Tell us the grade group and what you’d like to explore. Please confirm an appointment before visiting.',
            '请告诉我们年级和希望探索的方向。到访前请先确认预约。',
        )}</p>'''
        f'''<p>{t(DATA['location'])}</p>'''
        f'''</article>'''
        f'''<article class="card">'''
        f'''<h2>{t('Find a starting point', '寻找学习起点')}</h2>'''
        f'''<p>{t('Our short request builder helps you share the details for a trial or program conversation.', '通过简短申请，分享体验课或课程咨询所需的信息。')}</p>'''
        f'''{button()}'''
        f'''<p class="small" style="margin-top:20px">{t('You can write your inquiry in English or Chinese.', '您可以用中文或英文发送咨询。')}</p>'''
        f'''</article>'''
        f'''</div>''',
        'tinted',
    )
    render(
        'contact.html', t('Contact TTW', '联系 TTW'),
        t(
            'Contact Tinker Tech World in Markham about programs, trial classes and future workshops.',
            '联系万锦 Tinker Tech World，咨询课程、体验课和未来工作坊。',
        ),
        contact,
    )

    privacy_sections = [
        ('Preparing a request', '准备申请',
         'Form entries stay in this page until you choose to open an email, copy the message or download it. '
         'This website does not send the form to a server or save it in browser storage.',
         '在您选择打开邮件、复制或下载之前，表单信息仅保留在本页面。本网站不会将表单发送至服务器，也不会存入浏览器存储。'),
        ('Emailing TTW', '向 TTW 发送邮件',
         'When you send the message through your email provider, TTW receives the details you include and your '
         'email address. They are shared for replying to your inquiry. Email services handle messages under their '
         'own policies. Contact TTW with questions about handling or deleting an inquiry.',
         '通过您的邮箱发送后，TTW 将收到您填写的信息及邮件地址，用于回复咨询。邮件服务按其自身政策处理消息。'
         '如对咨询资料的处理或删除有疑问，请联系 TTW。'),
        ('Keep the information minimal', '尽量少提供资料',
         'Use an adult’s contact information. We do not ask for a child’s full name, date of birth, medical '
         'details or payment information. Postal area and discovery source are optional. This form does not '
         'sign you up for marketing.',
         '请使用成人联系方式。本表单不要求孩子全名、出生日期、医疗信息或支付资料。邮编区域和了解来源为选填。'
         '此表单不会将您加入营销订阅。'),
        ('Hosting and external links', '托管与外部链接',
         'This site loads its styles, scripts and images from the same site and uses no advertising analytics or '
         'tracking cookies. The hosting provider may process technical request logs. Links to external websites '
         'and email services use those providers’ own privacy practices.',
         '本站样式、脚本与图片均从本站加载，不使用广告分析或追踪 Cookie。托管服务商可能处理技术访问日志。'
         '外部网站和邮件服务适用其各自的隐私做法。'),
    ]
    privacy = heading(
        t('Your inquiry.<br>Your choice.', '您的咨询，<br>由您选择。'),
        t('How this website handles information when you prepare a request.', '了解本网站在准备申请时如何处理信息。'),
        ['Website privacy', '网站隐私说明'],
    )
    privacy += section(
        '<div class="prose">'
        + ''.join(f'<h2>{t(e, z)}</h2><p>{t(d, zd)}</p>' for e, z, d, zd in privacy_sections)
        + f'<h2>{t("Contact", "联系")}</h2><a href="mailto:{DATA["email"]}">{DATA["email"]}</a>'
        f'<p class="small">{t("Website notice updated September 17, 2026.", "网站说明更新于 2026 年 9 月 17 日。")}</p></div>'
    )
    render(
        'privacy.html', t('Website Privacy', '网站隐私说明'),
        t(
            'Learn how the TTW website prepares inquiry messages and handles optional information.',
            '了解 TTW 网站如何准备咨询消息并处理可选信息。',
        ),
        privacy,
    )

    render(
        '404.html', t('Page not found', '页面未找到'),
        t('Find your way back to TTW programs and trial requests.', '返回 TTW 课程及体验申请页面。'),
        heading(
            t('Let’s try<br>another route.', '换条路径，<br>继续探索。'),
            t('This page could not be found. Explore our programs or head back home.', '没有找到该页面。您可以探索课程或返回首页。'),
        ) + section(
            '<div class="actions">'
            + button(t('Back to Home', '返回首页'), 'index.html')
            + button(t('View Programs', '浏览课程'), 'programs/index.html', 'outline')
            + '</div>'
        ),
        noindex=True,
    )


# ============================================================
# Build entry point
# ============================================================

if __name__ == '__main__':
    for LANG in ['en', 'zh']:
        home()
        other_pages()
        for p in DATA['programs']:
            program_page(p)
        for a in DATA['ages']:
            age_page(a)
        booking()

    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join('<url><loc>' + x + '</loc></url>\n' for x in pages)
        + '</urlset>\n'
    )
    (ROOT / 'robots.txt').write_text(
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /docs/\n'
        'Disallow: /content/\n'
        'Disallow: /tests/\n'
        'Disallow: /scripts/\n'
        'Sitemap: ' + DATA['url'] + '/sitemap.xml\n'
    )
    (ROOT / '.nojekyll').touch()

    exclude_dirs = {'docs', 'content', 'scripts', 'tests', 'assets', 'image'}
    stale = [
        f for f in ROOT.rglob('*.html')
        if not (set(f.relative_to(ROOT).parts[:-1]) & exclude_dirs) and f not in written
    ]
    for f in stale:
        print(f'Removing stale page: {f.relative_to(ROOT)}')
        f.unlink()

    note = f' Removed {len(stale)} stale file(s).' if stale else ''
    print(f'Built {len(pages) + 4} static pages across English and Chinese.' + note)
