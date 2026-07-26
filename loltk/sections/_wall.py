"""圖像網格的外殼。

折疊行為屬於 .wall 這個版面模式本身，不是造型區塊的特例——造型、
碎片以及日後任何圖像牆共用這一份，新增功能時不必重新設計外觀。

實際折不折由 theme.SCRIPT 依視窗高度決定（見 spec 第四節）；這裡
只負責產生標記，JS 停用時就是一面完整攤開的牆。
"""

from ..theme import esc


def wall(*, tiles: str, wall_id: str, expand_label: str) -> str:
    """產生一面圖像牆。

    tiles        已產生的 tile HTML 串接
    wall_id      牆的唯一 id，供同層展開按鈕的 aria-controls 指向
    expand_label 展開按鈕的文字；量詞因區塊而異（個造型／個碎片），
                 因此由呼叫端提供而非寫死在這裡
    """
    return (
        f'<div class="wall-box">'
        f'<div class="wall" id="{esc(wall_id)}">{tiles}</div>'
        f'<button class="more" type="button" aria-expanded="false" '
        f'aria-controls="{esc(wall_id)}">{esc(expand_label)}</button>'
        f"</div>"
    )
