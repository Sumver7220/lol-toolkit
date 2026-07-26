"""LCU（League Client Update）API 連線層。

與功能無關：只負責找到客戶端、取得認證資訊、發出請求。
不認識造型、對戰紀錄等任何業務邏輯。
"""

import re
from typing import Any

import psutil
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLIENT_PROCESS_NAMES = ("LeagueClientUx.exe", "LeagueClientUx")

# LCU 的 HTTP Basic Auth 帳號固定為 riot
LCU_USERNAME = "riot"

CONNECT_TIMEOUT = 5
READ_TIMEOUT = 30

_PORT_RE = re.compile(r"--app-port=(\d+)")
_TOKEN_RE = re.compile(r"--remoting-auth-token=([a-zA-Z0-9_-]+)")


class LcuError(Exception):
    """所有 LCU 相關失敗的共同基底，訊息為可直接顯示給使用者的繁體中文。"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ClientNotFound(LcuError):
    def __init__(self) -> None:
        super().__init__("找不到《英雄聯盟》客戶端，請先開啟客戶端後再試一次。")


class ClientAccessDenied(LcuError):
    def __init__(self) -> None:
        super().__init__(
            "偵測到客戶端正在執行，但無法讀取它的連線資訊。\n"
            "這通常是因為客戶端以系統管理員權限執行，請用相同權限重新執行本工具。"
        )


class NotLoggedIn(LcuError):
    def __init__(self) -> None:
        super().__init__("已連上客戶端，但尚未完全登入。請登入並進入大廳後再試一次。")


class LcuRequestFailed(LcuError):
    pass


def parse_client_args(cmdline: list[str] | None) -> tuple[str, str] | None:
    """從客戶端進程的命令列參數取出 (port, token)，取不到時回傳 None。"""
    if not cmdline:
        return None
    joined = " ".join(cmdline)
    port = _PORT_RE.search(joined)
    token = _TOKEN_RE.search(joined)
    if port and token:
        return port.group(1), token.group(1)
    return None


def find_client(process_iter=None) -> tuple[str, str]:
    """掃描進程找出執行中的客戶端，回傳 (port, token)。

    失敗時區分兩種原因：完全找不到客戶端進程（ClientNotFound），
    或找到了卻讀不到它的命令列參數（ClientAccessDenied）。後者幾乎
    都是權限問題，訊息必須不同，否則使用者會被誤導。
    """
    process_iter = process_iter or psutil.process_iter
    found_client = False

    for proc in process_iter(["name", "cmdline"]):
        try:
            info = proc.info
            if info.get("name") not in CLIENT_PROCESS_NAMES:
                continue
            found_client = True
            parsed = parse_client_args(info.get("cmdline"))
            if parsed:
                return parsed
        except psutil.AccessDenied:
            # 無法得知這是不是客戶端，因此不設 found_client
            continue
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue

    raise ClientAccessDenied() if found_client else ClientNotFound()


class LcuClient:
    """對本機 LCU 介面發出請求。

    LCU 使用自我簽署憑證，因此關閉憑證驗證——連線目標是 127.0.0.1，
    不經過網路。
    """

    def __init__(self, port: str, token: str, session=None):
        self.base_url = f"https://127.0.0.1:{port}"
        self.session = session or requests.Session()
        self.session.auth = (LCU_USERNAME, token)
        self.session.verify = False

    @classmethod
    def connect(cls) -> "LcuClient":
        port, token = find_client()
        return cls(port, token)

    def get_json(self, path: str) -> Any:
        try:
            response = self.session.get(
                f"{self.base_url}{path}", timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise LcuRequestFailed(
                f"客戶端回應逾時（連線 {CONNECT_TIMEOUT} 秒／讀取 {READ_TIMEOUT} 秒）。"
                "請確認客戶端沒有卡住，稍後再試。"
            ) from None
        except requests.exceptions.RequestException as exc:
            raise LcuRequestFailed(f"與客戶端通訊時發生錯誤：{exc}") from exc
        except ValueError as exc:
            raise LcuRequestFailed(f"解析客戶端回傳的資料時發生錯誤：{exc}") from exc
