"""排位戰績區塊。

實測此帳號 6 種佇列全部 0 勝 0 敗——未打排位是常態，不是例外。因此
空狀態是這個區塊的主要設計考量，而非邊角情況。
"""

from ..theme import esc

KEY = "ranked"
TITLE = "排位戰績"

NAV_LABEL = "排位"

PATH = "/lol-ranked/v1/current-ranked-stats"

_QUEUES = {
    "RANKED_SOLO_5x5": "單／雙排",
    "RANKED_FLEX_SR": "彈性積分",
    "RANKED_PREMADE_5x5": "組隊排位（舊制）",
    "RANKED_TFT": "聯盟戰棋",
    "RANKED_TFT_DOUBLE_UP": "戰棋雙人",
    "RANKED_TFT_TURBO": "超級戰棋",
}


def fetch(client) -> list[dict] | None:
    # 不要 try/except——例外由 sections.safe_fetch 統一攔截
    raw = client.get_json(PATH)
    qmap = (raw or {}).get("queueMap") or {}
    out = []
    for key, v in qmap.items():
        wins = int(v.get("wins") or 0)
        losses = int(v.get("losses") or 0)
        if wins + losses == 0:
            continue
        out.append(
            {
                "queue": _QUEUES.get(key, key),
                "tier": v.get("tier") or "",
                "division": v.get("division") or "",
                "lp": int(v.get("leaguePoints") or 0),
                "wins": wins,
                "losses": losses,
                "winrate": round(wins / (wins + losses) * 100),
            }
        )
    return out or None


def to_dict(data: list[dict] | None) -> dict | None:
    if not data:
        return None
    return {"queues": data}


def empty_html() -> str:
    """排位為空時顯示的說明。空是常態，不該讓區塊整段消失。"""
    return f"""<div class="wrap">
<section class="block">
<h2 class="block-h">{esc(TITLE)}</h2>
<p class="note">本賽季尚無排位紀錄。</p>
</section></div>"""


def to_html(data: list[dict] | None) -> str:
    if not data:
        return ""
    cards = "".join(
        f'<div class="rank">'
        f'<div class="rank-q">{esc(r["queue"])}</div>'
        f'<div class="rank-t num">{esc(r["tier"])} {esc(r["division"])}'
        f' <span class="rank-lp">{r["lp"]} LP</span></div>'
        f'<div class="rank-w num">{r["wins"]}勝 {r["losses"]}敗 · {r["winrate"]}%</div>'
        f"</div>"
        for r in data
    )
    return f"""<div class="wrap">
<section class="block">
<h2 class="block-h">{esc(TITLE)}</h2>
<div class="ranks">{cards}</div>
</section></div>"""
