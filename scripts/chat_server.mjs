// Node 20.12+ local same-origin server. It never serves dotfiles or backend/knowledge sources.
import {createServer} from 'node:http';
import {readFile, realpath} from 'node:fs/promises';
import {resolve, sep, extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const built = spawnSync(process.env.PYTHON || 'python3', [resolve(root, 'scripts/generate_pages_function.py')], {stdio: 'inherit'});
if (built.status !== 0) process.exit(1);
// An explicitly provided environment value takes precedence over a local secret file.
const saved = {...process.env};
try { process.loadEnvFile(resolve(root, '.dev.vars')); } catch (error) { if (error.code !== 'ENOENT') throw new Error('Unable to read .dev.vars; check its format'); }
for (const [key, value] of Object.entries(saved)) process.env[key] = value;
const {handleChat, MAX_BODY_BYTES} = await import('../server/chat-core.mjs');
const allowedDirs = new Set(['assets','image','products','programs','age-groups','zh']);
const allowedRoot = /^(?:[a-z0-9-]+\.html|robots\.txt|sitemap\.xml)$/;
const types = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.svg':'image/svg+xml','.xml':'application/xml','.txt':'text/plain; charset=utf-8'};
const server = createServer(async (req, res) => {
  try {
    const origin = `http://${req.headers.host}`;
    const pathname = new URL(req.url, origin).pathname;
    if (pathname === '/api/chat') {
      const parts = []; let length = 0;
      for await (const part of req) {
        length += part.length;
        if (length > MAX_BODY_BYTES) { res.writeHead(413, {'Content-Type':'application/json'});res.end('{"error":"request_too_large"}');return; }
        parts.push(part);
      }
      const headers = new Headers();
      for (const [key,value] of Object.entries(req.headers)) if (value) headers.set(key, Array.isArray(value) ? value.join(',') : value);
      headers.set('CF-Connecting-IP', req.socket.remoteAddress || 'local');
      const request = new Request(origin + req.url, {method:req.method,headers,...(!['GET','HEAD'].includes(req.method) ? {body:Buffer.concat(parts)} : {})});
      const result = await handleChat(request, process.env);
      res.writeHead(result.status, Object.fromEntries(result.headers));res.end(Buffer.from(await result.arrayBuffer()));return;
    }
    if (!['GET','HEAD'].includes(req.method)) {res.writeHead(405);res.end();return;}
    let relative = decodeURIComponent(pathname).replace(/^\/+/, '');
    if (!relative || relative.endsWith('/')) relative += 'index.html';
    const segments = relative.split('/');
    if (segments.some(x => x.startsWith('.') || x.includes('\\')) || !(segments.length === 1 ? allowedRoot.test(relative) : allowedDirs.has(segments[0]))) {res.writeHead(404);res.end('Not found');return;}
    const file = await realpath(resolve(root, relative));
    if (!file.startsWith(root + sep)) {res.writeHead(404);res.end('Not found');return;}
    const content = await readFile(file);
    res.writeHead(200, {'Content-Type':types[extname(file).toLowerCase()] || 'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
    res.end(req.method === 'HEAD' ? undefined : content);
  } catch {res.writeHead(404);res.end('Not found');}
});
const port = Number(process.env.CHAT_PORT || 8787);
server.listen(port, '127.0.0.1', () => {
  console.log(`TTW website + /api/chat: http://127.0.0.1:${port}`);
  console.log(process.env.GEMINI_API_KEY ? 'Gemini key loaded (value hidden).' : 'No local key. Chat will explicitly report unavailable; set .dev.vars to test Gemini.');
});
