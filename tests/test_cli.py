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


def test_main_browser_open_failure_does_not_report_as_write_error(
    monkeypatch, tmp_path, capsys
):
    """瀏覽器開不起來（例如找不到瀏覽器執行檔）不該被誤報成寫檔失敗，
    檔案仍要存在，離開碼仍要是 0。"""

    def boom(url):
        raise FileNotFoundError("no browser found")

    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: FakeClient())
    )
    monkeypatch.setattr(cli.webbrowser, "open", boom)
    code = cli.main(["skins", "--quiet", "--output", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "lol_skins.json").exists()
    assert (tmp_path / "lol_skins.html").exists()
    out = capsys.readouterr().out
    assert "寫入輸出檔時發生錯誤" not in out
    assert "無法自動開啟瀏覽器" in out
    assert str(tmp_path / "lol_skins.html") in out


def test_main_resolves_relative_output_dir(monkeypatch, tmp_path):
    """--output 傳入相對路徑時，webbrowser.open 收到的必須是有效的 file: URI，
    這代表 output_dir 有先被 .resolve() 成絕對路徑（否則 Path.as_uri() 會丟出
    ValueError: relative paths can't be expressed as file URIs）。"""
    monkeypatch.chdir(tmp_path)
    opened = []
    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: FakeClient())
    )
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: opened.append(url))
    code = cli.main(["skins", "--quiet", "--output", ".\\rel-out"])
    assert code == 0
    assert len(opened) == 1
    assert opened[0].startswith("file:")
    assert (tmp_path / "rel-out" / "lol_skins.html").exists()


def test_default_output_dir_uses_executable_dir_when_frozen(monkeypatch, tmp_path):
    """打包成 exe 後，輸出目錄應該取執行檔所在位置，而不是 cwd。"""
    fake_exe = tmp_path / "loltk.exe"
    monkeypatch.setattr(cli.sys, "frozen", True, raising=False)
    monkeypatch.setattr(cli.sys, "executable", str(fake_exe))
    assert cli.default_output_dir() == tmp_path.resolve()


def test_main_defaults_to_skins_when_frozen_with_no_args(monkeypatch, tmp_path):
    """雙擊 exe（無參數）時，應直接視為 `skins` 子命令，而不是顯示 argparse help。"""
    monkeypatch.setattr(cli.sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: FakeClient())
    )
    monkeypatch.setattr(cli, "default_output_dir", lambda: tmp_path)
    monkeypatch.setattr(cli.webbrowser, "open", lambda url: None)
    monkeypatch.setattr(cli, "_pause", lambda quiet: None)
    code = cli.main([])
    assert code == 0
    assert (tmp_path / "lol_skins.json").exists()


def test_main_shows_help_when_unpackaged_with_no_args(monkeypatch):
    """未打包（一般開發環境）且無參數時，仍要照 argparse 預設顯示 help 並離開。"""
    monkeypatch.delattr(cli.sys, "frozen", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        cli.main([])
    assert exc_info.value.code != 0
