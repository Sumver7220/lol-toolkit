"""摘要數字帶：等級、榮譽、貨幣。

三個 endpoint 各自獨立擷取。任一個失敗或欄位對不上，只讓該格不顯示，
不影響其他格或整頁產生——摘要是加分項，造型收藏才是主體。

缺值一律為 None 而非 0：0 會被讀成「真的是零」。
"""

from ..page import Figure

WALLET_PATH = (
    "/lol-inventory/v1/wallet"
    '?currencyTypes=["RP","lol_blue_essence","lol_orange_essence"]'
)

KEY = "summary"
TITLE = "摘要"


def _get(client, path, *fields):
    """取一個 endpoint 並抽出指定欄位；任何失敗都回傳同長度的 None。"""
    try:
        data = client.get_json(path)
        if not isinstance(data, dict):
            return (None,) * len(fields)
        return tuple(data.get(f) for f in fields)
    except Exception:
        return (None,) * len(fields)


def fetch(client) -> dict:
    (level,) = _get(client, "/lol-summoner/v1/current-summoner", "summonerLevel")
    (honor,) = _get(client, "/lol-honor-v2/v1/profile", "honorLevel")
    rp, blue, orange = _get(
        client, WALLET_PATH, "RP", "lol_blue_essence", "lol_orange_essence"
    )
    return {
        "level": level,
        "honor": honor,
        "rp": rp,
        "blue_essence": blue,
        "orange_essence": orange,
    }


def to_dict(data: dict | None) -> dict | None:
    if not data:
        return None
    kept = {k: v for k, v in data.items() if v is not None}
    return kept or None


_LABELS = (
    ("level", "等級"),
    ("honor", "榮譽"),
    ("blue_essence", "藍色精華"),
    ("orange_essence", "橘色精華"),
    ("rp", "RP"),
)


def figures(data: dict | None) -> list[Figure]:
    """轉成摘要數字帶的格子。缺值的格子整格不輸出。"""
    if not data:
        return []
    out = []
    for key, label in _LABELS:
        value = data.get(key)
        if value is None:
            continue
        out.append(Figure(f"{value:,}" if isinstance(value, int) else str(value), label))
    return out


def to_html(data) -> str:
    """摘要不是獨立區塊，它透過 figures() 併入海報卡。"""
    return ""
