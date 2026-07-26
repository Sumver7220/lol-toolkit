"""把 Inventory 轉成 JSON 與 HTML 字串。

純函式：只回傳字串，不負責寫檔。
"""

import html as html_lib
import json
from datetime import datetime

from .inventory import Inventory

SCHEMA_VERSION = 1

CDN_BASE = (
    "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default"
)


def cdn_url(lcu_asset_path: str) -> str:
    """把 LCU 的本機資產路徑轉成 Community Dragon 的公開網址。

    LCU 的圖片需要認證才能取得，直接寫進 HTML 沒有意義。Community
    Dragon 提供同一批資產的公開鏡像，路徑規則是全小寫並去掉
    /lol-game-data/assets 前綴。

    注意這個網址無法從 championId 與 skinId 推導——
    /v1/champion-tiles/{championId}/{skinId}.jpg 實測為 404。
    """
    if not lcu_asset_path:
        return ""
    return CDN_BASE + lcu_asset_path.lower().removeprefix("/lol-game-data/assets")


def to_dict(inventory: Inventory, generated_at: datetime) -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at.isoformat(),
        "account": {
            "summonerName": inventory.summoner_name,
            "summonerId": inventory.summoner_id,
        },
        "summary": {
            "champions": inventory.champion_count,
            "skins": inventory.skin_count,
        },
        "champions": [
            {
                "championId": champion.champion_id,
                "name": champion.name,
                "skins": [
                    {
                        "id": skin.id,
                        "name": skin.name,
                        "hasChromas": skin.has_chromas,
                        "tileUrl": cdn_url(skin.tile_path),
                    }
                    for skin in champion.skins
                ],
            }
            for champion in inventory.champions
        ],
    }


def to_json(inventory: Inventory, generated_at: datetime) -> str:
    return json.dumps(
        to_dict(inventory, generated_at), ensure_ascii=False, indent=2
    )


_STYLE = """
:root {
  --bg: #f5f6f8; --card: #ffffff; --text: #16181d; --muted: #6b7280;
  --border: #e3e5ea; --accent: #0a7c6b;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #101216; --card: #191c22; --text: #e8eaee; --muted: #9aa1ad;
    --border: #262a33; --accent: #3ddbc0;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2rem 1.25rem 4rem; background: var(--bg); color: var(--text);
  font-family: "Segoe UI", "Microsoft JhengHei", system-ui, sans-serif;
  line-height: 1.5;
}
.wrap { max-width: 1200px; margin: 0 auto; }
header { margin-bottom: 1.5rem; }
h1 { margin: 0 0 .35rem; font-size: 1.6rem; letter-spacing: .01em; }
.meta { color: var(--muted); font-size: .9rem; }
.stats { display: flex; gap: 2rem; margin: 1.25rem 0; flex-wrap: wrap; }
.stat-value { font-size: 1.9rem; font-weight: 650; color: var(--accent); }
.stat-label { color: var(--muted); font-size: .82rem; }
#search {
  width: 100%; padding: .7rem .9rem; margin-bottom: 1.75rem; font-size: 1rem;
  border: 1px solid var(--border); border-radius: 9px;
  background: var(--card); color: var(--text);
}
#search:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.champion {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 1rem 1.1rem; margin-bottom: 1rem;
}
.champion h2 { margin: 0 0 .75rem; font-size: 1.05rem; }
.champion h2 span { color: var(--muted); font-weight: 400; font-size: .85rem; }
.skins { display: grid; gap: .75rem;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
.skin { border: 1px solid var(--border); border-radius: 9px; overflow: hidden;
  background: var(--bg); }
.skin img { width: 100%; aspect-ratio: 308/560; object-fit: cover; display: block; }
.skin .name { padding: .45rem .55rem; font-size: .8rem; }
.chroma { color: var(--accent); }
.empty { color: var(--muted); font-size: .85rem; }
#no-result { display: none; color: var(--muted); padding: 2rem 0; }
"""

_SCRIPT = """
const box = document.getElementById('search');
const cards = Array.from(document.querySelectorAll('.champion'));
const none = document.getElementById('no-result');
box.addEventListener('input', () => {
  const q = box.value.trim().toLowerCase();
  let shown = 0;
  for (const card of cards) {
    const hit = !q || card.dataset.search.includes(q);
    card.style.display = hit ? '' : 'none';
    if (hit) shown++;
  }
  none.style.display = shown ? 'none' : 'block';
});
"""


def _esc(value) -> str:
    return html_lib.escape(str(value), quote=True)


def _skin_card(skin) -> str:
    url = cdn_url(skin.tile_path)
    chroma = ' <span class="chroma" title="此造型有炫彩">◆</span>' if skin.has_chromas else ""
    img = (
        f'<img src="{_esc(url)}" alt="{_esc(skin.name)}" loading="lazy" '
        f'onerror="this.remove()">'
        if url
        else ""
    )
    return (
        f'<div class="skin">{img}'
        f'<div class="name">{_esc(skin.name)}{chroma}</div></div>'
    )


def _champion_card(champion) -> str:
    if champion.skins:
        body = '<div class="skins">' + "".join(
            _skin_card(s) for s in champion.skins
        ) + "</div>"
    else:
        body = '<p class="empty">尚未擁有其他造型</p>'
    haystack = _esc(
        " ".join([champion.name] + [s.name for s in champion.skins]).lower()
    )
    count = len(champion.skins)
    return (
        f'<section class="champion" data-search="{haystack}">'
        f"<h2>{_esc(champion.name)} <span>{count} 個造型</span></h2>"
        f"{body}</section>"
    )


def to_html(inventory: Inventory, generated_at: datetime) -> str:
    """產生單一自包含的 HTML 頁面。

    圖片連向 Community Dragon 而非內嵌：實測 486 張 tile 內嵌後 HTML
    會膨脹到 29 MB，沒有人想收這種檔案。代價是檢視時需要網路，因此
    圖片載入失敗時直接移除 img，退化成純文字卡片而不是破圖。
    """
    cards = "".join(_champion_card(c) for c in inventory.champions)
    stamp = generated_at.strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(inventory.summoner_name)} 的造型收藏</title>
<style>{_STYLE}</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>{_esc(inventory.summoner_name)} 的造型收藏</h1>
  <div class="meta">產生時間 {_esc(stamp)}</div>
</header>
<div class="stats">
  <div><div class="stat-value">{inventory.champion_count}</div>
       <div class="stat-label">已擁有英雄</div></div>
  <div><div class="stat-value">{inventory.skin_count}</div>
       <div class="stat-label">已擁有造型</div></div>
</div>
<input id="search" type="search" placeholder="搜尋英雄或造型名稱…"
       autocomplete="off">
<div id="no-result">找不到符合的英雄或造型。</div>
{cards}
</div>
<script>{_SCRIPT}</script>
</body>
</html>
"""
