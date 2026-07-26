import pytest

from loltk.sections import loot as sec


def shard(name, count=1, value=270, rarity="EPIC", cat="SKIN",
          tile="/lol-game-data/assets/ASSETS/a/b.jpg"):
    return {
        "itemDesc": name, "count": count, "disenchantValue": value,
        "rarity": rarity, "displayCategories": cat, "tilePath": tile,
    }


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def get_json(self, path):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def test_keeps_only_skin_shards():
    c = FakeClient([shard("花仙精靈 阿璃"), shard("鑰匙", cat="CHEST")])
    data = sec.fetch(c)
    assert len(data) == 1
    assert data[0]["name"] == "花仙精靈 阿璃"


def test_fetch_lets_exceptions_propagate():
    """例外必須往外拋給 safe_fetch，區塊不得自己吞掉。

    自己吞掉會讓 safe_fetch 看不到真正的錯誤，使用者只會看到區塊憑空
    消失而不知原因。
    """
    with pytest.raises(RuntimeError):
        sec.fetch(FakeClient(RuntimeError("boom")))


def test_fetch_returns_none_when_no_shards():
    assert sec.fetch(FakeClient([shard("鑰匙", cat="CHEST")])) is None


def test_sorted_by_disenchant_value_descending():
    c = FakeClient([shard("便宜", value=100), shard("貴", value=900)])
    assert [d["name"] for d in sec.fetch(c)] == ["貴", "便宜"]


def test_html_shows_count_and_total_value():
    data = [{"name": "花仙精靈 阿璃", "count": 2, "value": 270,
             "rarity": "EPIC", "tile_path": "/lol-game-data/assets/x.jpg"}]
    html = sec.to_html(data)
    assert "花仙精靈 阿璃" in html
    assert "540" in html  # 2 x 270
    assert 'class="wall"' in html


def test_html_marks_duplicate_count_only_when_above_one():
    one = [{"name": "A", "count": 1, "value": 10, "rarity": "EPIC",
            "tile_path": "/lol-game-data/assets/x.jpg"}]
    assert "×1" not in sec.to_html(one)
    two = [dict(one[0], count=2)]
    assert "×2" in sec.to_html(two)


def test_html_escapes_names():
    data = [{"name": 'x" onerror="evil()', "count": 1, "value": 1,
             "rarity": "EPIC", "tile_path": ""}]
    html = sec.to_html(data)
    assert 'onerror="evil()' not in html
    assert "&quot;" in html


def test_none_yields_empty_outputs():
    assert sec.to_html(None) == ""
    assert sec.to_dict(None) is None


def test_wall_has_no_skin_wall_id():
    """回歸測試：碎片牆不得有 id="skin-wall"。

    theme.SCRIPT 用 '#skin-wall .t' 限縮造型搜尋的查詢範圍，若碎片牆
    也用了這個 id，會讓兩個 wall 的 tile 混在一起被誤算。
    """
    data = [{"name": "花仙精靈 阿璃", "count": 1, "value": 270,
             "rarity": "EPIC", "tile_path": "/lol-game-data/assets/x.jpg"}]
    html = sec.to_html(data)
    assert 'id="skin-wall"' not in html
    assert 'class="wall"' in html
