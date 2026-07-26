"""造型碎片區塊。

戰利品 endpoint 回傳所有類型（寶箱、鑰匙、永恆等），這裡只取造型碎片
——它與造型收藏是同一件事，且碎片的 tilePath 格式與造型完全相同，
可直接沿用同一套 CDN 推導與圖像網格。
"""

from ..skins.render import cdn_url
from ..theme import esc
from ._tile import tile

KEY = "loot"
TITLE = "造型碎片"

LOOT_PATH = "/lol-loot/v1/player-loot"


def fetch(client) -> list[dict] | None:
    """取得造型碎片清單。

    過濾戰利品中的造型碎片（displayCategories == "SKIN"），
    並依分解價值降序排列。
    """
    # 不要 try/except——例外由 sections.safe_fetch 統一攔截
    raw = client.get_json(LOOT_PATH)
    if not isinstance(raw, list):
        return None
    shards = [
        {
            "name": x.get("itemDesc") or "未知造型",
            "count": int(x.get("count") or 0),
            "value": int(x.get("disenchantValue") or 0),
            "rarity": x.get("rarity") or "",  # 僅進 JSON，不進 HTML
            "tile_path": x.get("tilePath") or "",
        }
        for x in raw
        if x.get("displayCategories") == "SKIN"
    ]
    if not shards:
        return None
    shards.sort(key=lambda s: s["value"], reverse=True)
    return shards


def to_dict(data: list[dict] | None) -> dict | None:
    """轉換為字典格式。

    計算碎片總數與可分解的橘色精華總量。
    """
    if not data:
        return None
    return {
        "count": sum(s["count"] for s in data),
        "disenchantTotal": sum(s["count"] * s["value"] for s in data),
        "shards": [
            {
                "name": s["name"],
                "count": s["count"],
                "disenchantValue": s["value"],
                "rarity": s["rarity"],
                "tileUrl": cdn_url(s["tile_path"]),
            }
            for s in data
        ],
    }


def to_html(data: list[dict] | None) -> str:
    """轉換為 HTML。

    顯示造型碎片網格，標示重複數量與橘色精華總量。
    """
    if not data:
        return ""
    total = sum(s["count"] for s in data)
    value = sum(s["count"] * s["value"] for s in data)
    tiles = "".join(
        tile(
            name=s["name"],
            sub=f"×{s['count']}" if s["count"] > 1 else "",
            tile_path=s["tile_path"],
        )
        for s in data
    )
    return f"""<div class="wrap">
<section class="block">
<h2 class="block-h">{esc(TITLE)} <span class="sub">{total:,} 個 · 分解可得 {value:,} 橘色精華</span></h2>
<div class="wall">{tiles}</div>
</section></div>"""
