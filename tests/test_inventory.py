from loltk.skins.inventory import Champion, Inventory, Skin, build_inventory


def raw_skin(name, skin_id, champion_id, *, base=False, owned=True, chroma=None, tile="/t.jpg"):
    return {
        "name": name,
        "id": skin_id,
        "championId": champion_id,
        "isBase": base,
        "chromaPath": chroma,
        "tilePath": tile,
        "ownership": {"owned": owned},
    }


def build(skins):
    return build_inventory(skins, summoner_name="Tester", summoner_id=42)


def test_groups_skins_under_their_champion():
    inv = build([
        raw_skin("安妮", 1000, 1, base=True),
        raw_skin("小紅帽 安妮", 1002, 1),
    ])
    assert inv.champion_count == 1
    assert inv.champions[0].name == "安妮"
    assert [s.name for s in inv.champions[0].skins] == ["小紅帽 安妮"]


def test_base_skin_appearing_after_other_skins_is_still_grouped():
    """不依賴 API 回傳順序：基礎造型排在後面時造型不能遺失。"""
    inv = build([
        raw_skin("小紅帽 安妮", 1002, 1),
        raw_skin("安妮", 1000, 1, base=True),
    ])
    assert [s.name for s in inv.champions[0].skins] == ["小紅帽 安妮"]


def test_unowned_skins_and_champions_are_excluded():
    inv = build([
        raw_skin("安妮", 1000, 1, base=True),
        raw_skin("小紅帽 安妮", 1002, 1),
        raw_skin("舞會皇后 安妮", 1004, 1, owned=False),
        raw_skin("歐拉夫", 2000, 2, base=True, owned=False),
        raw_skin("哥拉夫", 2001, 2),
    ])
    assert inv.champion_count == 1
    assert [s.name for s in inv.champions[0].skins] == ["小紅帽 安妮"]


def test_champion_owned_without_extra_skins_has_empty_skin_list():
    inv = build([raw_skin("阿祈爾", 268000, 268, base=True)])
    assert inv.champions[0].skins == ()
    assert inv.skin_count == 0


def test_champion_id_type_mismatch_still_groups():
    """championId 在基礎造型與其他造型間型別不一致時仍須對得上。"""
    inv = build([
        raw_skin("蓋倫", 86000, "86", base=True),
        raw_skin("鋼鐵軍團 蓋倫", 86001, 86),
    ])
    assert [s.name for s in inv.champions[0].skins] == ["鋼鐵軍團 蓋倫"]


def test_empty_list_produces_empty_inventory():
    inv = build([])
    assert inv.champions == ()
    assert inv.champion_count == 0
    assert inv.skin_count == 0


def test_champions_sorted_by_name_and_skins_sorted_by_id():
    inv = build([
        raw_skin("歐拉夫", 2000, 2, base=True),
        raw_skin("安妮", 1000, 1, base=True),
        raw_skin("超萌咖啡廳 安妮", 1022, 1),
        raw_skin("小紅帽 安妮", 1002, 1),
    ])
    assert [c.name for c in inv.champions] == ["安妮", "歐拉夫"]
    assert [s.id for s in inv.champions[0].skins] == [1002, 1022]


def test_has_chromas_reflects_chroma_path_presence():
    inv = build([
        raw_skin("安妮", 1000, 1, base=True),
        raw_skin("有炫彩", 1013, 1, chroma="/chroma.png"),
        raw_skin("無炫彩", 1002, 1, chroma=None),
    ])
    by_name = {s.name: s for s in inv.champions[0].skins}
    assert by_name["有炫彩"].has_chromas is True
    assert by_name["無炫彩"].has_chromas is False


def test_summoner_details_are_carried_through():
    inv = build([])
    assert inv.summoner_name == "Tester"
    assert inv.summoner_id == 42


def test_tile_path_is_preserved_for_rendering():
    inv = build([
        raw_skin("安妮", 1000, 1, base=True),
        raw_skin("小紅帽 安妮", 1002, 1, tile="/lol-game-data/assets/ASSETS/x.jpg"),
    ])
    assert inv.champions[0].skins[0].tile_path == "/lol-game-data/assets/ASSETS/x.jpg"
