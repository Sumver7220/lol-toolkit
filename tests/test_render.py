import json
from datetime import datetime, timezone, timedelta

from loltk.skins import render
from loltk.skins.inventory import Champion, Inventory, Skin

TAIPEI = timezone(timedelta(hours=8))
AT = datetime(2026, 7, 26, 14, 30, 0, tzinfo=TAIPEI)


def sample_inventory():
    skin = Skin(
        id=1002,
        name="小紅帽 安妮",
        champion_id=1,
        has_chromas=True,
        tile_path="/lol-game-data/assets/ASSETS/Characters/Annie/Skins/Skin02/Images/annie_splash_tile_2.jpg",
    )
    return Inventory(
        summoner_name="SumverMizz",
        summoner_id=3112301784908896,
        champions=(Champion(champion_id=1, name="安妮", skins=(skin,)),),
    )


def test_cdn_url_lowercases_and_strips_lcu_prefix():
    path = "/lol-game-data/assets/ASSETS/Characters/Annie/Skins/Skin02/Images/annie_splash_tile_2.jpg"
    assert render.cdn_url(path) == (
        "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/"
        "global/default/assets/characters/annie/skins/skin02/images/annie_splash_tile_2.jpg"
    )


def test_cdn_url_returns_empty_string_for_empty_path():
    assert render.cdn_url("") == ""


def test_cdn_url_with_path_not_starting_with_prefix():
    """非標準路徑不以 /lol-game-data/assets 開頭，仍應附加到 CDN_BASE。"""
    path = "/assets/characters/annie/skins/skin02/images/tile.jpg"
    assert render.cdn_url(path) == (
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
    result = render.cdn_url(path)
    # 只有開頭的應該被移除
    assert result == (
        "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/"
        "global/default/data/lol-game-data/assets/file.jpg"
    )


def test_json_has_expected_top_level_shape():
    data = json.loads(render.to_json(sample_inventory(), AT))
    assert data["schemaVersion"] == render.SCHEMA_VERSION
    assert data["generatedAt"] == "2026-07-26T14:30:00+08:00"
    assert data["account"] == {
        "summonerName": "SumverMizz",
        "summonerId": 3112301784908896,
    }
    assert data["summary"] == {"champions": 1, "skins": 1}


def test_json_champion_and_skin_fields():
    data = json.loads(render.to_json(sample_inventory(), AT))
    champion = data["champions"][0]
    assert champion["championId"] == 1
    assert champion["name"] == "安妮"
    skin = champion["skins"][0]
    assert skin["id"] == 1002
    assert skin["name"] == "小紅帽 安妮"
    assert skin["hasChromas"] is True
    assert skin["tileUrl"].startswith("https://raw.communitydragon.org/")
    assert skin["tileUrl"].endswith("annie_splash_tile_2.jpg")


def test_json_is_human_readable_and_keeps_chinese():
    text = render.to_json(sample_inventory(), AT)
    assert "小紅帽 安妮" in text
    assert "\\u" not in text
    assert "\n" in text


def test_html_is_self_contained_document():
    html = render.to_html(sample_inventory(), AT)
    assert html.startswith("<!DOCTYPE html>")
    assert "<html" in html and "</html>" in html
    # 不得引用任何外部函式庫或字型
    assert "cdn.jsdelivr" not in html
    assert "fonts.googleapis" not in html
    assert "<script src=" not in html


def test_html_shows_account_and_summary():
    html = render.to_html(sample_inventory(), AT)
    assert "SumverMizz" in html
    assert "安妮" in html
    assert "小紅帽 安妮" in html


def test_html_lazy_loads_images_with_fallback():
    html = render.to_html(sample_inventory(), AT)
    assert 'loading="lazy"' in html
    assert "onerror" in html


def test_html_escapes_special_characters():
    """帳號名與造型名來自 API，含尖括號時不得破壞版面。"""
    evil = Inventory(
        summoner_name='<script>alert("x")</script>',
        summoner_id=1,
        champions=(
            Champion(
                champion_id=1,
                name="A & B",
                skins=(
                    Skin(
                        id=1,
                        name='"><img onerror=alert(1)>',
                        champion_id=1,
                        has_chromas=False,
                        tile_path="/t.jpg",
                    ),
                ),
            ),
        ),
    )
    html = render.to_html(evil, AT)
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
    assert "A &amp; B" in html
    assert "<img onerror=alert(1)>" not in html


def test_html_handles_empty_inventory():
    empty = Inventory(summoner_name="Nobody", summoner_id=0, champions=())
    html = render.to_html(empty, AT)
    assert "<!DOCTYPE html>" in html
    assert "Nobody" in html


def test_html_champion_without_skins_still_renders():
    inv = Inventory(
        summoner_name="T",
        summoner_id=1,
        champions=(Champion(champion_id=268, name="阿祈爾", skins=()),),
    )
    html = render.to_html(inv, AT)
    assert "阿祈爾" in html
