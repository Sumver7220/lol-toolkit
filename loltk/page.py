"""頁面外殼：把各功能區塊組裝成一份自包含的 HTML。

只認識區塊契約（一段 HTML 字串），不認識任何區塊的內容。
"""

from dataclasses import dataclass
from datetime import datetime

from .theme import SCRIPT, STYLE, esc


@dataclass(frozen=True)
class Figure:
    """摘要數字帶的一格。value 已格式化為字串（含千分位）。"""

    value: str
    label: str
    lead: bool = False


def _figures_html(figures: list[Figure]) -> str:
    if not figures:
        return ""
    cells = "".join(
        f'<div class="fig{" lead" if f.lead else ""}">'
        f'<div class="n">{esc(f.value)}</div>'
        f'<div class="l">{esc(f.label)}</div></div>'
        for f in figures
    )
    return f'<div class="figures">{cells}</div>'


def render_page(
    *,
    summoner_name: str,
    generated_at: datetime,
    figures: list[Figure],
    sections: list[str],
    total_tiles: int,
) -> str:
    """組裝完整頁面。sections 為各區塊已產生的 HTML 片段，依序排列。"""
    stamp = generated_at.strftime("%Y-%m-%d %H:%M")
    body = "\n".join(s for s in sections if s)
    script = SCRIPT.replace("__TOTAL__", str(total_tiles))
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(summoner_name)} 的收藏</title>
<style>{STYLE}</style>
</head>
<body>
<div class="wrap"><header class="poster">
<div class="eyebrow">League of Legends · 個人收藏</div>
<h1 class="who">{esc(summoner_name)}</h1>
<div class="when">產生於 {esc(stamp)}</div>
<div class="hr"></div>
{_figures_html(figures)}
</header></div>
{body}
<div class="wrap"><footer>lol-toolkit · 唯讀 · 不含他人資料</footer></div>
<script>{script}</script>
</body>
</html>
"""
