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
    """ResizeObserver 觀察被自己改動尺寸的元素會無限迴圈。"""
    assert "addEventListener('resize'" in theme.SCRIPT
    assert "ResizeObserver" not in theme.SCRIPT


def test_searching_unfolds_the_skin_wall():
    """命中的 tile 可能落在被裁掉的區域。"""
    assert "unfold.get('skin-wall')" in theme.SCRIPT


def test_collapsing_scrolls_back_with_the_nav_offset():
    assert "NAVH" in theme.SCRIPT
    assert "scrollTo(" in theme.SCRIPT
