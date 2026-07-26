import json
from datetime import datetime, timezone, timedelta

import pytest

from loltk import cli, lcu

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


def test_write_outputs_creates_both_files(tmp_path):
    written = cli.write_outputs(
        "<html>頁面</html>", {"summary": {"skins": 1}}, tmp_path,
        json_only=False, html_only=False,
    )
    assert (tmp_path / "lol_skins.json").exists()
    assert (tmp_path / "lol_skins.html").exists()
    assert len(written) == 2
    data = json.loads((tmp_path / "lol_skins.json").read_text(encoding="utf-8"))
    assert data["summary"]["skins"] == 1


def test_write_outputs_json_only(tmp_path):
    written = cli.write_outputs(
        "<html></html>", {}, tmp_path, json_only=True, html_only=False
    )
    assert (tmp_path / "lol_skins.json").exists()
    assert not (tmp_path / "lol_skins.html").exists()
    assert len(written) == 1


def test_write_outputs_html_only(tmp_path):
    cli.write_outputs(
        "<html></html>", {}, tmp_path, json_only=False, html_only=True
    )
    assert not (tmp_path / "lol_skins.json").exists()
    assert (tmp_path / "lol_skins.html").exists()


def test_main_reports_lcu_error_and_returns_nonzero(monkeypatch, capsys):
    def boom():
        raise lcu.ClientNotFound()

    monkeypatch.setattr(cli.lcu.LcuClient, "connect", staticmethod(boom))
    code = cli.main(["skins", "--quiet"])
    assert code == 1
    assert "找不到" in capsys.readouterr().err


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
    err = capsys.readouterr().err
    assert "寫入輸出檔時發生錯誤" not in err
    assert "無法自動開啟瀏覽器" in err
    assert str(tmp_path / "lol_skins.html") in err


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


def test_main_defaults_to_all_when_frozen_with_no_args(monkeypatch, tmp_path):
    """雙擊 exe（無參數）時，應直接視為 `all` 子命令，而不是顯示 argparse help。"""
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


def test_main_catches_unexpected_exception_and_still_pauses(monkeypatch, tmp_path, capsys):
    """未預期的例外（例如格式錯誤的紀錄造成 TypeError）不得讓 exe 視窗
    瞬間消失：仍要印出訊息、回傳非零離開碼，且照樣暫停等待 Enter。"""

    def boom():
        raise TypeError("'NoneType' object is not subscriptable")

    monkeypatch.setattr(cli.lcu.LcuClient, "connect", staticmethod(boom))
    paused = []
    monkeypatch.setattr("builtins.input", lambda *a: paused.append(1))
    code = cli.main(["skins", "--output", str(tmp_path)])
    assert code == 1
    assert paused == [1]
    assert "發生未預期的錯誤" in capsys.readouterr().err


AT2 = datetime(2026, 7, 27, 14, 30, tzinfo=timezone(timedelta(hours=8)))


class SectionClient:
    """所有 endpoint 都回傳空/無效資料，用來測全部區塊皆空的情況。"""

    def get_json(self, path):
        if "current-summoner" in path:
            return {"summonerLevel": 467, "puuid": "p", "displayName": "T"}
        if "login/v1/session" in path:
            return {"summonerId": 1, "username": "T"}
        if "skins-minimal" in path:
            return []
        return {}


def test_all_sections_registered():
    keys = [s.KEY for s in cli.SECTIONS]
    assert keys == ["skins", "loot", "challenges", "matches", "ranked"]


def test_build_report_with_empty_data_still_produces_page():
    html, data, skipped = cli.build_report(SectionClient(), AT2, keys=None)
    assert "<!DOCTYPE html>" in html
    assert data["schemaVersion"] == 2
    assert skipped == []


def test_keys_filter_limits_sections():
    html, data, _ = cli.build_report(SectionClient(), AT2, keys=["skins"])
    assert "loot" not in data
    assert "champions" in data
    assert "account" in data


def test_json_keeps_champions_shape_unchanged():
    html, data, _ = cli.build_report(SectionClient(), AT2, keys=None)
    assert "account" in data and "champions" in data
    assert "skins" not in data  # champions 提到頂層，不留巢狀 key


def test_failing_section_is_reported_not_silently_dropped():
    """區塊無聲消失會讓人誤以為自己沒有那些資料。"""

    class Boom:
        def get_json(self, path):
            if "player-loot" in path:
                raise RuntimeError("loot exploded")
            return SectionClient().get_json(path)

    html, data, skipped = cli.build_report(Boom(), AT2, keys=None)
    assert "<!DOCTYPE html>" in html          # 整頁仍產生
    titles = [t for t, _ in skipped]
    assert "造型碎片" in titles
    assert any("loot exploded" in r for _, r in skipped)


def test_parser_accepts_all_subcommand():
    args = cli.build_parser().parse_args(["all"])
    assert args.command == "all"


def test_parser_accepts_each_section_subcommand():
    for key in ("skins", "loot", "challenges", "matches", "ranked"):
        args = cli.build_parser().parse_args([key])
        assert args.command == key


def test_pause_swallows_eof_error_when_stdin_closed(monkeypatch):
    """以管道方式呼叫（stdin 已關閉）時 input() 會拋出 EOFError，
    _pause 本身不能因此而炸掉。"""

    def raise_eof(*a):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    cli._pause(quiet=False)  # 不應拋出例外


def test_quiet_still_reports_skipped_sections_to_stderr(monkeypatch, tmp_path, capsys):
    """--quiet 是 README 記載的腳本用法，失敗區塊的訊息不能因此消失——
    這是整個錯誤處理故事的機制，必須有端到端測試涵蓋，而不是只測
    build_report 本身。"""

    class Boom(SectionClient):
        def get_json(self, path):
            if "player-loot" in path:
                raise RuntimeError("loot exploded")
            return super().get_json(path)

    monkeypatch.setattr(cli.lcu.LcuClient, "connect", staticmethod(lambda: Boom()))
    code = cli.main(["all", "--quiet", "--no-open", "--output", str(tmp_path)])
    assert code == 0
    err = capsys.readouterr().err
    assert "造型碎片" in err
    assert "loot exploded" in err


def test_non_skins_subcommand_still_has_account_in_json(monkeypatch, tmp_path):
    """loot／challenges／matches／ranked 等子命令沒有機會打造型 endpoint，
    但 summary 的 current-summoner 呼叫已經拿得到帳號名稱，account key
    不該只在 skins 子命令才存在。"""
    monkeypatch.setattr(
        cli.lcu.LcuClient, "connect", staticmethod(lambda: SectionClient())
    )
    code = cli.main(["loot", "--quiet", "--no-open", "--output", str(tmp_path)])
    assert code == 0
    data = json.loads((tmp_path / "lol_skins.json").read_text(encoding="utf-8"))
    assert data.get("account", {}).get("summonerName") == "T"


def test_command_dispatch_uses_registered_handler(monkeypatch):
    """main() 必須依 args.command 查表決定要跑哪個處理函式，而不是
    永遠呼叫 _run_skins——否則未來多一個子命令就會被誤導向錯的處理函式。"""
    calls = []

    def fake_handler(args):
        calls.append(args)
        return 0

    monkeypatch.setitem(cli.COMMANDS, "skins", fake_handler)
    monkeypatch.setattr(cli, "_pause", lambda quiet: None)
    code = cli.main(["skins", "--quiet"])
    assert code == 0
    assert len(calls) == 1
