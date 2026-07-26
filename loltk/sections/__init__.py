"""功能區塊。

每個模組提供完全相同的三個函式，`cli.py` 只依這個契約運作：

    KEY: str            區塊識別，同時是 CLI 子命令名與 JSON 頂層 key
    TITLE: str          顯示標題（繁體中文）

    fetch(client)       向 LCU 取資料，無資料時回傳 None。
                        **不要自己 try/except**——讓例外往外拋。
    to_dict(data)       轉成 JSON 可序列化結構；data 為 None 時回傳 None。
    to_html(data)       回傳 HTML 片段；data 為 None 時回傳空字串。

例外的隔離邊界主要只有 safe_fetch 一處，把它收在這裡而不是散落在
六個 fetch 裡，既避免六份重複的例外處理，也讓「哪裡會吞掉錯誤」
集中在一個地方要稽核。

唯一的例外是 summary：它的三個 endpoint 是逐欄位容錯（單一 endpoint
失敗不該讓其他兩個數字也消失），這與逐區塊層次不同，因此有自己的
_get()。但它一樣不能靜默——summary.fetch() 回傳 (data, errors)，
errors 由 cli.build_report 併入 skipped，稽核時記得一併檢查。
"""

from ..lcu import LcuError


def safe_fetch(section, client) -> tuple[object | None, str | None]:
    """取得一個區塊的資料，回傳 (data, error)。

    任何區塊失敗都只讓該區塊消失，不影響其他區塊與整頁產生。但失敗
    原因會一併回傳，由 cli 告知使用者——區塊無聲消失會讓人誤以為是
    自己沒有那些資料。
    """
    try:
        return section.fetch(client), None
    except LcuError as exc:
        return None, exc.message
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
