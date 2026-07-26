from loltk import assets


def test_cdn_url_lowercases_and_strips_lcu_prefix():
    path = "/lol-game-data/assets/ASSETS/Characters/Annie/Skins/Skin02/Images/annie_splash_tile_2.jpg"
    assert assets.cdn_url(path) == (
        "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/"
        "global/default/assets/characters/annie/skins/skin02/images/annie_splash_tile_2.jpg"
    )


def test_cdn_url_returns_empty_string_for_empty_path():
    assert assets.cdn_url("") == ""


def test_cdn_url_with_path_not_starting_with_prefix():
    """非標準路徑不以 /lol-game-data/assets 開頭，仍應附加到 CDN_BASE。"""
    path = "/assets/characters/annie/skins/skin02/images/tile.jpg"
    assert assets.cdn_url(path) == (
        "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/"
        "global/default/assets/characters/annie/skins/skin02/images/tile.jpg"
    )


def test_cdn_url_removes_only_leading_prefix_not_all_occurrences():
    """前綴移除應只針對開頭，即使字串在路徑中再次出現也不受影響。

    測試 anchored 行為：/lol-game-data/assets 在路徑開頭被移除，
    但如果在路徑後面再出現也應保留。
    """
    # 構造一個路徑，/lol-game-data/assets 在開頭和中間都出現
    path = "/lol-game-data/assets/data/lol-game-data/assets/file.jpg"
    result = assets.cdn_url(path)
    # 只有開頭的應該被移除
    assert result == (
        "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/"
        "global/default/data/lol-game-data/assets/file.jpg"
    )
