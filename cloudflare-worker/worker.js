// Generated. Optional standalone Worker; Pages is the primary deployment.
import {handleChat} from '../server/chat-core.mjs';
export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname === '/api/chat') return handleChat(request, env);
    return env.ASSETS ? env.ASSETS.fetch(request) : new Response('Not found', {status: 404});
  }
};
