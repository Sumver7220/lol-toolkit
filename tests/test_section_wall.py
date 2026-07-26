"""圖像牆共用外殼。

折疊是 .wall 這個版面模式本身的行為，不是造型區塊的特例——碎片牆
與未來新增的任何圖像牆都用同一份標記。
"""

from loltk.inventory import Champion, Inventory, Skin
from loltk.sections import _wall, loot
from loltk.sections import skins as skins_section


def test_wall_wraps_tiles_and_expand_button():
    html = _wall.wall(tiles="<i>t</i>", wall_id="w", expand_label="展開全部 3 個造型")
    assert 'class="wall-box"' in html
    assert '<div class="wall" id="w">' in html
    assert 'class="more"' in html
    assert "展開全部 3 個造型" in html


def test_expand_button_is_wired_to_its_wall():
    html = _wall.wall(tiles="", wall_id="w", expand_label="展開")
    assert 'aria-controls="w"' in html
    assert 'aria-expanded="false"' in html


def test_expand_button_defaults_to_hidden():
    """JS 停用時牆本來就是全展開的，這顆按鈕預設不該出現；

    JS 啟用後 theme.SCRIPT 的 paint() 會在判定需要折疊時把 hidden 拿掉。
    """
    html = _wall.wall(tiles="", wall_id="w", expand_label="展開")
    assert "hidden" in html


def test_expand_label_is_escaped():
    html = _wall.wall(tiles="", wall_id="w", expand_label='x" onclick="evil()')
    assert 'onclick="evil()' not in html
    assert "&quot;" in html


ANNIE = Champion(1, "安妮", (
    Skin(id=1002, name="小紅帽 安妮", champion_id=1,
         has_chromas=False, tile_path="/lol-game-data/assets/a.jpg"),
))


def test_skins_wall_uses_the_shared_shell():
    html = skins_section.to_html(
        Inventory(summoner_name="T", summoner_id=1, champions=(ANNIE,))
    )
    assert 'class="wall-box"' in html
    assert 'id="skin-wall"' in html
    assert 'aria-controls="skin-wall"' in html


def test_skins_expand_label_uses_the_right_measure_word():
    html = skins_section.to_html(
        Inventory(summoner_name="T", summoner_id=1, champions=(ANNIE,))
    )
    assert "1 個造型" in html


def test_loot_wall_has_its_own_id_and_measure_word():
    data = [{"name": "花仙精靈 阿璃", "count": 2, "value": 270,
             "rarity": "EPIC", "tile_path": "/lol-game-data/assets/x.jpg"}]
    html = loot.to_html(data)
    assert 'id="loot-wall"' in html
    assert 'id="skin-wall"' not in html
    assert "2 個碎片" in html


def test_skins_section_has_a_heading_for_screen_readers():
    """回歸測試：造型區塊原本沒有 <h2>，使 h1 直接跳到零造型英雄的 <h3>。

    視覺上仍不顯示可見標題（首屏要留給兩排造型），但螢幕閱讀器
    必須能靠標題導覽到這個區塊。
    """
    html = skins_section.to_html(
        Inventory(summoner_name="T", summoner_id=1, champions=(ANNIE,))
    )
    assert '<h2 class="sr-only">造型收藏</h2>' in html
    assert "block-h" not in html  # 不顯示可見標題
