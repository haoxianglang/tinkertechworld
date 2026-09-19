// Generated adapter. Business logic lives in server/chat-core.mjs.
import {handleChat} from '../../server/chat-core.mjs';
export const onRequest = ({request, env}) => handleChat(request, env);
