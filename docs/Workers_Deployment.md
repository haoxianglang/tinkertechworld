# Cloudflare Workers 发布与聊天 404 修复

更新：2026-09-19。实际线上站点：<https://tinkertechworld.haoxianglang.workers.dev/zh/>。

## 已确认的故障

用户在此 workers.dev 站点点击聊天后失败。实际 `POST /api/chat` 返回 HTTP 404、空响应体。当前请求没有到达已实现的 Gemini handler；不能据此判断 Gemini Key 无效或额度不足。最可能是当前部署只有静态资源，或没有接入正确的 Worker 入口。

此前指南假定使用 Pages，与用户提供的实际地址不一致。`functions/api/chat.js` 是 Pages 适配器，Workers 不会自动加载这个目录。

## 修复配置

`05_website/wrangler.jsonc` 现在统一配置：

- Worker 名称 `tinkertechworld`，与现有网址一致。
- `main`: `cloudflare-worker/worker.js`，导入共享 Gemini 后端与知识包。
- `assets.directory`: `dist`；`ASSETS` 绑定处理网站文件。
- `assets.run_worker_first`: `["/api/*"]`，保证聊天请求进入 Worker。
- 构建命令自动生成页面与知识包；保留已有普通运行时变量（`keep_vars`）。

这些配置遵循 [Cloudflare Worker 与静态资源路由](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/) 和 [资源绑定配置](https://developers.cloudflare.com/workers/static-assets/binding/)。

## 发布到现有 Worker

在 `05_website/` 目录执行：

```sh
npx wrangler@4.135.0 login
npx wrangler@4.135.0 whoami
npx wrangler@4.135.0 deploy
```

登录应使用拥有 `haoxianglang.workers.dev` 的现有 Cloudflare 账号；如账号有多个账户，部署前确认选中此 Worker 所在的账户。不要选择创建临时账号或发布到另一个新站点。用户已完成登录并发布修复，当前状态见文末线上部署进展。

如通过 Workers Builds 的 Git 集成发布，项目根目录必须指向 `05_website`（仅网站仓库则为仓库根目录），部署命令用 `npx wrangler@4.135.0 deploy`。不要使用 `wrangler pages deploy` 或仅上传 `dist`。

## 密钥检查

在现有 **tinkertechworld Worker** 的 Settings → Variables and Secrets 中确认运行时 `GEMINI_API_KEY`。只配置在另一个 Pages 项目或构建阶段的变量不会供此 Worker 运行时使用。已经存在于正确 Worker 的 Secret 应保留，不需要重新创建或把值发到聊天中。

若确实缺少，可由用户在 Cloudflare 面板填写 Secret，或在终端交互输入：

```sh
npx wrangler@4.135.0 secret put GEMINI_API_KEY
```

不要把 Key 写进命令行参数、wrangler.jsonc 或前端。可选 `GEMINI_MODEL` 未配置时默认使用 `gemini-3.1-flash-lite`。

## 发布后验收

- `GET /zh/` 返回网页。
- `GET /api/chat` 应返回 405 JSON，而不是 404；证明请求进入了后端。
- `POST /api/chat` 带合法 JSON，配置正确时应返回 200 及 `reply`、`sources`。
- 503 `not_configured` 表示当前 Worker 的运行时 Secret 缺失。
- 429 表示限流或上游繁忙；502/504 需继续检查模型、供应商响应或超时。
- 实际询问“四年级适合什么课程？”、“那学费呢？”及知识库未覆盖的问题。

## 本次验证边界

Workers 部署 dry-run 已成功打包后端和 109 个公开资源，随后已发布到现有 Worker。14 项接口测试通过；本地 Workers 运行时实测网页 200、GET API 405、缺少本地密钥时 POST API 503，证明入口接通；私密文件 404。随后生产 Secret 已配置，四项真实 Gemini 测试均返回 200，详情见文末最终验收。完整知识库与聊天维护规则见 [Chatbot_Guide.md](Chatbot_Guide.md)。

## 最终验收（2026-09-19）

已发布至现有站点，最终 Worker 版本 `7b1b2c62-fed6-480f-84dc-9dce5873a494`。

修复三个连续问题：原 `/api/chat` 404（补齐 Workers 入口）；运行时缺少 Gemini 密钥（由用户配置 Secret）；旧 `gemini-2.5-flash` 在实际请求中返回模型不可用（改用 `gemini-3.1-flash-lite`，最小思考等级）。新模型使用官方支持的结构化输出，温度 1；环境变量仍可覆盖模型。

真实线上测试四项全部 200：中文四年级选课、携带上下文追问学费（正确引用 $40/节）、英文会员权益、未知实时名额（明确无法查询或预留）。响应约 1.2–2.1 秒，仅代表本次测试。网页端也已显示真实回复和资料链接。未读取、复制或保存密钥值。

发布前 14 项服务端测试通过；56 个 HTML 页面、54 个 sitemap 条目检查通过。实际测试记录位于 `06_testing/website/chatbot/production-gemini-results.json`；此前 503 记录是修复过程的历史状态，不是当前状态。

[当前模型官方说明](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite) · [思考配置](https://ai.google.dev/gemini-api/docs/generate-content/thinking)
