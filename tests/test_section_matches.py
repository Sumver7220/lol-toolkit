import pytest

from loltk.sections import matches as sec


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def get_json(self, path):
        if isinstance(self.payload, Exception):
            raise self.payload
        if "current-summoner" in path:
            return {"puuid": "p-1"}
        return self.payload


def game(win=True, k=5, d=2, a=7, mode="KIWI", dur=1800, champ=1, queue_id=2400, map_id=12):
    return {
        "gameMode": mode, "gameDuration": dur, "gameCreationDate": "2026-07-26T20:00:00Z",
        "queueId": queue_id, "mapId": map_id,
        "participants": [{"championId": champ,
                          "stats": {"win": win, "kills": k, "deaths": d, "assists": a}}],
    }


def multiplayer_game(my_participant_id, my_puuid="p-1", win=True, k=5, d=2, a=7,
                      mode="KIWI", dur=1800, queue_id=2400, map_id=12):
    """十人陣列的真實形狀（見 participantIdentities 的實測結構）：
    participants 與 participantIdentities 分別用 participantId 對應，
    自己不保證在陣列的第一格。"""
    participants = []
    identities = []
    for pid in range(1, 11):
        is_me = pid == my_participant_id
        participants.append({
            "participantId": pid,
            "championId": pid,
            "stats": {
                "win": win if is_me else not win,
                "kills": k if is_me else 0,
                "deaths": d if is_me else 0,
                "assists": a if is_me else 0,
            },
        })
        identities.append({
            "participantId": pid,
            "player": {"puuid": my_puuid if is_me else f"other-{pid}"},
        })
    return {
        "gameMode": mode, "gameDuration": dur, "gameCreationDate": "2026-07-26T20:00:00Z",
        "queueId": queue_id, "mapId": map_id,
        "participants": participants,
        "participantIdentities": identities,
    }


def payload(games):
    return {"games": {"games": games, "gameCount": len(games)}}


def test_fetch_extracts_games():
    d = sec.fetch(FakeClient(payload([game(), game(win=False)])))
    assert len(d) == 2
    assert d[0]["win"] is True
    assert d[1]["win"] is False


def test_fetch_lets_exceptions_propagate():
    """例外必須往外拋給 safe_fetch，區塊不得自己吞掉。

    自己吞掉會讓 safe_fetch 看不到真正的錯誤，使用者只會看到區塊憑空
    消失而不知原因。
    """
    with pytest.raises(RuntimeError):
        sec.fetch(FakeClient(RuntimeError("boom")))


def test_fetch_returns_none_when_no_games():
    assert sec.fetch(FakeClient(payload([]))) is None


def test_kda_is_computed():
    d = sec.fetch(FakeClient(payload([game(k=6, d=2, a=4)])))
    assert d[0]["kda"] == "6/2/4"


def test_finds_correct_participant_by_puuid_in_full_ten_player_game():
    """回歸測試：先前的實作假設「自己」永遠是 participants[0]。

    真實對戰紀錄的 participants 是完整十人陣列，自己的 participantId
    不保證在陣列開頭（實測值為 9）。此測試把「我」放在陣列中段，
    若程式碼退回 participants[0]，KDA 與勝負會變成別人的。
    """
    g = multiplayer_game(my_participant_id=9, win=True, k=11, d=1, a=6)
    d = sec.fetch(FakeClient(payload([g])))
    assert d[0]["win"] is True
    assert d[0]["kda"] == "11/1/6"


def test_falls_back_to_first_participant_when_identity_missing():
    """缺 participantIdentities 時退回第一筆，維持不崩潰（保底路徑）。"""
    g = game(win=False, k=0, d=9, a=1)
    d = sec.fetch(FakeClient(payload([g])))
    assert d[0]["win"] is False
    assert d[0]["kda"] == "0/9/1"


def test_zero_deaths_does_not_crash():
    d = sec.fetch(FakeClient(payload([game(k=6, d=0, a=4)])))
    assert d[0]["kda"] == "6/0/4"


def test_duration_formatted_as_minutes():
    d = sec.fetch(FakeClient(payload([game(dur=1373)])))
    assert d[0]["duration"] == "22:53"


def test_html_states_the_ten_game_limit():
    """客戶端不保留完整歷史，必須明講，否則使用者以為自己只打過 10 場。"""
    d = sec.fetch(FakeClient(payload([game()])))
    html = sec.to_html(d)
    assert "最近" in html
    assert "不保留" in html or "完整歷史" in html


def test_html_shows_queue_name_for_known_queue_id():
    """已知的佇列 ID（如 450 ARAM）應顯示中文名稱。"""
    d = sec.fetch(FakeClient(payload([game(mode="KIWI", queue_id=450, map_id=12)])))
    html = sec.to_html(d)
    assert "大亂鬥" in html
    assert "KIWI" not in html


def test_html_falls_back_to_map_name_when_queue_unknown():
    """未知的佇列 ID 應改用地圖名稱（mapId 12 → 嚎哭深淵）。"""
    d = sec.fetch(FakeClient(payload([game(mode="KIWI", queue_id=2400, map_id=12)])))
    html = sec.to_html(d)
    assert "嚎哭深淵" in html
    assert "KIWI" not in html


def test_html_shows_other_mode_when_both_unknown():
    """佇列 ID 與地圖 ID 都未知時應顯示「其他模式」。"""
    d = sec.fetch(FakeClient(payload([game(mode="KIWI", queue_id=9999, map_id=9999)])))
    html = sec.to_html(d)
    assert "其他模式" in html
    assert "KIWI" not in html
    assert "9999" not in html


def test_raw_game_mode_never_appears_in_html():
    """內部代號（gameMode: KIWI 等）絕不應該出現在渲染的 HTML 中。"""
    games_with_various_modes = [
        game(mode="KIWI", queue_id=2400, map_id=12),
        game(mode="UNKNOWN_CODE", queue_id=9999, map_id=9999),
    ]
    d = sec.fetch(FakeClient(payload(games_with_various_modes)))
    html = sec.to_html(d)
    # 這些內部代號不應該在 HTML 中
    for raw_code in ["KIWI", "UNKNOWN_CODE"]:
        assert raw_code not in html, f"Raw code '{raw_code}' found in HTML output"


def test_html_marks_win_and_loss_distinctly():
    d = sec.fetch(FakeClient(payload([game(win=True), game(win=False)])))
    html = sec.to_html(d)
    assert "win" in html and "loss" in html


def test_json_preserves_raw_values_for_consumers():
    """JSON 輸出應保留原始的 gameMode、queueId、mapId，供機器消費者使用。"""
    d = sec.fetch(FakeClient(payload([game(mode="KIWI", queue_id=2400, map_id=12)])))
    as_dict = sec.to_dict(d)
    game_data = as_dict["games"][0]
    assert game_data["gameMode"] == "KIWI"
    assert game_data["queueId"] == 2400
    assert game_data["mapId"] == 12
    # 同時也應該有人類可讀的標籤
    assert game_data["mode_label"] == "嚎哭深淵"


def test_none_yields_empty_outputs():
    assert sec.to_html(None) == ""
    assert sec.to_dict(None) is None
