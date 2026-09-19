const {chromium}=require(process.env.TTW_PLAYWRIGHT_PATH || '/Users/haoxiang/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs');const assert=require('node:assert/strict');const path=require('node:path');
const base=process.env.TTW_BASE_URL || 'http://127.0.0.1:8787';
const output=process.env.TTW_QA_OUTPUT || '/tmp/ttw-chat-qa';fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.TTW_BROWSER || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const results=[];
 // The unconfigured LOCAL server must fail explicitly; the configured Cloudflare key is not copied here.
 const missing=await page.request.post(base+'/api/chat',{data:{message:'Hi',lang:'en'}});assert.equal(missing.status(),503);
 for(const url of ['/.dev.vars','/.env','/server/knowledge.mjs','/knowledge/programs.md','/scripts/chat_server.mjs'])assert.equal((await page.request.get(base+url)).status(),404,url);
 let requests=[],mode='success';
 await page.route('**/api/chat',async route=>{
  const data=route.request().postDataJSON();requests.push(data);
  if(mode==='network')return route.abort();
  if(mode==='rate')return route.fulfill({status:429,contentType:'application/json',body:'{"error":"rate_limited"}'});
  if(mode==='timeout')return route.fulfill({status:504,contentType:'application/json',body:'{"error":"timeout"}'});
  if(mode==='invalid')return route.fulfill({status:200,contentType:'text/html',body:'<html>wrong endpoint</html>'});
  if(mode==='slow')await new Promise(r=>setTimeout(r,600));
  const zh=data.lang==='zh';
  return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({reply:zh?'四年级可了解 LEGO 机器人。公布学费为每节 $40，具体开班请联系 TTW 确认。':'Grades 3–6 can explore LEGO Robotics. The published tuition is $40 per class; confirm availability with TTW.',sources:[{id:'programs',title:zh?'课程':'Programs',href:(zh?'/zh':'')+'/programs/index.html'},{id:'bad',title:'unsafe',href:'javascript:alert(1)'}]})});
 });
 const send=async question=>{await page.locator('#tinker-input').fill(question);await page.locator('#tinker-form button').click();await page.waitForFunction(()=>document.querySelector('#tinker-form').getAttribute('aria-busy')==='false');};
 const reset=async()=>{await page.locator('#tinker-reset').click();};
 for(const lang of ['en','zh']){
  await page.goto(base+(lang==='zh'?'/zh/index.html':'/'));
  await page.locator('#tinker-launcher').focus();await page.keyboard.press('Enter');assert(await page.locator('#tinker-panel').isVisible());assert.equal(await page.locator('#tinker-input').evaluate(e=>e===document.activeElement),true);
  await send(lang==='zh'?'四年级适合什么？':'Which program suits Grade 4?');
  assert.equal(requests.at(-1).history.length,0);assert.equal(await page.locator('.tinker-sources a').count(),1);
  await send(lang==='zh'?'那么多少钱？':'How much is that?');assert.equal(requests.at(-1).history.length,2);assert.equal(requests.at(-1).history[0].role,'user');assert.equal(requests.at(-1).history[1].role,'model');
  assert.equal(await page.evaluate(()=>localStorage.length),0);
  await reset();await send('<img src=x onerror=alert(1)>');assert.equal(await page.locator('#tinker-messages img').count(),0);
  assert((await page.locator('.tinker-msg.user').textContent()).includes('<img'));
  for(const error of ['network','rate','timeout','invalid']){
   await reset();mode=error;await send('Question');assert(await page.locator('.tinker-error-actions a').isVisible());assert.equal(await page.locator('#tinker-input').inputValue(),'Question');
   mode='success';await page.locator('.tinker-error-actions button').click();await page.waitForFunction(()=>document.querySelector('#tinker-form').getAttribute('aria-busy')==='false');assert.equal(requests.at(-1).history.length,0);assert.equal(await page.locator('.tinker-msg.user').count(),1);
  }
  await reset();mode='slow';await page.locator('#tinker-input').fill('waiting');await page.locator('#tinker-form button').click();assert(await page.locator('#tinker-form button').isDisabled());await reset();await page.waitForTimeout(750);assert.equal(await page.locator('.tinker-msg').count(),1);mode='success';
  await send(lang==='zh'?'四年级适合什么课程？':'Which program suits Grade 4?');
  for(const width of [320,390,768,1440]){
   await page.setViewportSize({width,height:844});const box=await page.locator('#tinker-panel').boundingBox();assert(box.x>=0&&box.x+box.width<=width+1);assert(box.y>=0&&box.y+box.height<=844);
   assert(await page.locator('#tinker-form button').isVisible());assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`document overflow: ${lang} ${width}`);
   if([390,1440].includes(width))await page.screenshot({path:path.join(output,`chat-${lang}-${width}.png`)});
  }
  await page.keyboard.press('Escape');assert(await page.locator('#tinker-panel').isHidden());assert.equal(await page.locator('#tinker-launcher').evaluate(e=>e===document.activeElement),true);
  results.push(lang+' dialogue, errors, retry, reset, XSS, sources, responsive and keyboard checks passed');
 }
 // Automated accessibility of the open, interactive panel in both languages.
 const axePath=process.env.TTW_AXE_PATH || '/tmp/ttw-accessibility/node_modules/axe-core/axe.min.js';
 if(fs.existsSync(axePath))for(const lang of ['en','zh']){
  await page.setViewportSize({width:390,height:844});await page.goto(base+(lang==='zh'?'/zh/':'/'));await page.locator('#tinker-launcher').click();await page.addScriptTag({path:axePath});
  const check=await page.evaluate(()=>axe.run(document.querySelector('#tinker-panel'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));assert.deepEqual(check.violations,[]);results.push(lang+' open-panel axe: 0 violations');
 }
 assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'results.json'),JSON.stringify({results,consoleErrors:errors,provider:'mocked; real Gemini not called'},null,2));console.log(results.join('\n'));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
