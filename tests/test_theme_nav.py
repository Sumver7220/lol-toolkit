"""導覽列的樣式契約。

CSS 無法在單元測試裡真的算繪,因此這裡固定的是「容易在改動中被
悄悄破壞」的關係,而不是外觀本身。
"""

from loltk import theme


def test_nav_height_is_a_component_token():
    assert "--nav-h:44px" in theme.STYLE


def test_search_bar_sticks_below_the_nav_not_at_zero():
    """回歸測試:.bar 若維持 top:0 會疊在導覽列上。"""
    bar = theme.STYLE[theme.STYLE.index(".bar{"):]
    bar = bar[: bar.index("}")]
    assert "top:var(--nav-h)" in bar
    assert "top:0" not in bar


def test_nav_sits_above_the_search_bar():
    """.bar 的 z-index 是 40,導覽列必須更高。"""
    nav = theme.STYLE[theme.STYLE.index(".nav{"):]
    nav = nav[: nav.index("}")]
    assert "z-index:50" in nav


def test_anchors_offset_scroll_by_nav_height():
    assert ".anchor{scroll-margin-top:var(--nav-h)}" in theme.STYLE


def test_active_nav_item_has_a_non_colour_cue():
    """不能只靠顏色區分作用中項目。"""
    assert ".nv.on{" in theme.STYLE
    on = theme.STYLE[theme.STYLE.index(".nv.on{"):]
    assert "border-bottom-color:var(--accent)" in on[: on.index("}")]


def test_nav_items_fill_the_full_touch_height():
    """觸控目標最小 44x44;項目必須撐滿導覽列全高。"""
    wrap = theme.STYLE[theme.STYLE.index(".nav .wrap{"):]
    assert "height:var(--nav-h)" in wrap[: wrap.index("}")]


def test_narrow_screens_hide_counts_instead_of_scrolling_sideways():
    """390px 不得橫向捲動;計數在海報卡的數字帶裡已經有了。"""
    assert ".nv b{display:none}" in theme.STYLE
    assert "overflow-x:auto" not in theme.STYLE


def test_smooth_scroll_respects_reduced_motion():
    assert "prefers-reduced-motion:no-preference" in theme.STYLE
    idx = theme.STYLE.index("scroll-behavior:smooth")
    guard = theme.STYLE.index("prefers-reduced-motion:no-preference")
    assert guard < idx


def test_sr_only_hides_visually_without_hiding_from_screen_readers():
    assert ".sr-only{" in theme.STYLE
    rule = theme.STYLE[theme.STYLE.index(".sr-only{"):]
    rule = rule[: rule.index("}")]
    assert "clip-path:inset(50%)" in rule
    assert "display:none" not in rule


def test_nav_marks_current_section_for_assistive_tech():
    assert "aria-current" in theme.SCRIPT


def test_nav_uses_observer_not_a_scroll_loop():
    assert "IntersectionObserver" in theme.SCRIPT
    assert "addEventListener('scroll'" not in theme.SCRIPT
