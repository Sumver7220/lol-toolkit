"""命令列介面。

唯一知道檔案路徑、使用者訊息與瀏覽器的一層。
"""

import argparse
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from . import __version__, lcu, page
from .sections import safe_fetch
from .sections import challenges, loot, matches, ranked, skins as skins_section
from .sections import summary as summary_section
from .skins.render import SCHEMA_VERSION

JSON_NAME = "lol_skins.json"
HTML_NAME = "lol_skins.html"

# 子命令名稱與 JSON 頂層 key 皆取自各模組的 KEY。順序即為區塊在頁面上
# 出現的順序。
SECTIONS = [skins_section, loot, challenges, matches, ranked]


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

    for name, help_text in [("all", "產生全部區塊")] + [
        (s.KEY, f"只產生{s.TITLE}") for s in SECTIONS
    ]:
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("--output", type=Path, default=None, help="輸出目錄")
        group = sub.add_mutually_exclusive_group()
        group.add_argument("--json-only", action="store_true", help="只產生 JSON")
        group.add_argument("--html-only", action="store_true", help="只產生 HTML")
        sub.add_argument("--no-open", action="store_true", help="不自動開啟瀏覽器")
        sub.add_argument("--quiet", action="store_true", help="只輸出錯誤")
    return parser


def build_report(client, generated_at: datetime, keys: list[str] | None = None):
    """取得所有（或指定）區塊，回傳 (html, payload, skipped)。

    skipped 為 [(TITLE, 失敗原因)]，由呼叫端告知使用者——區塊無聲消失
    會讓人誤以為是自己沒有那些資料。
    """
    chosen = [s for s in SECTIONS if keys is None or s.KEY in keys]

    summary_data, summary_errors = summary_section.fetch(client)
    figures = []
    fragments = []
    skipped = [(summary_section.TITLE, err) for err in summary_errors]
    payload = {"schemaVersion": SCHEMA_VERSION, "generatedAt": generated_at.isoformat()}

    skins_data = None
    for section in chosen:
        data, error = safe_fetch(section, client)
        if error:
            skipped.append((section.TITLE, error))
        # skins 是唯一需要特殊處理的區塊：它的 fetch 回傳一個 Inventory
        # 物件（而非其他區塊慣用的 list/dict），且海報卡的造型／英雄數字
        # 與 JSON 的 champions 提升都得靠它——這份資料形狀與其他區塊差
        # 太多，無法用通用機制概括，因此保留這個特例。
        if section.KEY == "skins":
            skins_data = data
        fragment = section.to_html(data)
        if not fragment and not error:
            # 任何區塊都可以「選擇性」提供 empty_html()，用來在無資料
            # 但非錯誤時顯示說明（例如排位：未打排位是常態而非異常）。
            # 用 getattr 而非硬編區塊名稱，新增區塊時不必回來改這裡。
            empty_html = getattr(section, "empty_html", None)
            if empty_html:
                fragment = empty_html()
        if fragment:
            fragments.append(fragment)
        as_dict = section.to_dict(data)
        if as_dict is not None:
            payload[section.KEY] = as_dict

    account_name = summary_data.get("account_name")
    account_id = summary_data.get("account_id")

    if skins_data is not None:
        figures.append(page.Figure(f"{skins_data.skin_count:,}", "造型", lead=True))
        figures.append(page.Figure(f"{skins_data.champion_count:,}", "英雄"))
        payload["account"] = {
            "summonerName": skins_data.summoner_name,
            "summonerId": skins_data.summoner_id,
        }
        # champions 提到頂層並移除巢狀的 skins key，維持與 schema 1 相同的形狀
        payload["champions"] = payload.pop("skins", {}).get("champions", [])
    elif account_name:
        # 非 skins 子命令（loot／challenges／matches／ranked）沒有機會
        # 打造型 endpoint，但 summary 這次呼叫已經拿到帳號名稱——
        # account key 不該只在 skins 子命令才存在。
        payload["account"] = {"summonerName": account_name, "summonerId": account_id}

    figures.extend(summary_section.figures(summary_data))
    summary_dict = summary_section.to_dict(summary_data)
    if summary_dict:
        payload["summary"] = summary_dict

    # 優先用 summary 取得的帳號名稱，skins_data 作為後備——非 skins
    # 子命令沒有 skins_data，若又只看它就會永遠顯示「未知帳號」。
    name = account_name or (skins_data.summoner_name if skins_data else None) or "未知帳號"
    total = skins_data.skin_count if skins_data else 0

    html = page.render_page(
        summoner_name=name,
        generated_at=generated_at,
        figures=figures,
        sections=fragments,
        total_tiles=total,
    )
    return html, payload, skipped


