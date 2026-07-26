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
    "current-summoner": {"summonerLevel": 467, "displayName": "", "gameName": "Tester",
                         "summonerId": 42},
    "honor": {"honorLevel": 5},
    "wallet": {"RP": 1286, "lol_blue_essence": 458965, "lol_orange_essence": 3890},
}


def test_fetches_all_three():
    d, errors = sec.fetch(FakeClient(ALL_OK))
    assert d["level"] == 467
    assert d["honor"] == 5
    assert d["blue_essence"] == 458965
    assert d["rp"] == 1286
    assert errors == []


def test_one_endpoint_failing_does_not_kill_the_others():
    m = dict(ALL_OK, honor=RuntimeError("boom"))
    m["honor"] = RuntimeError("boom")
    d, errors = sec.fetch(FakeClient(m))
    assert d["level"] == 467
    assert d["honor"] is None
    assert d["blue_essence"] == 458965
    assert len(errors) == 1


def test_all_endpoints_failing_returns_all_none_not_exception():
    m = {k: RuntimeError("boom") for k in ALL_OK}
    d, errors = sec.fetch(FakeClient(m))
    assert set(v for k, v in d.items() if k not in ("account_name", "account_id")) == {None}
    assert d["account_name"] is None
    assert len(errors) == 3


def test_missing_field_becomes_none_not_zero():
    """缺值必須是 None——0 會被誤讀為真的沒有。"""
    m = dict(ALL_OK)
    m["honor"] = {}
    d, errors = sec.fetch(FakeClient(m))
    assert d["honor"] is None
    assert errors == []


def test_account_name_prefers_game_name_over_display_name():
    """實測帳號 displayName 為空字串、gameName 才有值，因此以 gameName 優先。"""
    d, _ = sec.fetch(FakeClient(ALL_OK))
    assert d["account_name"] == "Tester"


def test_account_name_falls_back_to_display_name():
    m = dict(ALL_OK)
    m["current-summoner"] = {"summonerLevel": 467, "displayName": "顯示名", "gameName": ""}
    d, _ = sec.fetch(FakeClient(m))
    assert d["account_name"] == "顯示名"


def test_failing_endpoint_is_reported_not_silently_dropped():
    """summary 是逐欄位容錯，但失敗仍必須回報，不能是靜默的例外邊界。"""
    m = dict(ALL_OK, honor=RuntimeError("wallet endpoint renamed"))
    d, errors = sec.fetch(FakeClient(m))
    assert any("wallet endpoint renamed" in e for e in errors)


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
