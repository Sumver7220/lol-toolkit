"""把 LCU 回傳的扁平造型清單整理成結構化模型。

純函式：不碰網路、不碰檔案系統。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Skin:
    id: int
    name: str
    champion_id: int
    has_chromas: bool
    tile_path: str


@dataclass(frozen=True)
class Champion:
    champion_id: int
    name: str
    skins: tuple[Skin, ...]


@dataclass(frozen=True)
class Inventory:
    summoner_name: str
    summoner_id: int
    champions: tuple[Champion, ...]

    @property
    def champion_count(self) -> int:
        return len(self.champions)

    @property
    def skin_count(self) -> int:
        """已擁有的造型數，不含基礎造型。"""
        return sum(len(c.skins) for c in self.champions)


def _is_owned(raw: dict) -> bool:
    return bool(raw.get("ownership", {}).get("owned", False))


def build_inventory(
    skins_list: list[dict], summoner_name: str, summoner_id: int
) -> Inventory:
    """整理造型清單。

    分兩輪處理而非一輪：第一輪從基礎造型建立 championId → 英雄名的
    對照，第二輪才歸類其餘造型。這樣就不依賴 API 的回傳順序——雖然
    實測 LCU 確實是基礎造型排在前面，但這個假設沒有任何保證。

    championId 在不同筆之間可能是 int 或 str，一律轉成 str 當索引。
    """
    owned = [s for s in skins_list if _is_owned(s)]

    champion_names: dict[str, str] = {}
    champion_ids: dict[str, int] = {}
    for raw in owned:
        if raw.get("isBase", False):
            key = str(raw.get("championId"))
            champion_names[key] = raw.get("name")
            champion_ids[key] = int(raw.get("championId"))

    grouped: dict[str, list[Skin]] = {key: [] for key in champion_names}
    for raw in owned:
        if raw.get("isBase", False):
            continue
        key = str(raw.get("championId"))
        if key not in grouped:
            continue
        grouped[key].append(
            Skin(
                id=int(raw.get("id")),
                name=raw.get("name"),
                champion_id=champion_ids[key],
                has_chromas=bool(raw.get("chromaPath")),
                tile_path=raw.get("tilePath") or "",
            )
        )

    champions = tuple(
        sorted(
            (
                Champion(
                    champion_id=champion_ids[key],
                    name=champion_names[key],
                    skins=tuple(sorted(skins, key=lambda s: s.id)),
                )
                for key, skins in grouped.items()
            ),
            key=lambda c: c.name,
        )
    )

    return Inventory(
        summoner_name=summoner_name, summoner_id=summoner_id, champions=champions
    )
