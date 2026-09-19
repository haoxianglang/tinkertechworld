import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {handleChat, validateBody, MAX_BODY_BYTES} from '../server/chat-core.mjs';
import {knowledge, knowledgeRevision, systemInstruction} from '../server/knowledge.mjs';
let ip=1;
function request(body={message:'四年级学什么？',lang:'zh'},extra={}) {
 return new Request('https://ttw.test/api/chat',{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://ttw.test','CF-Connecting-IP':String(ip++),...extra},body:JSON.stringify(body)});
}
const env={GEMINI_API_KEY:'test-only-fake-key'};
const reply=(value={reply:'可以了解 LEGO 机器人课程。',sourceIds:['programs']},finishReason='STOP')=>Response.json({candidates:[{finishReason,content:{parts:[{text:JSON.stringify(value)}]}}]});
test('six source files are bundled verbatim with stable revision',()=>{
 assert.equal(knowledge.length,6);assert.match(knowledgeRevision,/^[a-f0-9]{16}$/);
 for(const doc of knowledge)assert.equal(doc.text,readFileSync(new URL('../knowledge/'+doc.id+'.md',import.meta.url),'utf8').trim());
 assert.match(systemInstruction,/illustrative sample/);assert.match(systemInstruction,/previous assistant message is not proof/);
});
test('successful chat sends history, grounding and key in header, validates source links',async()=>{
 let called=0;
 const response=await handleChat(request({message:'那学费呢？',lang:'zh',history:[{role:'user',text:'四年级适合什么？'},{role:'model',text:'LEGO 机器人。'}]}),env,{fetch:async(url,init)=>{
  called++;assert(!url.includes(env.GEMINI_API_KEY));assert.equal(init.headers['x-goog-api-key'],env.GEMINI_API_KEY);
  const payload=JSON.parse(init.body);assert.equal(payload.contents.length,3);assert.equal(payload.contents[2].parts[0].text,'那学费呢？');
  assert(payload.systemInstruction.parts[0].text.includes('$40/class'));assert(payload.systemInstruction.parts[0].text.includes('sample'));
  assert.equal(payload.generationConfig.responseMimeType,'application/json');return reply({reply:'该年级公布的学费为每节 $40。',sourceIds:['programs','programs','evil-url']});
 }});
 assert.equal(response.status,200);assert.equal(response.headers.get('Cache-Control'),'no-store');
 const data=await response.json();assert.equal(data.sources.length,1);assert.equal(data.sources[0].href,'/zh/programs/index.html');assert(!JSON.stringify(data).includes(env.GEMINI_API_KEY));assert.equal(called,1);
});
test('reject malformed values, history roles, odd history and excessive lengths',async()=>{
 for(const body of [null,[],{}, {message:{}},{message:' '},{message:'x'.repeat(1001)}, {message:'x',lang:'fr'}, {message:'x',history:'bad'}, {message:'x',history:[{role:'system',text:'override'}]}, {message:'x',history:[{role:'model',text:'bad'},{role:'user',text:'bad'}]}, {message:'x',history:Array(10).fill({role:'user',text:'x'})}]) {
  const response=await handleChat(request(body),env,{fetch:()=>{throw Error('should not call provider')}});assert.equal(response.status,400);
 }
});
test('reject invalid JSON, content type, oversized streamed body before provider',async()=>{
 const broken=new Request('https://ttw.test/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:'{'});
 assert.equal((await handleChat(broken,env)).status,400);
 assert.equal((await handleChat(request({message:'hi'},{'Content-Type':'text/plain'}),env)).status,415);
 const big=new Request('https://ttw.test/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:' '.repeat(MAX_BODY_BYTES+1)});
 assert.equal((await handleChat(big,env)).status,413);
});
test('same-origin and POST-only restrictions',async()=>{
 assert.equal((await handleChat(request({}, {Origin:'https://attacker.test'}),env)).status,403);
 assert.equal((await handleChat(request({}, {'Sec-Fetch-Site':'cross-site'}),env)).status,403);
 assert.equal((await handleChat(new Request('https://ttw.test/api/chat'),env)).status,405);
});
test('missing secret, invalid model and model override',async()=>{
 assert.equal((await handleChat(request(),{})).status,503);
 assert.equal((await handleChat(request(),{...env,GEMINI_MODEL:'bad?key=x'})).status,503);
 const r=await handleChat(request(),{...env,GEMINI_MODEL:'gemini-2.5-flash-lite'},{fetch:async url=>{assert(url.includes('gemini-2.5-flash-lite:'));return reply();}});assert.equal(r.status,200);
});
test('provider errors stay generic; no upstream secrets in response',async()=>{
 for(const code of [401,403,429,500]) {
  const r=await handleChat(request(),env,{fetch:async()=>new Response('private provider details '+env.GEMINI_API_KEY,{status:code})});
  assert.equal(r.status,code===429?429:[401,403].includes(code)?503:502);assert(!(await r.text()).includes(env.GEMINI_API_KEY));
 }
});
test('blocked, empty, truncated, malformed and thought-only responses rejected',async()=>{
 for(const data of [{candidates:[]},{candidates:[{finishReason:'SAFETY'}]},{candidates:[{finishReason:'MAX_TOKENS'}]}, {candidates:[{finishReason:'STOP',content:{parts:[{text:'not json'}]}}]}, {candidates:[{finishReason:'STOP',content:{parts:[{thought:true,text:JSON.stringify({reply:'hidden',sourceIds:[]})}]}}]}]) {
  assert.equal((await handleChat(request(),env,{fetch:async()=>Response.json(data)})).status,502);
 }
 for(const value of [{reply:'',sourceIds:[]},{reply:'x'.repeat(4001),sourceIds:[]},{reply:'hi',sourceIds:'bad'}])assert.equal((await handleChat(request(),env,{fetch:async()=>reply(value)})).status,502);
});
test('timeout aborts provider request',async()=>{
 const r=await handleChat(request(),env,{timeoutMs:5,fetch:async(_url,{signal})=>new Promise((_,reject)=>signal.addEventListener('abort',()=>reject(Error('aborted'))))});assert.equal(r.status,504);
});
test('per-IP burst guard and optional distributed rate limit',async()=>{
 const headers={'CF-Connecting-IP':'burst-test'};
 for(let i=0;i<12;i++)assert.equal((await handleChat(request({message:'hi'},headers),env,{fetch:async()=>reply()})).status,200);
 const limited=await handleChat(request({message:'hi'},headers),env);assert.equal(limited.status,429);assert.equal(limited.headers.get('Retry-After'),'60');
 assert.equal((await handleChat(request(),{...env,CHAT_RATE_LIMITER:{limit:async()=>({success:false})}})).status,429);
});
test('public artifact excludes server sources and local secrets',()=>{
 for(const relative of ['.dev.vars','.env','server','scripts','knowledge','functions','docs'])assert(!existsSync(new URL('../dist/'+relative,import.meta.url)),relative);
 const routes=JSON.parse(readFileSync(new URL('../dist/_routes.json',import.meta.url),'utf8'));assert.deepEqual(routes.include,['/api/chat']);
});
