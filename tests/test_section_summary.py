import pytest

from loltk.sections import summary as sec


class FakeClient:
    """依 path 關鍵字回傳假資料；設為 Exception 則該 path 拋錯。"""

    def __init__(self, mapping):
        self.mapping = mapping

    def get_json(self, path):
        for key, val in self.mapping.items():
            if key in path:
                if isinstance(val, Exception):
                    raise val
                return val
        raise KeyError(path)


ALL_OK = {
    "current-summoner": {"summonerLevel": 467},
    "honor": {"honorLevel": 5},
    "wallet": {"RP": 1286, "lol_blue_essence": 458965, "lol_orange_essence": 3890},
}


def test_fetches_all_three():
    d = sec.fetch(FakeClient(ALL_OK))
    assert d["level"] == 467
    assert d["honor"] == 5
    assert d["blue_essence"] == 458965
    assert d["rp"] == 1286


def test_one_endpoint_failing_does_not_kill_the_others():
    m = dict(ALL_OK, honor=RuntimeError("boom"))
    m["honor"] = RuntimeError("boom")
    d = sec.fetch(FakeClient(m))
    assert d["level"] == 467
    assert d["honor"] is None
    assert d["blue_essence"] == 458965


def test_all_endpoints_failing_returns_all_none_not_exception():
    m = {k: RuntimeError("boom") for k in ALL_OK}
    d = sec.fetch(FakeClient(m))
    assert set(d.values()) == {None}


def test_missing_field_becomes_none_not_zero():
    """缺值必須是 None——0 會被誤讀為真的沒有。"""
    m = dict(ALL_OK)
    m["honor"] = {}
    d = sec.fetch(FakeClient(m))
    assert d["honor"] is None


def test_figures_omit_missing_values_entirely():
    d = {"level": 467, "honor": None, "blue_essence": None, "rp": 1286,
         "orange_essence": None}
    labels = [f.label for f in sec.figures(d)]
    assert "等級" in labels
    assert "RP" in labels
    assert "榮譽" not in labels
    assert "藍色精華" not in labels


def test_figures_format_thousands_separator():
    d = {"level": None, "honor": None, "blue_essence": 458965, "rp": None,
         "orange_essence": None}
    assert sec.figures(d)[0].value == "458,965"


def test_figures_empty_when_nothing_available():
    d = {k: None for k in ("level", "honor", "blue_essence", "rp", "orange_essence")}
    assert sec.figures(d) == []


def test_to_dict_drops_none_keys():
    d = {"level": 467, "honor": None, "blue_essence": None, "rp": None,
         "orange_essence": None}
    assert sec.to_dict(d) == {"level": 467}
