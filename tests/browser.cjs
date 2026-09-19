/* Behaviour, responsive layout and keyboard checks. No messages are sent. */
const {chromium} = require(process.env.TTW_PLAYWRIGHT_PATH || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root=path.resolve(__dirname,'..');
const base=process.env.TTW_BASE_URL || 'http://127.0.0.1:4173';
const output=process.env.TTW_QA_OUTPUT || '/tmp/ttw-qa';
fs.mkdirSync(output,{recursive:true});
const routes=[...fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(x=>new URL(x[1]).pathname).concat(['/404.html','/zh/404.html']);
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.TTW_BROWSER || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({reducedMotion:'reduce'});
 const page=await context.newPage();const errors=[];const badResponses=[];let networkSubmissions=0;
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400)badResponses.push(r.url()+': '+r.status())});
 page.on('request',r=>{if(r.method()==='POST')networkSubmissions++});
 for(const width of [320,390,768,1024,1440]){
  await page.setViewportSize({width,height:960});
  for(const route of routes){
   await page.goto(base+route);
   const layout=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,broken:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src)}));
   assert(layout.scroll<=layout.width+1,`overflow ${width} ${route}: ${JSON.stringify(layout)}`);
   assert.equal(layout.broken.length,0,`broken image ${route}`);
  }
  console.log(`PASS responsive ${width}px: ${routes.length} pages`);
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto(base);
 await page.screenshot({path:path.join(output,'home-desktop.png'),fullPage:true});
 await page.keyboard.press('Tab');assert.equal(await page.locator('.skip').evaluate(e=>e===document.activeElement),true);
 await page.keyboard.press('Enter');assert.equal(await page.locator('#main').evaluate(e=>e===document.activeElement),true);
 await page.setViewportSize({width:390,height:844});await page.goto(base);
 await page.screenshot({path:path.join(output,'home-mobile.png'),fullPage:true});
 const menu=page.locator('.menu-toggle');await menu.focus();await page.keyboard.press('Enter');assert.equal(await menu.getAttribute('aria-expanded'),'true');assert(await page.locator('#navigation').isVisible());
 await page.keyboard.press('Escape');assert.equal(await menu.getAttribute('aria-expanded'),'false');assert.equal(await menu.evaluate(e=>e===document.activeElement),true);
 const faq=page.locator('summary').first();await faq.focus();await page.keyboard.press('Enter');assert.equal(await faq.evaluate(e=>e.parentElement.open),true);
 for(const lang of ['', '/zh']){
  await page.goto(base+lang+'/contact-us.html?program=lego-robotics&grade=grades-3-6');
  assert.equal(await page.locator('#program').inputValue(),'lego-robotics');assert.equal(await page.locator('#grade').inputValue(),'grades-3-6');
  await page.locator('button[type=submit]').click();assert(await page.locator('#review').isHidden());
  await page.locator('#name').fill('QA Parent <script>alert(1)</script>');await page.locator('#email').fill('qa@example.invalid');
  await page.locator('#timing').fill('Saturday morning');await page.locator('#area').fill('BAD');await page.locator('#consent').check();
  await page.locator('button[type=submit]').click();assert(await page.locator('#review').isHidden());
  await page.locator('#area').fill('L3R');await page.locator('#notes').fill('Test only: A&B + 中文 <img src=x onerror=alert(1)>');
  await page.locator('button[type=submit]').click();assert(await page.locator('#review').isVisible());
  const message=await page.locator('#request-preview').inputValue();assert(message.includes('qa@example.invalid'));assert(message.includes('<script>'));
  const href=await page.locator('#send-email').getAttribute('href');assert(href.startsWith('mailto:tinkertechworld@gmail.com?'));
  const mail=new URL(href);assert.equal(mail.searchParams.get('body'),message);
  assert.equal(await page.locator('#review img').count(),0);
  const downloadPromise=page.waitForEvent('download');await page.locator('#download-request').click();const download=await downloadPromise;
  await download.saveAs(path.join(output,lang?'zh-request.txt':'request.txt'));assert.equal(fs.readFileSync(path.join(output,lang?'zh-request.txt':'request.txt'),'utf8'),message);
  await page.locator('#copy-request').click();await page.waitForFunction(() => document.querySelector('#form-status').textContent.length > 0);
  await page.screenshot({path:path.join(output,lang?'booking-zh.png':'booking.png'),fullPage:true});
  await page.locator('#notes').fill('Updated question');assert(await page.locator('#review').isHidden());
  await page.locator('button[type=submit]').click();assert((await page.locator('#request-preview').inputValue()).includes('Updated question'));
 }
 await page.goto(base+'/contact-us.html?program=evil&grade=invalid');assert.equal(await page.locator('#program').inputValue(),'');assert.equal(await page.locator('#grade').inputValue(),'');
 await page.goto(base+'/contact-us.html?program=distilled&grade=high-school');await page.locator('.language-link').click();assert.equal(await page.locator('html').getAttribute('lang'),'zh-Hans');assert.equal(await page.locator('#program').inputValue(),'distilled');
 await page.setViewportSize({width:1440,height:1000});await page.goto(base+'/zh/index.html');await page.screenshot({path:path.join(output,'home-zh-desktop.png'),fullPage:true});
 await page.goto(base+'/programs/lego-robotics.html');await page.screenshot({path:path.join(output,'program-desktop.png'),fullPage:true});
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const fallback=await nojs.newPage();await fallback.goto(base);assert(await fallback.locator('#navigation').isVisible());assert(await fallback.locator('h1').isVisible());await fallback.goto(base+'/contact-us.html');assert(await fallback.locator('noscript').isVisible());assert(await fallback.locator('#inquiry-form').isHidden());
 assert.equal(networkSubmissions,0);assert.deepEqual(errors,[]);assert.deepEqual(badResponses,[]);
 console.log('PASS: keyboard skip/menu/FAQ, bilingual validated request preview, mailto encoding, download, copy fallback, invalidation, prefill, language preservation, no-JS fallback, no POSTs, no console/resource errors.');
 fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({pages:routes.length,widths:[320,390,768,1024,1440],browser:'Chromium via installed Chrome',errors,badResponses,networkSubmissions},null,2));
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
