"""頁面外殼：把各功能區塊組裝成一份自包含的 HTML。

只認識區塊契約（Block：key／title／count／html），不認識任何區塊的內容。
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


@dataclass(frozen=True)
class Block:
    """頁面上的一個區塊。

    page 只認識這個契約，不認識任何區塊的內容——html 是區塊模組
    自己產生的片段，這裡只負責包外殼與產生導覽列。
    """

    key: str          # 錨點 id 取自這裡：sec-{key}
    title: str        # 導覽列顯示的短標籤
    count: str | None  # 已格式化的計數（含千分位）；None 表示不顯示數字
    html: str


def _nav_html(blocks: list[Block]) -> str:
    """區塊數少於兩個時不輸出——一個項目的導覽沒有意義。"""
    if len(blocks) < 2:
        return ""
    items = "".join(
        f'<a class="nv" href="#sec-{esc(b.key)}">{esc(b.title)}'
        + (f'<b class="num">{esc(b.count)}</b>' if b.count else "")
        + "</a>"
        for b in blocks
    )
    return (
        f'<nav class="nav" aria-label="區塊導覽">'
        f'<div class="wrap">{items}</div></nav>'
    )


def render_page(
    *,
    summoner_name: str,
    generated_at: datetime,
    figures: list[Figure],
    blocks: list[Block],
    total_tiles: int,
) -> str:
    """組裝完整頁面。blocks 依序排列，每個包進自己的錨點外殼。"""
    stamp = generated_at.strftime("%Y-%m-%d %H:%M")
    shown = [b for b in blocks if b.html]
    nav = _nav_html(shown)
    body = "\n".join(
        f'<section class="anchor" id="sec-{esc(b.key)}">{b.html}</section>'
        for b in shown
    )
    script = SCRIPT.replace("__TOTAL__", str(total_tiles))
    # 只有輸出導覽列時才給 body 掛 has-nav：--nav-h 靠這個 class 歸零，
    # 見 theme.STYLE 的 body:not(.has-nav) 規則。
    body_class = ' class="has-nav"' if nav else ""
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(summoner_name)} 的收藏</title>
<style>{STYLE}</style>
</head>
<body{body_class}>
<div class="wrap"><header class="poster">
<div class="eyebrow">League of Legends · 個人收藏</div>
<h1 class="who">{esc(summoner_name)}</h1>
<div class="when">產生於 {esc(stamp)}</div>
<div class="hr"></div>
{_figures_html(figures)}
</header></div>
{nav}
{body}
<div class="wrap"><footer>lol-toolkit · 唯讀 · 不含他人資料</footer></div>
<script>{script}</script>
</body>
</html>
"""
