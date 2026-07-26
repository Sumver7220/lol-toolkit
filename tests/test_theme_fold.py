"""圖像牆折疊的契約。

折疊高度由 JS 依視窗高度換算成完整排數，CSS 只負責裁切與遮罩，
因此這裡固定的是「規則有沒有被寫進去」與「有沒有踩到既有陷阱」。
"""

from loltk import theme


def test_expand_button_meets_the_touch_target_floor():
    assert "--more-h:44px" in theme.STYLE


def test_hidden_expand_button_is_actually_hidden():
    """.more 是 display:block，若不補這條，hidden 屬性會被蓋掉。"""
    assert ".more[hidden]{display:none}" in theme.STYLE


def test_fold_clips_the_wall_not_the_box():
    """遮罩要疊在 .wall-box 上——.wall 有 overflow:hidden。"""
    assert ".wall-box.folded .wall{overflow:hidden}" in theme.STYLE
    assert ".wall-box.folded::after{" in theme.STYLE


def test_fade_uses_a_theme_token_not_a_bare_colour():
    rule = theme.STYLE[theme.STYLE.index(".wall-box.folded::after{"):]
    rule = rule[: rule.index("}")]
    assert "var(--bg)" in rule
    assert "#" not in rule


def test_fold_measures_a_single_tile_not_all_of_them():
    """回歸測試：querySelectorAll('.t') 會讓跨區塊 tally bug 復發，
    見 test_page.py::test_script_scopes_tile_query_to_skin_wall。"""
    assert "querySelectorAll('.t')" not in theme.SCRIPT
    assert "querySelector('.t')" in theme.SCRIPT
    assert "children.length" in theme.SCRIPT


def test_fold_reads_gap_from_computed_style_not_hardcoded():
    """--tile-gap 改值時折疊高度必須跟著對。"""
    assert "rowGap" in theme.SCRIPT


def test_fold_recomputes_on_resize_without_an_observer_loop():
    """ResizeObserver 觀察被自己改動尺寸的元素會無限迴圈。

    只擋建構式而非整個字串——註解裡說明「為什麼不用它」是有價值的
    文件，不該因為提到名字就被擋下來。
    """
    assert "addEventListener('resize'" in theme.SCRIPT
    assert "new ResizeObserver" not in theme.SCRIPT


def test_searching_unfolds_the_skin_wall():
    """命中的 tile 可能落在被裁掉的區域。"""
    assert "unfold.get('skin-wall')" in theme.SCRIPT


def test_collapsing_scrolls_back_clear_of_the_sticky_chrome():
    """偏移量交給 CSS 宣告，JS 不必知道頁面上有哪些 sticky 元素。

    捲的是 .anchor 外殼：上方若有 sticky 工具列，捲到外殼開頭時那條列
    就在它自然的位置上，牆從它下方開始。不能改捲那條列本身——已經釘住
    的 sticky 元素其 rect 永遠等於落點，scrollIntoView 會判定「已經到位」
    而完全不捲動（實測捲軸 5000 → 5000，牆頂被蓋掉 289px）。
    """
    assert "(box.closest('.anchor')||box).scrollIntoView({block:'start'})" in theme.SCRIPT
    # 落點偏移由外殼自己宣告；.wall-box 那條是沒有外殼時的退路。
    assert ".anchor{scroll-margin-top:var(--nav-h)}" in theme.STYLE
    rule = theme.STYLE[theme.STYLE.index("\n.wall-box{") :]
    rule = rule[: rule.index("}")]
    assert "scroll-margin-top:var(--nav-h)" in rule
    # 反向：不得用固定 token 描述會隨螢幕寬度換行變高的工具列
    assert "calc(var(--nav-h) + var(--bar-h))" not in theme.STYLE


def test_folded_tiles_leave_the_tab_order():
    """回歸測試：overflow:hidden 只是視覺裁切。

    被裁掉的 tile 是真的 <button>，仍可聚焦；而且 overflow:hidden 容器
    會為了露出被聚焦的元素自行捲動，使用者會看到折疊視窗內部整片位移
    且捲不回去。
    """
    assert "tabIndex" in theme.SCRIPT
    # 三條「不折疊」路徑都要還原，少一條就會留下聚焦得到卻看不見的 tile
    assert theme.SCRIPT.count("seat(Infinity)") == 3
    # 折疊路徑只留可見的那幾排
    assert "seat(fold*cols)" in theme.SCRIPT
