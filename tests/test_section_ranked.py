import pytest

from loltk.sections import ranked as sec


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def get_json(self, path):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


def q(name, tier="GOLD", div="II", lp=42, w=10, l=5):
    return {name: {"tier": tier, "division": div, "leaguePoints": lp,
                   "wins": w, "losses": l}}


def test_fetch_keeps_only_queues_with_games():
    payload = {"queueMap": {**q("RANKED_SOLO_5x5"),
                            **q("RANKED_FLEX_SR", w=0, l=0)}}
    d = sec.fetch(FakeClient(payload))
    assert len(d) == 1
    assert d[0]["queue"] == "單／雙排"


def test_fetch_returns_none_when_no_queue_has_games():
    payload = {"queueMap": {**q("RANKED_SOLO_5x5", w=0, l=0)}}
    assert sec.fetch(FakeClient(payload)) is None


def test_fetch_lets_exceptions_propagate():
    """例外必須往外拋給 safe_fetch，區塊不得自己吞掉。

    自己吞掉會讓 safe_fetch 看不到真正的錯誤，使用者只會看到區塊憑空
    消失而不知原因。
    """
    with pytest.raises(RuntimeError):
        sec.fetch(FakeClient(RuntimeError("boom")))


def test_winrate_is_computed():
    d = sec.fetch(FakeClient({"queueMap": {**q("RANKED_SOLO_5x5", w=15, l=5)}}))
    assert d[0]["winrate"] == 75


def test_empty_state_html_is_rendered_for_none():
    """排位常態為空，必須有明確的空狀態而不是整段消失。"""
    html = sec.empty_html()
    assert "本賽季" in html
    assert "排位" in html


def test_to_html_none_returns_empty_string():
    assert sec.to_html(None) == ""


def test_to_dict_none():
    assert sec.to_dict(None) is None
