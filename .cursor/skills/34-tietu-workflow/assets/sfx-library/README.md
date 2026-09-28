# OpenMontage 可复用音效库

当前共 34 个音效，按来源冻结在本地：

- `mixkit/`：26 个 Mixkit 原始音效，覆盖 pop、whoosh、click、notification、transition。
- `freesound-cc0/`：8 个 Freesound CC0 气泡音效的 MP3 预览文件。
- `manifest.jsonl`：逐文件来源、许可、用途与原页面记录。

## 使用顺序

1. 新片需要音效时先查本目录和 `manifest.jsonl`，避免重复下载。
2. 选择语义最贴近的音效，复制或引用到单集 `.media/audio/sfx/`，并登记单集 manifest。
3. 音效只在关键词、数据落点、切镜等节点短促触发；不得连续铺底或盖住口播。
4. 找不到合适素材时，才联网补充；只收许可清晰、允许商用的素材。

## 许可

- Mixkit：按 [Mixkit License](https://mixkit.co/license/) 使用；本库保留下载页和素材 ID。
- Freesound：本目录仅收录搜索结果明确筛选为 Creative Commons 0 的素材；仍保留原作品页。
- Pixabay：可作为后续候选源，但自动访问当前被安全验证拦截，未绕过验证、未收录文件。

下载日期：2026-08-14。
