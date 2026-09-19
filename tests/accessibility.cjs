/* Optional axe-core WCAG 2.1 AA audit. Install axe-core separately; not a production dependency. */
const {chromium}=require(process.env.TTW_PLAYWRIGHT_PATH || 'playwright');
const fs=require('node:fs');const path=require('node:path');
const axe=fs.readFileSync(process.env.TTW_AXE_PATH || require.resolve('axe-core/axe.min.js'),'utf8');
const root=path.resolve(__dirname,'..');const out=process.env.TTW_QA_OUTPUT || '/tmp/ttw-qa';fs.mkdirSync(out,{recursive:true});
const routes=[...fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(x=>new URL(x[1]).pathname).concat(['/404.html','/zh/404.html']);
(async()=>{
const browser=await chromium.launch({executablePath:process.env.TTW_BROWSER || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const page=await browser.newPage();const findings=[];
for(const width of [390,1440]){
 await page.setViewportSize({width,height:960});
 for(const route of routes){
  await page.goto('http://127.0.0.1:4173'+route);await page.addScriptTag({content:axe});
  const results=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
  if(results.violations.length)findings.push({route,width,violations:results.violations.map(x=>({id:x.id,impact:x.impact,description:x.description,nodes:x.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});
 }
 console.log('Audited '+routes.length+' pages at '+width+'px');
}
for(const [route,name,width] of [['/index.html','home-desktop-viewport',1440],['/index.html','home-mobile-viewport',390],['/zh/index.html','home-zh-viewport',1440],['/contact-us.html','booking-viewport',390]]){await page.setViewportSize({width,height:960});await page.goto('http://127.0.0.1:4173'+route);await page.screenshot({path:path.join(out,name+'.png')});}
fs.writeFileSync(path.join(out,'accessibility.json'),JSON.stringify(findings,null,2));console.log(JSON.stringify(findings));await browser.close();if(findings.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
