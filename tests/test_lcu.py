import psutil
import pytest
import requests

from loltk import lcu


def test_parse_client_args_extracts_port_and_token():
    cmdline = [
        "LeagueClientUx.exe",
        "--app-port=54321",
        "--remoting-auth-token=abcDEF-123_xyz",
        "--other-flag=1",
    ]
    assert lcu.parse_client_args(cmdline) == ("54321", "abcDEF-123_xyz")


def test_parse_client_args_returns_none_when_cmdline_is_none():
    assert lcu.parse_client_args(None) is None


def test_parse_client_args_returns_none_when_port_missing():
    assert lcu.parse_client_args(["LeagueClientUx.exe", "--remoting-auth-token=abc"]) is None


def test_parse_client_args_returns_none_when_token_missing():
    assert lcu.parse_client_args(["LeagueClientUx.exe", "--app-port=54321"]) is None


class FakeProc:
    """模擬 psutil.Process，info 取值時可拋出例外。"""

    def __init__(self, name, cmdline=None, raises=None):
        self._info = {"name": name, "cmdline": cmdline}
        self._raises = raises

    @property
    def info(self):
        if self._raises:
            raise self._raises
        return self._info


def fake_iter(procs):
    def _iter(attrs=None):
        return iter(procs)

    return _iter


def test_find_client_returns_port_and_token():
    procs = [
        FakeProc("chrome.exe", ["chrome"]),
        FakeProc("LeagueClientUx.exe", ["x", "--app-port=1234", "--remoting-auth-token=tok"]),
    ]
    assert lcu.find_client(process_iter=fake_iter(procs)) == ("1234", "tok")


def test_find_client_raises_not_found_when_no_client_process():
    procs = [FakeProc("chrome.exe", ["chrome"])]
    with pytest.raises(lcu.ClientNotFound):
        lcu.find_client(process_iter=fake_iter(procs))


def test_find_client_raises_access_denied_when_cmdline_unreadable():
    procs = [FakeProc("LeagueClientUx.exe", None)]
    with pytest.raises(lcu.ClientAccessDenied):
        lcu.find_client(process_iter=fake_iter(procs))


def test_find_client_reports_not_found_when_process_info_unreadable():
    """連進程名稱都讀不到時，無從判斷它是不是客戶端。

    這種情況只能回報「找不到」——猜測它是客戶端並顯示權限訊息，會在
    使用者根本沒開客戶端時給出誤導性的指示。
    """
    procs = [FakeProc("LeagueClientUx.exe", raises=psutil.AccessDenied())]
    with pytest.raises(lcu.ClientNotFound):
        lcu.find_client(process_iter=fake_iter(procs))


def test_find_client_skips_dead_processes_and_keeps_searching():
    procs = [
        FakeProc("whatever", raises=psutil.NoSuchProcess(1)),
        FakeProc("LeagueClientUx.exe", ["x", "--app-port=99", "--remoting-auth-token=t"]),
    ]
    assert lcu.find_client(process_iter=fake_iter(procs)) == ("99", "t")


class FakeResponse:
    def __init__(self, payload=None, status=200, raise_exc=None):
        self._payload = payload
        self.status_code = status
        self._raise_exc = raise_exc

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        if self._raise_exc:
            raise self._raise_exc
        return self._payload


class FakeSession:
    def __init__(self, response=None, exc=None):
        self.response = response
        self.exc = exc
        self.calls = []
        self.auth = None
        self.verify = True

    def get(self, url, timeout=None):
        self.calls.append((url, timeout))
        if self.exc:
            raise self.exc
        return self.response


def test_client_get_json_returns_payload_and_sets_timeout():
    session = FakeSession(FakeResponse({"ok": True}))
    client = lcu.LcuClient("1234", "tok", session=session)
    assert client.get_json("/some/path") == {"ok": True}
    url, timeout = session.calls[0]
    assert url == "https://127.0.0.1:1234/some/path"
    assert timeout == (lcu.CONNECT_TIMEOUT, lcu.READ_TIMEOUT)


def test_client_sets_basic_auth_and_disables_verify():
    session = FakeSession(FakeResponse({}))
    lcu.LcuClient("1", "tok", session=session)
    assert session.auth == ("riot", "tok")
    assert session.verify is False


def test_client_get_json_wraps_timeout_error():
    session = FakeSession(exc=requests.exceptions.Timeout())
    client = lcu.LcuClient("1", "t", session=session)
    with pytest.raises(lcu.LcuRequestFailed) as err:
        client.get_json("/x")
    assert "逾時" in err.value.message


def test_client_get_json_wraps_invalid_json():
    session = FakeSession(FakeResponse(raise_exc=ValueError("bad json")))
    client = lcu.LcuClient("1", "t", session=session)
    with pytest.raises(lcu.LcuRequestFailed) as err:
        client.get_json("/x")
    assert "解析" in err.value.message
