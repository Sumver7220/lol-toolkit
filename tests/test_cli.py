import json
from datetime import datetime, timezone, timedelta

import pytest

from loltk import cli, lcu
from loltk.skins.inventory import Champion, Inventory, Skin

AT = datetime(2026, 7, 26, 14, 30, tzinfo=timezone(timedelta(hours=8)))


class FakeClient:
    def __init__(self, session_payload=None, skins_payload=None):
        self.session_payload = session_payload if session_payload is not None else {
            "summonerId": 42, "username": "Tester"
        }
        self.skins_payload = skins_payload if skins_payload is not None else []

    def get_json(self, path):
        if path == "/lol-login/v1/session":
            return self.session_payload
        return self.skins_payload


def test_parser_rejects_json_only_with_html_only():
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["skins", "--json-only", "--html-only"])


def test_parser_defaults():
    args = cli.build_parser().parse_args(["skins"])
    assert args.json_only is False
    assert args.html_only is False
    assert args.no_open is False
    assert args.quiet is False


def test_fetch_inventory_raises_when_not_logged_in():
    client = FakeClient(session_payload={"username": "X"})
    with pytest.raises(lcu.NotLoggedIn):
        cli.fetch_inventory(client)


def test_fetch_inventory_builds_model():
    raw = [
        {"name": "安妮", "id": 1000, "championId": 1, "isBase": True,
         "chromaPath": None, "tilePath": "/t.jpg", "ownership": {"owned": True}},
        {"name": "小紅帽 安妮", "id": 1002, "championId": 1, "isBase": False,
         "chromaPath": None, "tilePath": "/t.jpg", "ownership": {"owned": True}},
    ]
    inv = cli.fetch_inventory(FakeClient(skins_payload=raw))
    assert inv.summoner_name == "Tester"
    assert inv.champion_count == 1
    assert inv.skin_count == 1


def test_write_outputs_creates_both_files(tmp_path):
    inv = Inventory("T", 1, (Champion(1, "安妮", (
        Skin(1002, "小紅帽 安妮", 1, False, "/t.jpg"),)),))
    written = cli.write_outputs(inv, tmp_path, AT, json_only=False, html_only=False)
    assert (tmp_path / "lol_skins.json").exists()
    assert (tmp_path / "lol_skins.html").exists()
    assert len(written) == 2
    data = json.loads((tmp_path / "lol_skins.json").read_text(encoding="utf-8"))
    assert data["summary"]["skins"] == 1


def test_write_outputs_json_only(tmp_path):
    inv = Inventory("T", 1, ())
    written = cli.write_outputs(inv, tmp_path, AT, json_only=True, html_only=False)
    assert (tmp_path / "lol_skins.json").exists()
    assert not (tmp_path / "lol_skins.html").exists()
    assert len(written) == 1


def test_write_outputs_html_only(tmp_path):
    inv = Inventory("T", 1, ())
    cli.write_outputs(inv, tmp_path, AT, json_only=False, html_only=True)
    assert not (tmp_path / "lol_skins.json").exists()
    assert (tmp_path / "lol_skins.html").exists()


def test_main_reports_lcu_error_and_returns_nonzero(monkeypatch, capsys):
    def boom():
        raise lcu.ClientNotFound()

    monkeypatch.setattr(cli.lcu.LcuClient, "connect", staticmethod(boom))
    code = cli.main(["skins", "--quiet"])
    assert code == 1
    assert "找不到" in capsys.readouterr().out


def test_main_succeeds_and_returns_zero(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: FakeClient())
    )
    code = cli.main(["skins", "--quiet", "--no-open", "--output", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "lol_skins.json").exists()


def test_main_does_not_open_browser_when_no_open(monkeypatch, tmp_path):
    opened = []
    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: FakeClient())
    )
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened.append(url))
    cli.main(["skins", "--quiet", "--no-open", "--output", str(tmp_path)])
    assert opened == []


def test_main_opens_browser_by_default(monkeypatch, tmp_path):
    opened = []
    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: FakeClient())
    )
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened.append(url))
    monkeypatch.setattr(cli, "_pause", lambda quiet: None)
    cli.main(["skins", "--output", str(tmp_path)])
    assert len(opened) == 1


def test_quiet_skips_pause(monkeypatch, tmp_path):
    paused = []
    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: FakeClient())
    )
    monkeypatch.setattr("builtins.input", lambda *a: paused.append(1))
    cli.main(["skins", "--quiet", "--no-open", "--output", str(tmp_path)])
    assert paused == []
