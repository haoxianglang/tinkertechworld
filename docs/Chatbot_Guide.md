# Tinker Chatbot · 开发、知识库与部署指南

更新：2026-09-19。适用目录：TTW 项目的 `05_website/`。

## 当前实现

Tinker 已从基本关键词 FAQ helper 改为 Gemini AI 对话助手。浏览器只访问同域 `POST /api/chat`；Gemini API Key 只通过服务端环境变量读取，不出现在 HTML、前端 JavaScript 或模型提示词中。

用户已说明 `GEMINI_API_KEY` 配置在 Cloudflare Pages。本次没有读取该密钥，也没有将其复制到本地。生产环境是否能成功调用仍须在新代码部署后验证。

```text
页面聊天窗口 → POST /api/chat → Cloudflare Pages Function
                                  ↓
                      server/chat-core.mjs
                      + server/knowledge.mjs
                                  ↓
                   Google Gemini generateContent
                                  ↓
                纯文本回答 + 经过校验的资料链接
```

- 支持中文、英文和追问；最多携带最近四轮已成功对话，并按 UTF-8 字节数进一步压缩历史。
- 浏览器只在内存保留历史；重新开始/刷新会清除。服务端不保存聊天档案，也不记录消息正文或供应商原始错误。
- 失败时明确显示不可用、超时或请求过多，并提供重试与联系 TTW。**不再静默回退为关键词匹配，也不把失败伪装成正常 AI 回答。**
- 回复按纯文本显示；来源链接由服务端根据已知文档 ID 生成，不执行模型生成的 HTML 或任意 URL。
- AI 回答仍可能出错。来源链接表示模型所引用的 TTW 资料，不是独立事实审核的证明。

## 关键文件

| 文件 | 作用 |
|---|---|
| `assets/chat.js` | 独立聊天前端、对话历史、加载/错误/重试/清除、来源链接 |
| `scripts/build_site.py` 内的 `tinker_widget()` | 双语聊天组件和提示文案；隐私页同步说明 AI 数据流 |
| `server/chat-core.mjs` | 本地、Pages 和可选 Worker 共用的服务端接口 |
| `server/knowledge.mjs` | 自动生成的知识包；不手工编辑 |
| `scripts/_chat_context.py` | 读取 Markdown、定义资料链接映射、统一提示规则和知识版本 |
| `functions/api/chat.js` | Cloudflare Pages 路由适配器 |
| `scripts/generate_pages_function.py` | 生成知识包和 Pages 适配器 |
| `scripts/generate_worker.py` | 生成可选 Worker 适配器；主部署仍为 Pages |
| `scripts/chat_server.mjs` | 本地同端口网站与 API 服务，读取本地环境配置 |
| `scripts/chat_server.py` | 兼容旧命令的 Node 启动入口 |
| `scripts/stage_public.py` | 生成只包含公开资源的 `dist/` |
| `.dev.vars.example` | 本地环境变量格式示例，不包含密钥 |
| `tests/chat-api.test.mjs` | 服务端自动化测试，模拟供应商响应 |
| `tests/chat-browser.cjs` | 双语 UI、追问、错误处理、移动端与无障碍测试 |

## 知识库维护

当前六个文档位于 `knowledge/`：`business-info.md`、`programs.md`、`schedule.md`、`membership.md`、`faq.md`、`about.md`。

这是一份规模较小的公共业务知识库，采用完整上下文注入，不需要额外向量数据库或 embedding 服务。源文档总长度超过 100,000 字符时构建会停止，要求重新评估范围；不要无限增加提示词和调用成本。

1. 编辑 `knowledge/*.md`，仅放适合向访客公开的业务资料。不要放 API Key、学生资料、聊天记录或内部财务。
2. 保持课程价格、状态与网页一致。新增文件会自动纳入知识包（`README.md` 除外）；在 `_chat_context.py` 的 `SOURCE_LINKS` 增加标题和公开页面地址，否则默认链接到联系页面。
3. 运行 `python3 scripts/build_site.py`，它会同时更新网页、知识包、函数适配器和公开发布目录。
4. 修改知识后重新启动本地服务；Cloudflare 上需要重新构建部署才能生效。线上不能直接读取这台 Mac 的本地文件。
5. 运行服务端测试，抽查相关问题的回答及限制措辞。

### 已识别的源资料冲突

当前资料中，旧 FAQ 仍称所有费用尚未公布，而 `programs.md` 已有部分课程价格；某些段落称排期确认，但 `schedule.md` 明确是示例课表。此外，资料中的“已开班”和未来开业日期并不完全一致。

本次保留原业务资料，通过统一提示规则处理：

- 学费优先使用具体课程条目，不据此推断开放席位或税费。
- 时间以 `schedule.md` 的“示例、需确认”限定为准。
- 会员规则以 `membership.md` 为准，保留安全培训和陪同要求。
- 服务端提供万锦当地当前日期，未来公告不能描述为已经发生。
- 无法解决的冲突说明不确定并转人工；不自行宣布营业事实。

这些规则降低错误风险，但不能保证模型永不出错。业务资料应逐步由 TTW 维护为一致版本。

## 环境变量

