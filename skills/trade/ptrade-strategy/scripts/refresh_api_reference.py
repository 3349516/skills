from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag


DEFAULT_URL = "http://180.169.107.9:7766/hub/help/api"


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/124 Safari/537.36"
        },
    )
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_text(value: str) -> str:
    return re.sub(r"[ \t]+", " ", value.replace("\xa0", " ")).strip()


def render_table(table: Tag) -> list[str]:
    rows = []
    for row in table.find_all("tr"):
        cells = [clean_text(cell.get_text(" ", strip=True)) for cell in row.find_all(["th", "td"])]
        if cells:
            rows.append(cells)
    if not rows:
        return []
    width = max(len(row) for row in rows)
    normalized = [row + [""] * (width - len(row)) for row in rows]
    output = [
        "| " + " | ".join(normalized[0]) + " |",
        "| " + " | ".join("---" for _ in range(width)) + " |",
    ]
    output.extend("| " + " | ".join(row) + " |" for row in normalized[1:])
    return output


def render_reference(html: str, url: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#help-content") or soup.body or soup
    for unwanted in content.select("script, style, .help-nav"):
        unwanted.decompose()

    lines = [
        "# PTrade API 离线参考",
        "",
        f"- 来源：{url}",
        f"- 抓取时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        "- 说明：此文件由官方帮助页自动转换，接口细节以本快照内容为准。",
        "",
    ]
    headings: list[str] = []
    for element in content.find_all(["h1", "h2", "h3", "h4", "h5", "p", "pre", "table", "li"]):
        if element.find_parent(["pre", "table", "li"]) is not None:
            continue
        name = element.name.lower()
        if name.startswith("h"):
            text = clean_text(element.get_text(" ", strip=True))
            if text:
                level = min(6, int(name[1]) + 1)
                lines.extend([f"{'#' * level} {text}", ""])
                headings.append(text)
        elif name == "pre":
            text = element.get_text("\n", strip=False).strip()
            if text:
                lines.extend(["```python", text, "```", ""])
        elif name == "table":
            rendered = render_table(element)
            if rendered:
                lines.extend(rendered + [""])
        else:
            text = clean_text(element.get_text(" ", strip=True))
            if text:
                prefix = "- " if name == "li" else ""
                lines.extend([prefix + text, ""])

    markdown = "\n".join(lines).rstrip() + "\n"
    return markdown, headings


def render_index(url: str, headings: list[str]) -> str:
    lifecycle = [
        "initialize",
        "before_trading_start",
        "handle_data",
        "after_trading_end",
        "tick_data",
        "on_order_response",
        "on_trade_response",
    ]
    return "\n".join(
        [
            "# PTrade API 索引",
            "",
            f"- 官方来源：{url}",
            "- 完整离线文档：`api-reference.md`",
            "- 更新命令：`uv run --no-sync -- python .codex/skills/ptrade-strategy/scripts/refresh_api_reference.py`",
            "",
            "## 策略生命周期",
            "",
            *(f"- `{name}`" for name in lifecycle),
            "",
            "## 常用检索词",
            "",
            "- 初始化与调度：`set_universe`、`set_benchmark`、`run_daily`、`run_interval`",
            "- 行情数据：`get_history`、`get_price`、`get_snapshot`、`get_stock_status`",
            "- 证券信息：`get_stock_info`、`get_Ashares`、`get_index_stocks`",
            "- 下单交易：`order`、`order_target`、`order_value`、`order_target_value`",
            "- 账户持仓：`context.portfolio`、`cash`、`positions`、`portfolio_value`",
            "- 回测成本：`set_commission`、`set_fixed_slippage`、`set_slippage`",
            "- 日志记录：`log.debug`、`log.info`、`log.warning`、`log.error`、`log.critical`",
            "",
            "## 文档章节",
            "",
            *(f"- {heading}" for heading in headings),
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="刷新 PTrade API 离线 Markdown 参考")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references",
    )
    args = parser.parse_args()

    markdown, headings = render_reference(fetch_html(args.url), args.url)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "api-reference.md").write_text(markdown, encoding="utf-8")
    (args.output_dir / "api-index.md").write_text(render_index(args.url, headings), encoding="utf-8")
    print(f"已写入 {args.output_dir}，共 {len(headings)} 个章节。")


if __name__ == "__main__":
    main()
