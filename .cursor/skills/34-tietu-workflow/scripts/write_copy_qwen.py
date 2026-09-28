"""画面文案 / 配套文案：调用百炼 Qwen3.8-Max 起稿。

密钥只从环境变量或本仓库根目录 `.env` 读取（`.env` 已在 .gitignore）。
不要把密钥写进代码、提交说明或聊天。

用法（仓库根目录）:

  py ".cursor/skills/34-tietu-workflow/scripts/write_copy_qwen.py" ^
     --kind scene --brief 要点.txt --out 文案草案.md

  py ".../write_copy_qwen.py" --kind caption --brief 要点.txt --out 配套文案与关键词.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

MODEL = "qwen3.8-max"
DEFAULT_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"

ROOT = Path(__file__).resolve().parents[4]
CORRECTIONS = ROOT / "workspace" / "corrections" / "订正流水账.md"

SYSTEM = """你是老汪，给制造业财务、经营分析做短视频和贴图。观众是会上的成本会计和老板，句子要能当场说出口。

只输出成稿。不要写「我改了什么」「以下是」，不要列写作说明。

硬性：
- 专业词可以出现在解释里，标题和钩子必须是完整人话。禁止把口径、三算、漏斗、铁三角这类两个字概念单独当标题。
- 禁止拿这些词当动词或空话：写死、对齐、闭环、沉淀、抓手、颗粒度、底座、赋能。
- 比喻要说完对象。说账本就写账本，不要写「本子」。
- 封面大标题一眼能看懂本期讲什么。禁止半截比喻、谜语对仗。一行尽量把意思说完，字多可以，不要为了短把话砍残。
- 案例、公司名、比例、年份、图表数字一律另拟，禁止照抄书里的真名真表。
- 适当位置用第一人称「我」写老汪的观察（会上看到、跟老板说过）。不要整篇都是我。
- 画面和标题禁止出现 ELI5、eli5。
- 下面「订正流水账」里用户改过的说法，禁止再用旧版。
"""


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load_api_key() -> str:
    key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    if key:
        return key
    local = _parse_env_file(ROOT / ".env")
    key = local.get("DASHSCOPE_API_KEY", "").strip()
    if key:
        return key
    raise SystemExit(
        "缺少 DASHSCOPE_API_KEY。请设环境变量，或在仓库根目录 .env 写一行（此文件不进 git）。"
    )


def load_corrections() -> str:
    if not CORRECTIONS.is_file():
        return "（暂无订正流水账）"
    text = CORRECTIONS.read_text(encoding="utf-8")
    if len(text) > 12000:
        text = text[:4000] + "\n…（中间略）…\n" + text[-8000:]
    return text


def task_brief(kind: str) -> str:
    if kind == "scene":
        return """这次写「画面文案」，给上滑长图或贴图套图用，不是发布区短标题。

按素材要点写。结构随内容，但要让人能直接填进画面：
- 封面大标题：最多两行，用 | 分开。每行是完整句子，不要谜语。
- 页眉栏目名：读者能看懂的中文，不要写内部工序词。
- 画面正文：按块列出。每块一个小标题 + 1～3 句人话。重点词用「」标出，每块 1～3 个。
- 需要对比就写成左右两句，两边都说清楚在比什么。
- 收口一句判断，会上能复述。

不要写 HTML，不要写页码，不要写内部版式名。"""
    if kind == "caption":
        return """这次写「配套文案与关键词.md」全文，用 Markdown。

必须有：
## 短标题（备选）
5～8 条，每条一句人话。
## 关键词（几组）
3～4 组，每组一行 #词，空格隔开。只写和本期真相关的词。
## 一句话发布文案（可选）
2～4 句即可。

不要出现分镜表、design-system、ELI5。"""
    raise SystemExit("--kind 只能是 scene 或 caption")


def call_qwen(messages: list[dict], thinking: bool) -> str:
    key = load_api_key()
    base = os.environ.get("DASHSCOPE_BASE_URL", DEFAULT_BASE).rstrip("/")
    url = base + "/chat/completions"
    body = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "enable_thinking": thinking,
        "stream": True,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    chunks: list[str] = []
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            for raw in resp:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    evt = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = evt.get("choices") or []
                if not choices:
                    err = evt.get("error") or evt.get("message")
                    if err:
                        raise SystemExit(f"Qwen 返回错误: {err}")
                    continue
                delta = choices[0].get("delta") or {}
                piece = delta.get("content") or ""
                if piece:
                    chunks.append(piece)
                    sys.stdout.write(piece)
                    sys.stdout.flush()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:800]
        raise SystemExit(f"Qwen HTTP {e.code}: {detail}") from e
    text = "".join(chunks).strip()
    if not text:
        raise SystemExit("Qwen 没有返回正文。")
    sys.stdout.write("\n")
    return text


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="用 Qwen3.8-Max 写画面文案或配套文案")
    p.add_argument("--kind", required=True, choices=["scene", "caption"])
    p.add_argument("--brief", required=True, help="素材要点文件路径")
    p.add_argument("--out", required=True, help="成稿输出路径")
    p.add_argument("--no-think", action="store_true", help="关掉思考，直接写")
    args = p.parse_args()

    brief_path = Path(args.brief)
    if not brief_path.is_file():
        raise SystemExit(f"找不到要点文件: {brief_path}")
    source = brief_path.read_text(encoding="utf-8").strip()
    if not source:
        raise SystemExit("要点文件是空的。")

    messages = [
        {"role": "system", "content": SYSTEM + "\n\n## 订正流水账（必须遵守）\n\n" + load_corrections()},
        {
            "role": "user",
            "content": task_brief(args.kind) + "\n\n## 本期素材要点\n\n" + source,
        },
    ]
    text = call_qwen(messages, thinking=not args.no_think)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    print(f"已写入 {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
