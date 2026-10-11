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
 for(const lang of ['', '/zh']){
  await page.goto(base+lang+'/contact-us.html');
  assert.equal(await page.locator('#inquiry-form').count(),0);
  assert.equal(await page.locator('main a[href="mailto:info@tinkertechworld.com"]').count(),1);
  assert.equal(await page.locator('main img').count(),4);
  for (const img of await page.locator('main img').all()) {
   assert(await img.evaluate(i=>i.complete && i.naturalWidth===i.naturalHeight));
  }
  await page.screenshot({path:path.join(output,lang?'contact-zh.png':'contact.png'),fullPage:true});
 }
 await page.goto(base+'/contact.html');await page.waitForURL('**/contact-us.html');
 await page.goto(base+'/contact-us.html');await page.locator('.header-trial a').click();
 assert.equal(await page.locator('html').getAttribute('lang'),'zh-Hans');
 await page.setViewportSize({width:1440,height:1000});await page.goto(base+'/zh/index.html');await page.screenshot({path:path.join(output,'home-zh-desktop.png'),fullPage:true});
 await page.goto(base+'/programs/lego-robotics.html');await page.screenshot({path:path.join(output,'program-desktop.png'),fullPage:true});
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const fallback=await nojs.newPage();await fallback.goto(base);assert(await fallback.locator('#navigation').isVisible());assert(await fallback.locator('h1').isVisible());await fallback.goto(base+'/contact-us.html');assert(await fallback.locator('main a[href="mailto:info@tinkertechworld.com"]').isVisible());assert.equal(await fallback.locator('main img').count(),4);
 assert.equal(networkSubmissions,0);assert.deepEqual(errors,[]);assert.deepEqual(badResponses,[]);
 console.log('PASS: responsive pages, keyboard skip/menu, bilingual contact QR codes, legacy contact redirect, language switch, no-JS contact, no POSTs, no console/resource errors.');
 fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({pages:routes.length,widths:[320,390,768,1024,1440],browser:'Chromium via installed Chrome',errors,badResponses,networkSubmissions},null,2));
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