| 名称 | 设置位置 / 作用 |
|---|---|
| `GEMINI_API_KEY` | Cloudflare Pages Secret；本地可用 `.dev.vars` 或 shell 环境变量 |
| `GEMINI_MODEL` | 可选，默认沿用 `gemini-2.5-flash`；可在服务端改成账号支持的兼容文本模型 |
| `CHAT_PORT` | 本地服务端口，默认 `8787` |
| `CHAT_RATE_LIMITER` | 可选 Cloudflare Rate Limiting binding，不是普通字符串环境变量 |

API Key 通过 `x-goog-api-key` 请求头发送到 Google，不放在请求 URL。请区分 Cloudflare Production 和 Preview 的 Secret 配置。不要在聊天对话中粘贴密钥，也不要把真实 `.dev.vars` 上传到网站。

## 本地运行

需要 Python 3 和 Node.js 20.12+（支持 `process.loadEnvFile` 和内置 fetch）。不需要生产 npm 依赖。

在 `05_website/` 中执行：

```sh
python3 scripts/build_site.py
cp .dev.vars.example .dev.vars
# 用本地编辑器填写 .dev.vars；仅本地测试 Gemini 时需要。
node scripts/chat_server.mjs
```

打开 `http://127.0.0.1:8787/` 或 `/zh/`。同一进程提供网站及 `/api/chat`，不再需要网站 4173 + API 8787 的跨域组合。已有 shell 环境变量优先于本地文件。

没有本地 Key 时网站仍能预览，AI 会明确显示不可用。Cloudflare 中的 Secret 不会自动出现在本机。

`python3 -m http.server` 仅支持静态页面，不能调用 Gemini；只用该命令预览时 chatbot 的失败提示是正常现象。

## Cloudflare Pages 发布

实际公开文件目录改为 `dist/`，其中不包含知识源文件、后端源码、文档、测试或本地环境文件。`functions/` 和 `server/` 保留在项目源码层，由 Cloudflare 单独编译后端。

如使用 Git 集成：将项目根目录设置为 `05_website`（如果仓库只包含网站，使用仓库根目录）；构建命令为 `python3 scripts/build_site.py`；输出目录为 `dist`。保留已有 Secret，并检查 Production / Preview 环境。

如使用 Wrangler，在 `05_website/` 目录执行：

```sh
python3 scripts/build_site.py
npx wrangler pages deploy dist --project-name tinkertechworld
```

项目名需与自己的 Cloudflare Pages 项目一致。Wrangler 从当前项目的 `functions/` 编译接口；不能只上传 `dist` 静态文件后期望 API 自动出现。Cloudflare Dashboard 的普通拖拽上传不支持 Pages Functions，应使用 Git 集成或 Wrangler。[Cloudflare Functions 部署说明](https://developers.cloudflare.com/pages/functions/get-started/)

此次开发只进行了本地构建和函数编译，未执行上述发布命令。发布后需实际验证中文、英文、一次追问和一次未知业务问题。不要将本地模拟测试当作真实 API 成功。

## 接口与边界

请求示例：

```json
{
  "message": "那学费呢？",
  "lang": "zh",
  "history": [
    {"role": "user", "text": "四年级适合什么课程？"},
    {"role": "model", "text": "可以了解 LEGO 机器人。"}
  ]
}
```

成功结果为 `{reply, sources, knowledgeRevision}`，错误结果为 `{error}` 和相应 HTTP 状态码。历史必须按 user/model 成对排列。错误回复、欢迎语和界面提示不会混入模型历史。

- 单条问题最多 1,000 字符；历史最多 8 条；请求体最多 20,000 bytes。
- 服务端 22 秒超时，前端 27 秒超时；超时会取消请求。
- 仅允许同域浏览器调用；校验 Content-Type、JSON、输入类型及角色。不把原始 Google 错误、Key 或完整提示词返回给访客。
- 12 次/分钟/IP 的进程内限流是 best-effort，只在单个实例有效；不等同于全球计费上限。多实例正式运营可配置分布式限流及供应商配额。
- 该助手没有报名、付款、发信或查询实时库存工具，因此不能声称已完成这些动作。
- 用户消息及部分历史会发送给 Google Gemini；页面和隐私说明已披露。刷新只清除本页面历史，不等同于删除供应商侧按其条款处理的数据。

## 测试与参考

```sh
python3 tests/check_site.py
node --test tests/chat-api.test.mjs
# 本地服务启动后；需要 Playwright 与 Chrome，可通过 TTW_PLAYWRIGHT_PATH 指定现有依赖。
node tests/chat-browser.cjs
```

浏览器测试拦截 Gemini 接口，验证 UI 行为，不产生真实 Gemini 调用。`TTW_AXE_PATH` 可指定 axe-core；有该工具时同时检查打开的聊天面板。

- [Gemini generateContent / 多轮对话](https://ai.google.dev/api/generate-content)
- [Gemini 结构化输出](https://ai.google.dev/gemini-api/docs/structured-output)
- [Cloudflare Pages Secret bindings](https://developers.cloudflare.com/pages/functions/bindings/)
- [Cloudflare Pages 本地开发](https://developers.cloudflare.com/pages/functions/local-development/)

## 后续 AI 修改要求

沿用现有 TTW 配色与组件；保留 AI 身份、发送数据提示、清除记录和错误状态。所有供应商调用走共用后端，不在浏览器加 Key。不恢复静默关键词回退。新增业务资料时同时核对公开页面；更换模型或输出格式时运行对应测试，并在实际已配置环境联调。
