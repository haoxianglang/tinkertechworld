# Tinker Tech World website

Report-informed redesign of the existing TTW static website. English and Simplified Chinese; shared components; mobile layouts; explicit program availability; trial and program inquiry paths.

## 当前维护目录 / Working copy

本目录 `05_website/` 是后续网站修改的默认工作目录，包含页面、源码、图片、产品资源、文档与测试脚本。它从原 `tinkertechworld` 仓库完整复制；原目录保留，两个位置当前没有自动同步。

修改前先阅读相邻的 [规范阅读入口](../04_website_spec/README.md) 和 [设计一致性指南](../04_website_spec/Design_Guidelines.md)。完整网站可直接从本目录构建与预览，不依赖原目录的文件。

保留了 `.nojekyll` 和 `CNAME` 等部署文件；没有复制 `.git` 历史、macOS `.DS_Store` 或 Python 缓存。当前复制不代表已推送或上线。发布时只部署本目录的站点内容，不发布整个 TTW 工作区。

## Preview / update
```sh
python3 scripts/build_site.py
python3 tests/check_site.py
python3 -m http.server 4173 --bind 127.0.0.1
```
Open http://127.0.0.1:4173 . Edit `content/site.json` for program/grade data, `scripts/build_site.py` for shared/editorial components, and `assets/site.css` for styles. Generated HTML is deployment output; rebuild after edits. Browser test instructions are in `docs/Technical_Architecture.md`.

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
