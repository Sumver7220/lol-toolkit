"""把 Inventory 轉成 JSON 字串，並推導圖片的公開 CDN 網址。

純函式：只回傳字串，不負責寫檔。HTML 產生已移至 loltk/sections/skins.py。
"""

import json
from datetime import datetime

from .inventory import Inventory

SCHEMA_VERSION = 2

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


def champion_dicts(inventory: Inventory) -> list[dict]:
    """英雄與造型的清單。to_dict 與 sections.skins.to_dict 共用這一份。"""
    return [
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
    ]


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
        "champions": champion_dicts(inventory),
    }


def to_json(inventory: Inventory, generated_at: datetime) -> str:
    return json.dumps(
        to_dict(inventory, generated_at), ensure_ascii=False, indent=2
    )
