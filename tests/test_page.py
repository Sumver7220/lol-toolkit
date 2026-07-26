from datetime import datetime, timedelta, timezone

from loltk import page, theme

AT = datetime(2026, 7, 27, 14, 30, tzinfo=timezone(timedelta(hours=8)))


def build(**kw):
    args = dict(
        summoner_name="SumverMizz",
        generated_at=AT,
        figures=[page.Figure("486", "造型", lead=True), page.Figure("173", "英雄")],
        sections=["<section id='x'>內容</section>"],
        total_tiles=486,
    )
    args.update(kw)
    return page.render_page(**args)


def test_page_is_self_contained():
    html = build()
    assert html.startswith("<!DOCTYPE html>")
    assert "</html>" in html
    assert "<script src=" not in html
    assert "fonts.googleapis" not in html
    assert "cdn.jsdelivr" not in html


def test_page_embeds_style_and_script():
    html = build()
    assert theme.STYLE.strip()[:40] in html
    assert "getElementById" in html


def test_theme_has_no_manual_toggle_leftovers():
    """mockup 的 data-t 覆寫與 .mockonly 按鈕不應進入正式輸出。"""
    assert "data-t" not in theme.STYLE
    assert "mockonly" not in theme.STYLE
    assert "mockonly" not in theme.SCRIPT


def test_script_scopes_tile_query_to_skin_wall():
    """回歸測試：跨區塊 tally bug。

    碎片區塊（loltk/sections/loot.py）跟造型牆共用同一份 .t/.wall
    標記，若 SCRIPT 用不限範圍的 querySelectorAll('.t') 抓 tile，
    分子會把碎片也算進去，但分母（__TOTAL__）只算造型數，
    導致「找到的 / 造型總數」對不上（例如 575 / 486）。
    查詢必須限縮在 #skin-wall 裡。
    """
    assert "querySelectorAll('#skin-wall .t')" in theme.SCRIPT
    # 不能同時留著沒有限縮範圍的舊寫法
    assert "querySelectorAll('.t')" not in theme.SCRIPT


def test_script_guards_missing_dom_elements():
    """回歸測試：`loltk loot` 單獨模式沒有 .bar / #q / #skin-wall。

    SCRIPT 目前的寫法一開頭就抓 #q 並直接掛 addEventListener，
    在只有碎片區塊的頁面上 #q 是 null，會丟出 TypeError 讓整段
    JS 掛掉。修正後必須在抓不到 #q 時安靜跳過，不執行後續的
    tally／index／#none 邏輯。

    這裡只能靜態檢查 SCRIPT 原始碼有沒有防護（例如 `if(q){`
    這種在使用 q 之前先判斷是否存在的寫法）；DOM 層面的行為
    已用無頭瀏覽器（Playwright）對 `loltk loot` 單獨算繪出的
    HTML 人工確認過，console 沒有出現 TypeError（見任務報告）。
    """
    assert "if(q){" in theme.SCRIPT
    q_pos = theme.SCRIPT.index("getElementById('q')")
    guard_pos = theme.SCRIPT.index("if(q){")
    add_listener_pos = theme.SCRIPT.index("q.addEventListener")
    # 防護必須夾在「拿到 q」跟「開始使用 q」之間
    assert q_pos < guard_pos < add_listener_pos


def test_poster_shows_name_time_and_figures():
    html = build()
    assert "SumverMizz" in html
    assert "2026-07-27 14:30" in html
    assert ">486<" in html and ">造型<" in html
    assert 'class="fig lead"' in html


def test_total_is_templated_into_script():
    html = build(total_tiles=1234)
    assert "1234" in html
    assert "TOTAL=486" not in html


def test_sections_are_inserted_in_order():
    html = build(sections=["<i>一</i>", "<i>二</i>"])
    assert html.index("<i>一</i>") < html.index("<i>二</i>")


def test_escapes_summoner_name():
    html = build(summoner_name='<script>alert("x")</script>')
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_escapes_quotes_in_attributes():
    """quote=True 必須生效，否則使用者自訂名稱可從屬性值逸出。"""
    html = build(summoner_name='x" onload="evil()')
    assert 'onload="evil()' not in html
    assert "&quot;" in html


def test_empty_figures_still_renders():
    html = build(figures=[])
    assert "<!DOCTYPE html>" in html
    assert "SumverMizz" in html


from loltk.sections import _tile


def test_tile_without_image_shows_name_only():
    html = _tile.tile(name="沒有圖")
    assert "<img" not in html
    assert "沒有圖" in html


def test_tile_with_image_has_lazy_and_onerror_fallback():
    html = _tile.tile(name="A", tile_path="/lol-game-data/assets/x.jpg")
    assert 'loading="lazy"' in html
    assert "classList.add('dead')" in html


def test_tile_escapes_hostile_name():
    html = _tile.tile(name='x" onerror="evil()')
    assert 'onerror="evil()' not in html
    assert "&quot;" in html


def test_tile_search_key_defaults_to_name_lowercased():
    assert 'data-k="annie"' in _tile.tile(name="Annie")


def test_tile_extra_class_is_applied():
    assert 'class="t ch"' in _tile.tile(name="A", extra_class="ch")


import pytest

from loltk import lcu
from loltk import sections


class _Sec:
    def __init__(self, result):
        self.result = result

    def fetch(self, client):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def test_safe_fetch_passes_data_through():
    data, err = sections.safe_fetch(_Sec("ok"), client=None)
    assert data == "ok" and err is None


def test_safe_fetch_converts_lcu_error_to_its_chinese_message():
    data, err = sections.safe_fetch(_Sec(lcu.ClientNotFound()), client=None)
    assert data is None
    assert "客戶端" in err


def test_safe_fetch_catches_unexpected_exception_with_type_name():
    data, err = sections.safe_fetch(_Sec(TypeError("bad")), client=None)
    assert data is None
    assert "TypeError" in err and "bad" in err


def test_safe_fetch_never_raises():
    """任何區塊失敗都不得讓整頁產生失敗。"""
    for exc in (KeyError("k"), ValueError("v"), RuntimeError("r")):
        data, err = sections.safe_fetch(_Sec(exc), client=None)
        assert data is None and err
