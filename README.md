# Tinker Tech World website

Report-informed redesign of the existing TTW static website. English and Simplified Chinese; shared components; mobile layouts; explicit program availability; trial and program inquiry paths.

## 当前维护目录 / Working copy

本目录 `05_website/` 是后续网站修改的默认工作目录，包含页面、源码、图片、产品资源、文档与测试脚本。它从原 `tinkertechworld` 仓库完整复制；原目录保留，两个位置当前没有自动同步。

修改前先阅读相邻的 [规范阅读入口](../04_website_spec/README.md) 和 [设计一致性指南](../04_website_spec/Design_Guidelines.md)。完整网站可直接从本目录构建与预览，不依赖原目录的文件。

保留了 `.nojekyll` 和 `CNAME` 等部署文件；没有复制 `.git` 历史、macOS `.DS_Store` 或 Python 缓存。当前复制不代表已推送或上线。发布时仅使用生成的 `dist/` 作为公开文件目录，由 Cloudflare 从源码层编译函数；不上传整个 TTW 工作区。

## Preview / update
```sh
python3 scripts/build_site.py
python3 tests/check_site.py
node scripts/chat_server.mjs
```
Open http://127.0.0.1:8787 . Gemini requires a local `.dev.vars` key or shell environment variable; Cloudflare secrets are not available locally. Edit `content/site.json` for program/grade data, `scripts/build_site.py` for shared/editorial components, and `assets/site.css` for styles. Generated HTML is deployment output; rebuild after edits. Browser test instructions are in `docs/Technical_Architecture.md`.

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
