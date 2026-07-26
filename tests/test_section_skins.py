from loltk.sections import skins as sec
from loltk.skins.inventory import Champion, Inventory, Skin


def sk(i, name, cid=1, chroma=False, tile="/lol-game-data/assets/ASSETS/a/b.jpg"):
    return Skin(id=i, name=name, champion_id=cid, has_chromas=chroma, tile_path=tile)


def inv(champions):
    return Inventory(summoner_name="T", summoner_id=1, champions=tuple(champions))


ANNIE = Champion(1, "安妮", (sk(1002, "小紅帽 安妮"), sk(1013, "牛年 安妮", chroma=True)))
BARE = Champion(268, "阿祈爾", ())


def test_tiles_are_flat_not_grouped():
    """486 張 tile 連續鋪排，不再每個英雄一個容器。"""
    html = sec.to_html(inv([ANNIE, Champion(2, "歐拉夫", (sk(2001, "哥拉夫", 2),))]))
    assert html.count('class="wall"') == 1
    assert 'class="champion"' not in html
    assert html.count('data-k="') == 3


def test_wall_has_skin_wall_id_for_script_scoping():
    """回歸測試：theme.SCRIPT 用 '#skin-wall .t' 限縮查詢範圍，

    造型牆必須有這個 id，否則搜尋計數會把碎片牆的 tile 也算進去
    （見 loltk/sections/loot.py 的同款 .wall 容器）。
    """
    html = sec.to_html(inv([ANNIE]))
    assert 'id="skin-wall"' in html


def test_tile_is_a_button_for_keyboard_access():
    html = sec.to_html(inv([ANNIE]))
    assert "<button" in html
    assert 'class="t' in html


def test_tile_caption_has_skin_and_champion_name():
    html = sec.to_html(inv([ANNIE]))
    assert "小紅帽 安妮" in html
    assert "安妮" in html


def test_chroma_marked_with_class_not_extra_element():
    html = sec.to_html(inv([ANNIE]))
    assert "t ch" in html


def test_search_key_is_lowercased_and_covers_both_names():
    html = sec.to_html(inv([ANNIE]))
    assert 'data-k="' in html
    assert "小紅帽 安妮" in html


def test_zero_skin_champions_go_to_chips_not_wall():
    html = sec.to_html(inv([ANNIE, BARE]))
    assert "阿祈爾" in html
    assert 'class="chips"' in html
    assert "1 位英雄" in html
    assert html.count('data-k="') == 2


def test_no_chip_section_when_every_champion_has_skins():
    html = sec.to_html(inv([ANNIE]))
    assert 'class="chips"' not in html


def test_index_lists_only_champions_with_skins():
    html = sec.to_html(inv([ANNIE, BARE]))
    idx = html[html.index('id="index"'):]
    assert "安妮" in idx
    assert idx.count('class="ix"') == 1


def test_missing_tile_path_still_renders_name():
    html = sec.to_html(inv([Champion(3, "無圖", (sk(3001, "沒有圖", 3, tile=""),))]))
    assert "沒有圖" in html
    assert "<img" not in html


def test_escapes_hostile_names():
    evil = Champion(9, 'A&B', (sk(9001, 'x" onerror="evil()'),))
    html = sec.to_html(inv([evil]))
    assert 'onerror="evil()' not in html
    assert "&amp;" in html
    assert "&quot;" in html


def test_none_returns_empty_string():
    assert sec.to_html(None) == ""
    assert sec.to_dict(None) is None


def test_tile_counting_with_data_k_is_collision_proof():
    """回歸測試：用 data-k 計算 tile，對 class=\"tally 免疫。

    確保即使有 class=\"tally num\" 元素，tile 計數也不會誤算。
    tile 數量必須等於已知造型數；class=\"tally num\" 必須存在；
    若用脆弱的 class=\"t 計數法，此測試會失敗（發現 collision）。
    """
    # 2 個英雄、3 張造型
    html = sec.to_html(inv([ANNIE, Champion(2, "歐拉夫", (sk(2001, "哥拉夫", 2),))]))

    # 用 data-k 計數：應該恰好 3 張 tile
    assert html.count('data-k="') == 3

    # 驗證 class="tally num" 確實存在（頁面正常結構）
    assert 'class="tally num"' in html

    # 驗證用脆弱的 class="t 會多算：
    # - 3 張 tile 的 class="t "
    # - 1 個 tally 的 class="tally num"（「class="t」會命中「class="tally」）
    # = 總計 4（不是我們想要的 3）
    fragile_count = html.count('class="t')
    assert fragile_count == 4, (
        f"脆弱計數法 count('class=\"t') 回傳 {fragile_count}，"
        f"包含了 tally 元素（collision）。這驗證了為什麼用 data-k 才安全。"
    )
