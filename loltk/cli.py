"""命令列介面。

唯一知道檔案路徑、使用者訊息與瀏覽器的一層。
"""

import argparse
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from . import __version__, lcu
from .skins import render
from .skins.inventory import Inventory, build_inventory

JSON_NAME = "lol_skins.json"
HTML_NAME = "lol_skins.html"

SESSION_PATH = "/lol-login/v1/session"


def default_output_dir() -> Path:
    """輸出目錄取程式所在位置，而非 cwd。

    打包成 exe 後從捷徑或其他資料夾啟動時，cwd 可能是任何地方，
    輸出檔會掉在使用者找不到的位置。
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loltk",
        description="透過 LCU API 讀取《英雄聯盟》客戶端資料的小工具箱。",
    )
    parser.add_argument("--version", action="version", version=f"loltk {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    skins = subparsers.add_parser("skins", help="匯出已擁有的造型")
    skins.add_argument("--output", type=Path, default=None, help="輸出目錄")
    exclusive = skins.add_mutually_exclusive_group()
    exclusive.add_argument("--json-only", action="store_true", help="只產生 JSON")
    exclusive.add_argument("--html-only", action="store_true", help="只產生 HTML")
    skins.add_argument("--no-open", action="store_true", help="不自動開啟瀏覽器")
    skins.add_argument("--quiet", action="store_true", help="只輸出錯誤")
    return parser


def fetch_inventory(client) -> Inventory:
    session = client.get_json(SESSION_PATH)
    summoner_id = session.get("summonerId")
    if not summoner_id:
        raise lcu.NotLoggedIn()
    raw = client.get_json(
        f"/lol-champions/v1/inventories/{summoner_id}/skins-minimal"
    )
    return build_inventory(raw, session.get("username") or "未知帳號", summoner_id)


def write_outputs(
    inventory: Inventory,
    output_dir: Path,
    generated_at: datetime,
    *,
    json_only: bool,
    html_only: bool,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    if not html_only:
        path = output_dir / JSON_NAME
        path.write_text(
            render.to_json(inventory, generated_at), encoding="utf-8"
        )
        written.append(path)
    if not json_only:
        path = output_dir / HTML_NAME
        path.write_text(
            render.to_html(inventory, generated_at), encoding="utf-8"
        )
        written.append(path)
    return written


def _pause(quiet: bool) -> None:
    if not quiet:
        input("按 Enter 鍵後離開...")


def _configure_stdout() -> None:
    """避免非 ASCII 帳號名在 cp950 終端機觸發 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _run_skins(args) -> int:
    client = lcu.LcuClient.connect()
    if not args.quiet:
        print("已連上客戶端，正在讀取資料...")

    inventory = fetch_inventory(client)
    output_dir = (args.output or default_output_dir()).resolve()
    written = write_outputs(
        inventory,
        output_dir,
        datetime.now().astimezone(),
        json_only=args.json_only,
        html_only=args.html_only,
    )

    if not args.quiet:
        print(f"\n帳號：{inventory.summoner_name}")
        print(
            f"共 {inventory.champion_count} 位英雄、"
            f"{inventory.skin_count} 個造型（不含基礎造型）"
        )
        for path in written:
            print(f"已輸出：{path}")

    html_files = [p for p in written if p.suffix == ".html"]
    if html_files and not args.no_open:
        try:
            webbrowser.open(html_files[0].as_uri())
        except OSError as exc:
            print(
                f"檔案已產生，但無法自動開啟瀏覽器：{exc}\n"
                f"請手動開啟：{html_files[0]}"
            )
    return 0


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    argv = list(sys.argv[1:] if argv is None else argv)

    # 雙擊 exe 的使用者不該看到 argparse 的 help 畫面
    if not argv and getattr(sys, "frozen", False):
        argv = ["skins"]

    args = build_parser().parse_args(argv)
    quiet = getattr(args, "quiet", False)

    try:
        code = _run_skins(args)
    except lcu.LcuError as exc:
        print(exc.message)
        _pause(quiet)
        return 1
    except OSError as exc:
        print(f"寫入輸出檔時發生錯誤：{exc}")
        _pause(quiet)
        return 1

    _pause(quiet)
    return code
