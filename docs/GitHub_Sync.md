# GitHub 与 Cloudflare 发布一致性

更新：2026-09-20。

## 本次差异的原因

GitHub `haoxianglang/tinkertechworld` 的 `main` 分支已提交修改后的 `zh/programs/wro.html`。线上文件却与旧 `dist/` 相同。独立检出并运行旧构建命令后，WRO 文件被模板重新写回长文案，SHA-256 与线上相同。这次问题来自构建覆盖已提交的 HTML。

## 发布原则

GitHub `main` 是线上发布的依据。默认发布只复制已审核的 HTML 和公开资源到 `dist/`，并构建聊天后端知识包，不渲染模板覆盖 HTML。

- `python3 scripts/prepare_deploy.py`：打包当前网页与资源，生成聊天知识包/后端适配器。
- `python3 scripts/build_site.py`：为兼容已有 Cloudflare 设置，默认同样只打包；不再覆盖网页。
- `python3 scripts/build_site.py --regenerate`：明确从模板和 `content/site.json` 重新生成全部页面。先保存/核对直接改过的 HTML，再执行；审查差异后将生成的页面一起提交。
- `npx wrangler@4.135.0 deploy`：自动调用 `prepare_deploy.py`，将 `dist/` 与 Worker 后端一起发布。

可以直接修改 HTML 后提交；如果要继续使用模板维护同一页面，也应将内容更新回模板/JSON，防止将来主动重新生成时恢复旧文案。修改 CSS/JavaScript 时，也要检查页面引用及缓存版本。

## Cloudflare Workers Builds 设置

现有 Worker：`tinkertechworld`。现有域名继续使用，不需创建新 Worker 或删除 Secret。

| 设置 | 值 |
|---|---|
| Git repository | `haoxianglang/tinkertechworld` |
| Production branch | `main` |
| Root directory | 仓库根目录 `/`，不是 `05_website`（当前 GitHub 仓库本身就是网站目录） |
| Build command | `python3 scripts/prepare_deploy.py` |
| Deploy command | `npx wrangler@4.135.0 deploy` |
| Static assets | 由 `wrangler.jsonc` 的 `assets.directory: ./dist` 指定 |
| Worker entry | `cloudflare-worker/worker.js` |

如果现有 Build command 仍为 `python3 scripts/build_site.py`，本次修复保留兼容行为，也会原样打包。请不要在自动构建命令中加入 `--regenerate`。

在 Worker → Settings → Builds 检查关联仓库和生产分支。连接后，push 到生产分支会触发构建及部署；必须等该提交对应的构建成功，线上才更新。参考 [Cloudflare 构建分支](https://developers.cloudflare.com/workers/ci-cd/builds/build-branches/) 和 [构建设置](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/)。

`GEMINI_API_KEY` 留在当前 Worker 的运行时 Secret，不提交到 GitHub、不放在构建变量里。网站源文件、服务端源码与知识库可保存在仓库，只有白名单公开资源会复制到 `dist/`。

## 维护位置

本机 Git 工作副本：`/Users/haoxiang/Library/CloudStorage/Dropbox/gitHub/tinkertechworld`。

TTW 项目中的 `05_website/` 是交付副本，不会自动推送到 GitHub。后续修改必须同步到 Git 工作副本并 commit/push 才会触发线上更新。不要从过期的副本手工部署覆盖新站点。`04_website_spec/` 继续保存 AI 设计与维护规范。

## 验证

```sh
python3 tests/test_deploy_preserves_html.py
python3 scripts/prepare_deploy.py
python3 tests/check_site.py
node --test tests/chat-api.test.mjs
```

回归测试专门模拟直接编辑 HTML，检查新打包命令和旧兼容命令均保留原始字节，且不把密钥或后端源码放入公开目录。线上验收应对比 GitHub 原文件与网页响应的哈希；不要仅根据页面标题或“构建成功”判断同步。