def write_outputs(
    html: str,
    payload: dict,
    output_dir: Path,
    *,
    json_only: bool,
    html_only: bool,
) -> list[Path]:
    """把已產生的內容寫成檔案。不負責產生內容。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    if not html_only:
        path = output_dir / JSON_NAME
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        written.append(path)
    if not json_only:
        path = output_dir / HTML_NAME
        path.write_text(html, encoding="utf-8")
        written.append(path)
    return written


def _pause(quiet: bool) -> None:
    if quiet:
        return
    try:
        input("按 Enter 鍵後離開...")
    except EOFError:
        # stdin 被關閉（例如以管道方式呼叫）時 input() 會拋出此例外，
        # 這種情況下沒有人在等待暫停，直接放行即可。
        pass


def _configure_stdout() -> None:
    """避免非 ASCII 帳號名在 cp950 終端機觸發 UnicodeEncodeError。"""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _run(args) -> int:
    client = lcu.LcuClient.connect()
    if not args.quiet:
        print("已連上客戶端，正在讀取資料...")

    keys = None if args.command == "all" else [args.command]
    html, payload, skipped = build_report(
        client, datetime.now().astimezone(), keys=keys
    )

    output_dir = (args.output or default_output_dir()).resolve()
    written = write_outputs(
        html, payload, output_dir,
        json_only=args.json_only, html_only=args.html_only,
    )

    if not args.quiet:
        account = payload.get("account", {})
        print(f"\n帳號：{account.get('summonerName', '未知')}")
        for path in written:
            print(f"已輸出：{path}")

    # 略過的區塊一律回報，即使 --quiet——使用者需要知道少了什麼
    for title, reason in skipped:
        print(f"已略過「{title}」：{reason}", file=sys.stderr)

    html_files = [p for p in written if p.suffix == ".html"]
    if html_files and not args.no_open:
        try:
            webbrowser.open(html_files[0].as_uri())
        except OSError as exc:
            print(
                f"檔案已產生，但無法自動開啟瀏覽器：{exc}\n"
                f"請手動開啟：{html_files[0]}",
                file=sys.stderr,
            )
    return 0


# 子命令名稱 -> 處理函式。全部指向同一個 _run，實際差異只在
# keys 篩選；未來新增子命令時只需在 build_parser／SECTIONS 登記。
COMMANDS = {name: _run for name in ["all"] + [s.KEY for s in SECTIONS]}


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    argv = list(sys.argv[1:] if argv is None else argv)

    # 雙擊 exe 的使用者不該看到 argparse 的 help 畫面
    if not argv and getattr(sys, "frozen", False):
        argv = ["all"]

    args = build_parser().parse_args(argv)
    quiet = getattr(args, "quiet", False)

    code = 1
    try:
        handler = COMMANDS[args.command]
        code = handler(args)
    except lcu.LcuError as exc:
        print(exc.message, file=sys.stderr)
        code = 1
    except OSError as exc:
        print(f"寫入輸出檔時發生錯誤：{exc}", file=sys.stderr)
        code = 1
    except Exception as exc:
        # 保底處理：任何未預期的例外都不能讓程式在雙擊執行時
        # 瞬間關閉視窗——至少要印出訊息並暫停讓使用者看到。
        print(f"發生未預期的錯誤：{exc}", file=sys.stderr)
        code = 1
    finally:
        _pause(quiet)
    return code
