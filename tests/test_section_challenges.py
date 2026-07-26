import pytest

from loltk.sections import challenges as sec


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def get_json(self, path):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def cat(name, cur, mx, lvl):
    return {"category": name, "current": cur, "max": mx, "level": lvl}


PAYLOAD = {"categoryProgress": [
    cat("COLLECTION", 2750, 4200, "DIAMOND"),
    cat("TEAMWORK", 1040, 7735, "SILVER"),
]}


def test_fetch_extracts_categories():
    d = sec.fetch(FakeClient(PAYLOAD))
    assert len(d) == 2
    assert d[0]["name"] == "收藏"


def test_fetch_lets_exceptions_propagate():
    """例外必須往外拋給 safe_fetch，區塊不得自己吞掉。

    自己吞掉會讓 safe_fetch 看不到真正的錯誤，使用者只會看到區塊憑空
    消失而不知原因。
    """
    with pytest.raises(RuntimeError):
        sec.fetch(FakeClient(RuntimeError("boom")))


def test_fetch_returns_none_when_empty():
    assert sec.fetch(FakeClient({"categoryProgress": []})) is None


def test_percent_is_computed_and_clamped():
    d = sec.fetch(FakeClient({"categoryProgress": [cat("COLLECTION", 9999, 100, "X")]}))
    assert d[0]["percent"] == 100


def test_zero_max_does_not_divide_by_zero():
    d = sec.fetch(FakeClient({"categoryProgress": [cat("COLLECTION", 5, 0, "X")]}))
    assert d[0]["percent"] == 0


def test_html_renders_a_bar_per_category():
    d = sec.fetch(FakeClient(PAYLOAD))
    html = sec.to_html(d)
    assert html.count('class="prog"') == 2
    assert "收藏" in html and "團隊合作" in html
    assert "2,750" in html and "4,200" in html


def test_html_shows_level_label():
    d = sec.fetch(FakeClient(PAYLOAD))
    assert "DIAMOND" in sec.to_html(d)


def test_unknown_category_falls_back_to_raw_name():
    d = sec.fetch(FakeClient({"categoryProgress": [cat("NEWTHING", 1, 2, "X")]}))
    assert d[0]["name"] == "NEWTHING"


def test_none_yields_empty_outputs():
    assert sec.to_html(None) == ""
    assert sec.to_dict(None) is None
