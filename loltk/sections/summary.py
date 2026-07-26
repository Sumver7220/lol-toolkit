"""摘要數字帶：等級、榮譽、貨幣、帳號名稱。

三個 endpoint 各自獨立擷取。任一個失敗或欄位對不上，只讓該格不顯示，
不影響其他格或整頁產生——摘要是加分項，造型收藏才是主體。

缺值一律為 None 而非 0：0 會被讀成「真的是零」。

逐欄位容錯（本模組）與逐區塊容錯（sections.safe_fetch）是不同層次，
故意都保留；但失敗仍必須回報，否則會出現「安靜」的例外邊界——見
fetch() 回傳的 errors。
"""

from ..page import Figure

WALLET_PATH = (
    "/lol-inventory/v1/wallet"
    '?currencyTypes=["RP","lol_blue_essence","lol_orange_essence"]'
)
CURRENT_SUMMONER_PATH = "/lol-summoner/v1/current-summoner"
HONOR_PATH = "/lol-honor-v2/v1/profile"

KEY = "summary"
TITLE = "摘要"


def _get(client, path, *fields):
    """取一個 endpoint 並抽出指定欄位。

    回傳 (values, error)：成功時 error 為 None；任何失敗都讓 values
    整組回傳同長度的 None，但 error 帶著失敗原因——呼叫端必須把它併入
    skipped，否則會出現沒有任何紀錄的靜默失敗。
    """
    try:
        data = client.get_json(path)
        if not isinstance(data, dict):
            return (None,) * len(fields), f"{path} 回傳非預期格式"
        return tuple(data.get(f) for f in fields), None
    except Exception as exc:
        return (None,) * len(fields), f"{type(exc).__name__}: {exc}"


def fetch(client) -> tuple[dict, list[str]]:
    """取得摘要資料，回傳 (data, errors)。

    errors 為失敗的 endpoint 訊息清單，由 cli.build_report 併入
    整體的 skipped 清單。

    data 除了摘要數字，也帶出帳號名稱（account_name）與帳號 ID
    （account_id）——current-summoner 這次呼叫本來就有這兩個欄位，
    讓非 skins 子命令也能有正確的帳號名稱可用，不必再多打一次 API。
    實測帳號 displayName 為空字串、gameName 才有值，因此以 gameName
    優先，displayName 作為備援。
    """
    errors = []

    (level, display_name, game_name, account_id), err = _get(
        client, CURRENT_SUMMONER_PATH, "summonerLevel", "displayName", "gameName", "summonerId"
    )
    if err:
        errors.append(err)

    (honor,), err = _get(client, HONOR_PATH, "honorLevel")
    if err:
        errors.append(err)

    (rp, blue, orange), err = _get(
        client, WALLET_PATH, "RP", "lol_blue_essence", "lol_orange_essence"
    )
    if err:
        errors.append(err)

    return {
        "level": level,
        "honor": honor,
        "rp": rp,
        "blue_essence": blue,
        "orange_essence": orange,
        "account_name": game_name or display_name or None,
        "account_id": account_id,
    }, errors


def to_dict(data: dict | None) -> dict | None:
    """轉成 JSON 用字典。account_name／account_id 只供 cli 組頁首用，
    不進摘要區塊的 JSON（會與頂層 account key 重複）。"""
    if not data:
        return None
    kept = {
        k: v
        for k, v in data.items()
        if v is not None and k not in ("account_name", "account_id")
    }
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
