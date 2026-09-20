# Tinker Tech World website

Report-informed redesign of the existing TTW static website. English and Simplified Chinese; shared components; mobile layouts; explicit program availability; trial and program inquiry paths.

## 发布来源 / Source of truth

线上发布以 GitHub `haoxianglang/tinkertechworld` 的 `main` 分支为准。Git 工作副本在 Dropbox 的 `gitHub/tinkertechworld`；TTW 的 `05_website/` 是交付副本，二者没有自动同步。

部署会原样打包仓库内已提交的 HTML 和公开资源。仅明确执行 `python3 scripts/build_site.py --regenerate` 才会从模板覆盖页面；生成后先审查并提交 HTML。详细配置与维护规则见 [GitHub_Sync.md](docs/GitHub_Sync.md)。不要上传密钥或整个源码目录作为公开网站。

## Preview / update
```sh
python3 scripts/prepare_deploy.py
python3 tests/check_site.py
node scripts/chat_server.mjs
```
Open http://127.0.0.1:8787 . Gemini requires a local `.dev.vars` key or shell environment variable; Cloudflare secrets are not available locally. Edit `content/site.json` for program/grade data, `scripts/build_site.py` for shared/editorial components, and `assets/site.css` for styles. To apply template/content edits, explicitly run `python3 scripts/build_site.py --regenerate`, review the resulting HTML and commit it. Deployment preserves committed HTML as-is. Browser test instructions are in `docs/Technical_Architecture.md`.

## Decisions and traceability
- [Website specification](docs/Website_Spec.md)
- [Information architecture](docs/Information_Architecture.md)
- [Content/source map](docs/Content_Map.md)
- [Technical architecture](docs/Technical_Architecture.md)
- [SEO plan](docs/SEO_Plan.md)
- [Verification record](docs/QA_Report.md)

These specifications were derived during implementation; no pre-existing approved website specification was found. The user's requested navigation is implemented, while conflicting or unconfirmed business details are kept out of public claims.

## Production boundary
The build is deployable on the existing static host. It prepares and previews an inquiry and hands it to the user's email application; it **does not** reserve a real slot, deliver a server-side form, take payment or claim a confirmed booking. Mailbox receipt was not tested. A direct email, copy and text-download fallback are available. No analytics or tracking cookies.

Before marketing this as an open enrollment site, the owner must provide confirmed trial times/fees, course availability, location, written policies and any real booking integration. FLL is retained from the current brief as an inquiry page; the earlier WRO-first strategy does not establish a registered FLL team. Future programs/camps remain labeled. Existing imagery is labeled conceptual, not actual students or premises.

No remote commit, push, deployment, DNS changes or outbound inquiry emails were performed. Existing logo/source images, CNAME and product assets are retained.

## Tinker AI chatbot（2026-09-19）

Tinker 现在通过同域 `/api/chat` 使用 Gemini 和 `knowledge/*.md`，支持连续对话和资料链接，不再使用关键词 FAQ 回退。2026-09-19 用户提供的实际线上地址为 `https://tinkertechworld.haoxianglang.workers.dev`，属于 Workers。此前将密钥位置理解为 Pages；实际应检查此 Worker 的运行时 `GEMINI_API_KEY` Secret，该值不会被读取或复制到前端。

实际 Workers 发布步骤见 [Workers_Deployment.md](docs/Workers_Deployment.md)。`wrangler.jsonc` 同时配置 Worker 后端入口及 `dist/` 公开资源，`/api/*` 优先进入后端。使用 `npx wrangler@4.135.0 deploy`；仅上传 `dist/` 不会部署聊天接口。构建会同步知识库。Pages 是备用方式，不能用于当前 workers.dev 站点。

本地完整预览：`node scripts/chat_server.mjs`，打开 `http://127.0.0.1:8787/`。可在 `.dev.vars` 配置本地测试 Key；不配置则 UI 会明确显示 AI 不可用。旧的纯静态 `http.server` 不提供聊天 API。

验证：`node --test tests/chat-api.test.mjs`；浏览器模拟测试：`node tests/chat-browser.cjs`。本地模拟成功不代表生产 Gemini 已联调；需部署后使用真实环境验证。

线上验收（2026-09-19）：Workers 后端已发布并接通 Secret，默认模型更新为 `gemini-3.1-flash-lite`。中文、英文、连续追问及未知席位问题的真实 Gemini 调用均通过，网页端已验证回复与资料链接。
