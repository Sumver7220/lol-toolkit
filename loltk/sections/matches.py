"""對戰紀錄區塊。

客戶端可取得最近 20 場對戰。gameMode 回傳內部代號（例如 KIWI），
不可直接顯示給使用者；應改用 queueId（優先）與 mapId（後備）推導
人類可讀的中文標籤。
"""

from ..theme import esc

KEY = "matches"
TITLE = "最近對戰"

LIMIT_NOTE = "客戶端不保留完整歷史，僅能取得最近的對戰"

# 佇列 ID → 中文名稱。已驗證者列入；未驗證者不要猜測。
_QUEUE_NAMES = {
    400: "一般（選角）",
    430: "一般（隨機）",
    420: "單／雙排",
    440: "彈性積分",
    450: "大亂鬥",
    830: "人機",
    840: "人機",
    850: "人機",
    1700: "鬥魂競技場",
    1900: "極限閃電戰",
}

# 地圖 ID → 中文名稱。
_MAP_NAMES = {
    11: "召喚師峽谷",
    12: "嚎哭深淵",
    30: "鬥魂競技場",
}


def _get_mode_label(queue_id: int | None, map_id: int | None) -> str:
    """推導對戰模式的人類可讀中文標籤。

    優先順序：
    1. queueId → 佇列名稱
    2. mapId → 地圖名稱（queueId 未知時）
    3. 「其他模式」（兩者都未知）

    絕不回傳原始 gameMode 內部代號如 KIWI。
    """
    if queue_id in _QUEUE_NAMES:
        return _QUEUE_NAMES[queue_id]
    if map_id in _MAP_NAMES:
        return _MAP_NAMES[map_id]
    return "其他模式"


def _fmt_duration(seconds: int) -> str:
    m, s = divmod(max(0, int(seconds or 0)), 60)
    return f"{m}:{s:02d}"


def _my_stats(game: dict, puuid: str) -> dict:
    """從對戰紀錄找出「我」的那筆 stats。

    participants 陣列的順序不保證是自己在前——必須先用 puuid 在
    participantIdentities 找出自己的 participantId，再拿它去
    participants 對應正確的那筆，否則多人陣列會顯示到別人的 KDA。
    找不到對應時（例如缺 participantIdentities）退回第一筆，維持
    不崩潰，但這只是保底而非預期路徑。
    """
    parts = game.get("participants") or []
    identities = game.get("participantIdentities") or []
    my_pid = None
    for identity in identities:
        player = identity.get("player") or {}
        if player.get("puuid") == puuid:
            my_pid = identity.get("participantId")
            break
    if my_pid is not None:
        for p in parts:
            if p.get("participantId") == my_pid:
                return p.get("stats") or {}
    return (parts[0].get("stats") if parts else {}) or {}


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
        stats = _my_stats(g, puuid)
        queue_id = g.get("queueId")
        map_id = g.get("mapId")
        mode_label = _get_mode_label(queue_id, map_id)
        out.append(
            {
                "mode_label": mode_label,
                "gameMode": g.get("gameMode") or "",
                "queueId": queue_id,
                "mapId": map_id,
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
        f'<span class="ev-m">{esc(g["mode_label"])}</span>'
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
