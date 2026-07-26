"""造型牆區塊。

486 張 tile 連續鋪排，不依英雄分組——173 個分組平均只有 2.8 個造型，
每個分組一個容器會讓網格每行約 57% 是空的。分組資訊改由 tile 字幕、
搜尋與英雄索引抽屜三個機制承擔。
"""

from ..skins.inventory import Inventory, build_inventory
from ..skins.render import champion_dicts
from ..theme import esc
from ._tile import tile

KEY = "skins"
TITLE = "造型收藏"

SESSION_PATH = "/lol-login/v1/session"


def fetch(client) -> Inventory | None:
    # 不要 try/except——例外由 sections.safe_fetch 統一攔截
    session = client.get_json(SESSION_PATH)
    summoner_id = session.get("summonerId")
    if not summoner_id:
        return None
    raw = client.get_json(
        f"/lol-champions/v1/inventories/{summoner_id}/skins-minimal"
    )
    return build_inventory(raw, session.get("username") or "未知帳號", summoner_id)


def to_dict(inv: Inventory | None) -> dict | None:
    """只回傳 champions 清單。

    刻意不呼叫 skins.render.to_dict——那會回傳一份完整文件（含自己的
    schemaVersion、generatedAt、account），塞進頂層區塊後會變成巢狀
    重複。帳號與版本資訊由 cli.build_report 統一在頂層產生。
    """
    if inv is None:
        return None

    return {"champions": champion_dicts(inv)}


def to_html(inv: Inventory | None) -> str:
    if inv is None:
        return ""

    with_skins = [c for c in inv.champions if c.skins]
    bare = [c for c in inv.champions if not c.skins]

    tiles = "".join(
        tile(
            name=s.name,
            sub=c.name,
            tile_path=s.tile_path,
            search_key=f"{c.name} {s.name}",
            extra_class="ch" if s.has_chromas else "",
        )
        for c in with_skins
        for s in c.skins
    )
    index = "".join(
        f'<button class="ix" type="button" data-n="{esc(c.name.lower())}">'
        f"{esc(c.name)}</button>"
        for c in with_skins
    )
    total = inv.skin_count

    chips = ""
    if bare:
        items = "".join(f'<span class="chip">{esc(c.name)}</span>' for c in bare)
        chips = (
            f'<section class="bare"><h3>尚無其他造型 · {len(bare)} 位英雄</h3>'
            f'<div class="chips">{items}</div></section>'
        )

    return f"""<div class="bar"><div class="wrap">
<input id="q" type="search" placeholder="搜尋英雄或造型…" autocomplete="off"
 aria-label="搜尋英雄或造型">
<button class="btn" id="idxbtn" type="button" aria-expanded="false" aria-controls="index">
英雄索引</button>
<span class="tally num" id="tally">{total:,} / {total:,}</span>
</div></div>
<div class="index" id="index"><div class="wrap">{index}</div></div>
<div class="wrap">
<div class="wall">{tiles}</div>
<div class="empty" id="none">找不到符合的英雄或造型。</div>
{chips}
</div>"""
