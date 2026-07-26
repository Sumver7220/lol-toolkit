"""挑戰進度區塊。

五個分類各有等級與 current/max。這是「進度指標」版面模式的第一個使用者。
"""

from ..theme import esc

KEY = "challenges"
TITLE = "挑戰進度"

NAV_LABEL = "挑戰"

PATH = "/lol-challenges/v1/summary-player-data/local-player"

_NAMES = {
    "COLLECTION": "收藏",
    "TEAMWORK": "團隊合作",
    "EXPERTISE": "精通",
    "VETERANCY": "資歷",
    "IMAGINATION": "想像力",
}


def fetch(client) -> list[dict] | None:
    # 不要 try/except——例外由 sections.safe_fetch 統一攔截
    raw = client.get_json(PATH)
    cats = (raw or {}).get("categoryProgress") or []
    out = []
    for c in cats:
        current = int(c.get("current") or 0)
        maximum = int(c.get("max") or 0)
        percent = min(100, round(current / maximum * 100)) if maximum else 0
        key = c.get("category") or ""
        out.append(
            {
                "key": key,
                "name": _NAMES.get(key, key),
                "current": current,
                "max": maximum,
                "percent": percent,
                "level": c.get("level") or "",
            }
        )
    return out or None


def to_dict(data: list[dict] | None) -> dict | None:
    if not data:
        return None
    return {"categories": data}


def to_html(data: list[dict] | None) -> str:
    if not data:
        return ""
    rows = "".join(
        f'<div class="prog">'
        f'<div class="prog-h"><span class="prog-n">{esc(c["name"])}</span>'
        f'<span class="prog-lv num">{esc(c["level"])}</span></div>'
        f'<div class="prog-bar"><i style="width:{c["percent"]}%"></i></div>'
        f'<div class="prog-v num">{c["current"]:,} / {c["max"]:,}</div>'
        f"</div>"
        for c in data
    )
    return f"""<div class="wrap">
<section class="block">
<h2 class="block-h">{esc(TITLE)}</h2>
<div class="progs">{rows}</div>
</section></div>"""
