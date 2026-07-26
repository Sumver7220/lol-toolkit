"""推導圖片的公開 CDN 網址。

不只造型用得到——戰利品碎片、日後任何圖像網格都靠這份 CDN 推導。
純函式：只回傳字串，不負責寫檔。
"""

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
