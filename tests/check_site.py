#!/usr/bin/env python3
"""Validate generated pages, links, translations, structured data and asset budget."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
errors=[]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.tags=[]; self.ids=[]; self.links=[]; self.scripts=[]; self.script=False; self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); self.tags.append((tag,a))
        if 'id' in a:self.ids.append(a['id'])
        for prop in ['href','src']:
            if prop in a:self.links.append(a[prop])
        if tag=='script' and a.get('type')=='application/ld+json':self.script=True
    def handle_endtag(self,tag):
        if tag=='script':self.script=False
    def handle_data(self,data):
        if self.script:self.scripts.append(data)
files=[p for p in ROOT.rglob('*.html') if not any(x in p.parts for x in ['.git','node_modules'])]
parsed={p:Page(p.read_text()) for p in files}
for p,page in parsed.items():
    label=str(p.relative_to(ROOT)); text=p.read_text()
    def check(ok,msg):
        if not ok:errors.append(label+': '+msg)
    for tag in ['h1','main','title']:
        check(sum(t==tag for t,a in page.tags)==1,f'exactly one {tag}')
    check(len(page.ids)==len(set(page.ids)),'duplicate IDs')
    check(any(t=='html' and a.get('lang') in ['en','zh-Hans'] for t,a in page.tags),'language')
    check(any(t=='meta' and a.get('name')=='description' and a.get('content') for t,a in page.tags),'description')
    check(sum(t=='link' and a.get('rel')=='canonical' for t,a in page.tags)==1,'canonical')
    check(sum(t=='link' and a.get('rel')=='alternate' for t,a in page.tags)==3,'3 hreflang alternates')
    for t,a in page.tags:
        if t=='img':check('alt' in a and 'width' in a and 'height' in a,'image alt/dimensions')
        if t in ['input','select','textarea'] and a.get('type') not in ['checkbox','hidden']:
            check(any(lt=='label' and la.get('for')==a.get('id') for lt,la in page.tags),'form label '+str(a.get('id')))
    check('888-888-8888' not in text,'placeholder phone')
    check('wechat-qr' not in text,'missing QR')
    for data in page.scripts:
        try:json.loads(data)
        except ValueError:check(False,'invalid JSON-LD')
    for href in page.links:
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        target=(ROOT/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else p.parent/unquote(u.path)
        if not u.path:target=p
        if target.is_dir():target=target/'index.html'
        check(target.exists(),'missing target '+href)
        if u.fragment and target in parsed:check(unquote(u.fragment) in parsed[target].ids,'missing fragment '+href)
# All sitemap locations resolve and are canonical/indexable.
urls=ET.parse(ROOT/'sitemap.xml').findall('{*}url/{*}loc')
for loc in urls:
    p=ROOT/unquote(urlsplit(loc.text).path.lstrip('/')); page=parsed.get(p)
    if not page:errors.append('sitemap missing '+loc.text);continue
    if not any(t=='link' and a.get('rel')=='canonical' and a.get('href')==loc.text for t,a in page.tags):errors.append('sitemap canonical mismatch '+loc.text)
    if any(t=='meta' and a.get('name')=='robots' and 'noindex' in a.get('content','') for t,a in page.tags):errors.append('sitemap noindex '+loc.text)
for en in [p for p in files if 'zh' not in p.relative_to(ROOT).parts]:
    if ROOT/'zh'/en.relative_to(ROOT) not in parsed:errors.append('missing Chinese '+str(en))
for path,budget in [('assets/site.js',10000),('assets/site.css',25000),('assets/makerspace.webp',220000),('assets/makerspace-small.webp',100000)]:
    size=(ROOT/path).stat().st_size
    if size>budget:errors.append(f'{path}: {size} > {budget} byte budget')
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(files)} HTML pages, {len(urls)} sitemap entries; local links, fragments, forms, languages, metadata, JSON-LD and asset budgets.')
