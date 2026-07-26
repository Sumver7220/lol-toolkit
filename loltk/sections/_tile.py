"""圖像網格的單一格子。

造型、造型碎片以及日後任何圖像網格共用這一份，避免各區塊各自複製一份
形狀相同的標記。
"""

from ..skins.render import cdn_url
from ..theme import esc


def tile(*, name: str, sub: str = "", tile_path: str = "", search_key: str = "",
         extra_class: str = "") -> str:
    """產生一格。

    name      主標（造型名）
    sub       副標（英雄名或重複數量），可省略
    tile_path LCU 資產路徑；為空時不輸出 img，只顯示文字
    search_key data-k 的內容，供前端篩選；為空時取 name
    extra_class 追加的 class，例如炫彩的 "ch"
    """
    url = cdn_url(tile_path)
    cls = f"t {extra_class}".strip()
    img = (
        f'<img src="{esc(url)}" alt="" loading="lazy" '
        f"onerror=\"this.closest('.t').classList.add('dead')\">"
        if url
        else ""
    )
    # 字幕永遠疊在深色漸層上，因此固定色而非 token（見 Global Constraints）
    sub_html = f'<span class="c">{esc(sub)}</span>' if sub else ""
    key = esc((search_key or name).lower())
    return (
        f'<button class="{cls}" type="button" data-k="{key}">{img}'
        f'<span class="cap"><span class="s">{esc(name)}</span>{sub_html}</span>'
        f"</button>"
    )
