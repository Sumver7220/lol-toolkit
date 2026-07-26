"""導覽列所需的區塊中繼資料。

短標籤與 TITLE 分開：「造型收藏」在 390px 螢幕的導覽列太長。
計數是選配的——挑戰與排位沒有有意義的單一數字，不硬湊。
"""

from loltk.inventory import Champion, Inventory, Skin
from loltk.sections import challenges, loot, matches, ranked
from loltk.sections import skins as skins_section


def test_every_section_has_a_short_nav_label():
    labels = {
        skins_section.NAV_LABEL,
        loot.NAV_LABEL,
        challenges.NAV_LABEL,
        matches.NAV_LABEL,
        ranked.NAV_LABEL,
    }
    assert labels == {"造型", "碎片", "挑戰", "對戰", "排位"}


def test_nav_labels_are_shorter_than_titles():
    """導覽列用短標籤，不是 TITLE。"""
    for mod in (skins_section, loot, challenges, matches, ranked):
        assert len(mod.NAV_LABEL) < len(mod.TITLE)


def test_skins_nav_count_is_thousands_separated():
    inv = Inventory(
        summoner_name="T",
        summoner_id=1,
        champions=(
            Champion(1, "安妮", tuple(
                Skin(id=i, name=f"造型{i}", champion_id=1,
                     has_chromas=False, tile_path="/x.jpg")
                for i in range(1200)
            )),
        ),
    )
    assert skins_section.nav_count(inv) == "1,200"


def test_skins_nav_count_is_none_without_data():
    assert skins_section.nav_count(None) is None


def test_loot_nav_count_sums_duplicates():
    data = [
        {"name": "A", "count": 2, "value": 10, "rarity": "", "tile_path": ""},
        {"name": "B", "count": 3, "value": 10, "rarity": "", "tile_path": ""},
    ]
    assert loot.nav_count(data) == "5"


def test_loot_nav_count_is_none_when_empty():
    assert loot.nav_count(None) is None
    assert loot.nav_count([]) is None


def test_matches_nav_count_is_game_count():
    assert matches.nav_count([{}, {}, {}]) == "3"
    assert matches.nav_count(None) is None


def test_challenges_and_ranked_declare_no_count():
    """沒有有意義的單一數字就不定義——呼叫端用 getattr 取。"""
    assert not hasattr(challenges, "nav_count")
    assert not hasattr(ranked, "nav_count")
