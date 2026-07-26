"""對戰紀錄區塊。

實測 gameCount 為 10——客戶端**不保留完整歷史**，只有最近幾場。這個
限制必須顯示在頁面上，否則使用者會以為自己只打過 10 場。
"""

from ..theme import esc

KEY = "matches"
TITLE = "最近對戰"

LIMIT_NOTE = "客戶端不保留完整歷史，僅能取得最近的對戰"


def _fmt_duration(seconds: int) -> str:
    m, s = divmod(max(0, int(seconds or 0)), 60)
    return f"{m}:{s:02d}"


def fetch(client) -> list[dict] | None:
    # 不要 try/except——例外由 sections.safe_fetch 統一攔截
    me = client.get_json("/lol-summoner/v1/current-summoner")
    puuid = (me or {}).get("puuid")
    if not puuid:
        return None
    raw = client.get_json(
        f"/lol-match-history/v1/products/lol/{puuid}/matches?begIndex=0&endIndex=19"
    )
    games = ((raw or {}).get("games") or {}).get("games") or []
    out = []
    for g in games:
        parts = g.get("participants") or []
        stats = (parts[0].get("stats") if parts else {}) or {}
        out.append(
            {
                "mode": g.get("gameMode") or "",
                "win": bool(stats.get("win")),
                "kda": f"{stats.get('kills', 0)}/{stats.get('deaths', 0)}/"
                       f"{stats.get('assists', 0)}",
                "duration": _fmt_duration(g.get("gameDuration")),
                "date": (g.get("gameCreationDate") or "")[:10],
            }
        )
    return out or None


def to_dict(data: list[dict] | None) -> dict | None:
    if not data:
        return None
    return {"note": LIMIT_NOTE, "games": data}


def to_html(data: list[dict] | None) -> str:
    if not data:
        return ""
    rows = "".join(
        f'<li class="ev {"win" if g["win"] else "loss"}">'
        f'<span class="ev-r">{"勝" if g["win"] else "敗"}</span>'
        f'<span class="ev-m">{esc(g["mode"])}</span>'
        f'<span class="ev-k num">{esc(g["kda"])}</span>'
        f'<span class="ev-d num">{esc(g["duration"])}</span>'
        f'<span class="ev-t num">{esc(g["date"])}</span></li>'
        for g in data
    )
    return f"""<div class="wrap">
<section class="block">
<h2 class="block-h">{esc(TITLE)} <span class="sub">{esc(LIMIT_NOTE)}</span></h2>
<ol class="events">{rows}</ol>
</section></div>"""
