"""設計系統：頁面的 CSS 與 JS，以及跳脫工具。

這是視覺的唯一來源。新增功能區塊時只能引用既有的 semantic token
（--accent / --line / --text-muted / 間距與字級）並自行新增 component
token，不得新增 primitive 值，也不得引入第二個強調色。
"""

import html as _html

STYLE = """
/* ============================== PRIMITIVES ============================== */
:root{
  --ink-950:#08090b; --ink-900:#0d0f13; --ink-850:#12151b; --ink-800:#171b23;
  --ink-700:#1e232d; --ink-600:#2a3039; --ink-500:#3f4653;
  --ink-400:#767e8b; --ink-300:#98a0ac; --ink-200:#bcc2cb; --ink-50:#ecebe7;
  --gold-300:#e6d3a8; --gold-400:#d6ba81; --gold-500:#c8aa6e; --gold-700:#7d6229;
  --paper-50:#f7f5f1; --paper-100:#efece5; --paper-200:#e2ddd2; --paper-400:#a89f8d;
  --s-1:4px; --s-2:8px; --s-3:12px; --s-4:16px; --s-6:24px; --s-8:32px;
  --s-12:48px; --s-16:64px; --s-24:96px;
  --fs-micro:10.5px; --fs-xs:11.5px; --fs-sm:13px; --fs-base:14px; --fs-md:16px;
  --track-wide:.26em; --track-xwide:.42em;
  --font-display:"Bahnschrift","DIN Alternate","Segoe UI Variable Display",system-ui,sans-serif;
  --font-text:"Microsoft JhengHei","PingFang TC","Noto Sans TC",system-ui,sans-serif;
  --dur:.24s; --ease:cubic-bezier(.2,.7,.3,1);
}
/* ============================ SEMANTIC (dark) =========================== */
:root{
  --bg:var(--ink-950); --surface:var(--ink-900); --surface-2:var(--ink-850);
  --line:var(--ink-700); --line-soft:var(--ink-800);
  --text:var(--ink-50); --text-muted:var(--ink-300); --text-faint:var(--ink-400);
  --accent:var(--gold-500); --accent-quiet:var(--gold-400);
  --tile-bg:var(--ink-800); --grain:.035;
  --poster-glow:radial-gradient(120% 90% at 10% -10%,#1a1a22 0%,transparent 62%);
}
@media (prefers-color-scheme:light){
  :root{
    --bg:var(--paper-50); --surface:#fff; --surface-2:var(--paper-100);
    --line:var(--paper-200); --line-soft:var(--paper-100);
    --text:#15171c; --text-muted:#4f5661; --text-faint:#5d6470;
    --accent:var(--gold-700); --accent-quiet:var(--gold-700);
    --tile-bg:var(--paper-200); --grain:0;
    --poster-glow:radial-gradient(120% 90% at 10% -10%,#fffdf8 0%,transparent 62%);
  }
}
/* =========================== COMPONENT TOKENS =========================== */
:root{
  --poster-pad:var(--s-12); --poster-border:var(--line);
  --fig-gap:1px; --fig-pad:var(--s-6);
  --tile-gap:2px; --tile-min:132px;
  --bar-h:58px;
}

*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font-text);
  line-height:1.55;-webkit-font-smoothing:antialiased}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:99;
  opacity:var(--grain);background-image:radial-gradient(#fff 1px,transparent 1px);
  background-size:3px 3px}
.wrap{max-width:1680px;margin:0 auto;padding:0 var(--s-6)}
.num{font-family:var(--font-display);font-variant-numeric:tabular-nums;letter-spacing:-.03em}

/* --- 模式 A：海報頁首（外殼，所有功能共用） --- */
.poster{position:relative;margin-top:var(--s-8);border:1px solid var(--poster-border);
  background:var(--poster-glow),var(--surface);padding:var(--poster-pad) var(--s-12) var(--s-8);
  overflow:hidden}
.eyebrow{font-size:var(--fs-micro);letter-spacing:var(--track-xwide);text-transform:uppercase;
  color:var(--accent-quiet)}
.who{font-family:var(--font-display);font-size:clamp(38px,6.4vw,80px);font-weight:700;
  letter-spacing:-.035em;line-height:.96;margin:var(--s-3) 0 0}
.when{color:var(--text-faint);font-size:var(--fs-xs);letter-spacing:.12em;margin-top:var(--s-3)}
.hr{height:1px;background:linear-gradient(90deg,var(--accent),transparent 72%);
  margin:var(--s-8) 0 0;opacity:.55}

/* --- 模式 1：摘要數字帶 --- */
.figures{display:grid;grid-template-columns:repeat(auto-fit,minmax(146px,1fr));
  gap:var(--fig-gap);background:var(--line);border:1px solid var(--line);margin-top:var(--s-8)}
.fig{background:var(--surface);padding:var(--fig-pad) var(--s-4)}
.fig .n{font-family:var(--font-display);font-variant-numeric:tabular-nums;
  font-size:clamp(28px,3.2vw,44px);font-weight:700;letter-spacing:-.035em;line-height:1}
.fig.lead .n{color:var(--accent)}
.fig .l{font-size:var(--fs-micro);letter-spacing:var(--track-wide);text-transform:uppercase;
  color:var(--text-muted);margin-top:var(--s-2)}

/* --- 外殼：工具列 --- */
.bar{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--bg) 92%,transparent);
  backdrop-filter:blur(14px);border-bottom:1px solid var(--line);margin-top:var(--s-12)}
.bar .wrap{display:flex;gap:var(--s-3);align-items:center;min-height:var(--bar-h)}
#q{flex:1;background:var(--surface-2);border:1px solid var(--line);color:var(--text);
  padding:10px 14px;font:inherit;font-size:var(--fs-base);border-radius:2px}
#q:focus-visible{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
#q::placeholder{color:var(--text-faint)}
.btn{background:var(--surface-2);border:1px solid var(--line);color:var(--text-muted);
  padding:10px 14px;font:inherit;font-size:var(--fs-xs);letter-spacing:.1em;cursor:pointer;
  border-radius:2px;white-space:nowrap}
.btn:hover{color:var(--text);border-color:var(--accent)}
.btn:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.tally{font-family:var(--font-display);font-size:var(--fs-xs);letter-spacing:.16em;
  color:var(--text-muted);font-variant-numeric:tabular-nums;white-space:nowrap}

/* --- 英雄索引抽屜 --- */
.index{display:none;border-bottom:1px solid var(--line);background:var(--surface);
  padding:var(--s-4) 0 var(--s-6)}
.index.open{display:block}
.index .wrap{display:flex;flex-wrap:wrap;gap:var(--s-1)}
.ix{font-size:var(--fs-sm);color:var(--text-muted);border:1px solid var(--line-soft);
  background:none;padding:4px 9px;cursor:pointer;font-family:inherit;border-radius:2px}
.ix:hover{color:var(--accent);border-color:var(--accent)}
.ix:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.ix i{font-style:normal;color:var(--text-faint);margin-left:5px;font-size:var(--fs-xs)}

/* --- 模式 2：圖像牆 --- */
.wall{display:grid;grid-template-columns:repeat(auto-fill,minmax(var(--tile-min),1fr));
  gap:var(--tile-gap);padding-top:var(--tile-gap)}
.t{position:relative;aspect-ratio:1;background:var(--tile-bg);overflow:hidden;display:block;
  border:0;padding:0;width:100%;cursor:default;text-align:left;color:inherit;font:inherit}
.t img{width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .45s var(--ease)}
.t:hover img,.t:focus-visible img{transform:scale(1.07)}
.t:focus-visible{outline:2px solid var(--accent);outline-offset:-2px;z-index:2}
.cap{position:absolute;inset:auto 0 0 0;padding:26px var(--s-2) 7px;
  background:linear-gradient(transparent,rgba(4,5,7,.94) 60%);
  opacity:0;transition:opacity var(--dur);pointer-events:none}
.t:hover .cap,.t:focus-visible .cap{opacity:1}
.cap .s{font-size:var(--fs-xs);line-height:1.25;display:block;color:#f2f0ec}
.cap .c{font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold-400);
  display:block;margin-top:2px}
.t.ch::after{content:"";position:absolute;top:6px;right:6px;width:5px;height:5px;
  background:var(--accent);transform:rotate(45deg)}
.t.dead{display:flex;align-items:center;justify-content:center;padding:var(--s-2);
  text-align:center}
.t.dead img{display:none}
.t.dead .cap{position:static;opacity:1;background:none;padding:0}
.t.dead .cap .s{color:var(--text-muted)}
.t.dead .cap .c{color:var(--text-faint)}
.hide{display:none!important}

/* --- 模式 5：空狀態 --- */
.empty{padding:var(--s-16) 0;color:var(--text-muted);font-size:var(--fs-base);display:none}
.empty.on{display:block}
.bare{padding:var(--s-12) 0 var(--s-8);border-top:1px solid var(--line);margin-top:var(--tile-gap)}
.bare h3{font-size:var(--fs-micro);letter-spacing:var(--track-wide);text-transform:uppercase;
  color:var(--text-muted);font-weight:400;margin:0 0 var(--s-4)}
.chips{display:flex;flex-wrap:wrap;gap:var(--s-1)}
.chip{font-size:var(--fs-sm);color:var(--text-faint);border:1px solid var(--line-soft);
  padding:4px 9px;border-radius:2px}
footer{padding:var(--s-8) 0 var(--s-16);color:var(--text-faint);font-size:var(--fs-xs);
  letter-spacing:.1em;border-top:1px solid var(--line-soft);margin-top:var(--s-8)}

/* --- 窄螢幕：海報內距收窄，避免把數字帶擠成單欄 --- */
@media (max-width:640px){
  .wrap{padding:0 var(--s-4)}
  .poster{padding:var(--s-8) var(--s-5,20px) var(--s-6)}
  .figures{grid-template-columns:repeat(auto-fit,minmax(104px,1fr))}
  .bar .wrap{flex-wrap:wrap;padding-top:var(--s-2);padding-bottom:var(--s-2)}
  #q{flex:1 1 100%}
  .tally{margin-left:auto}
}

/* --- 區塊標題 --- */
.block{margin:var(--s-16) 0 0}
.block-h{font-family:var(--font-display);font-size:var(--fs-md);font-weight:600;
  letter-spacing:.04em;margin:0 0 var(--s-4);padding-bottom:var(--s-3);
  border-bottom:1px solid var(--line);display:flex;align-items:baseline;gap:var(--s-3)}
.block-h .sub{font-family:var(--font-text);font-size:var(--fs-xs);font-weight:400;
  color:var(--text-muted);letter-spacing:.02em}

/* --- 模式 6：進度指標 --- */
.progs{display:grid;gap:var(--s-4);grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.prog{border:1px solid var(--line);padding:var(--s-4);background:var(--surface)}
.prog-h{display:flex;justify-content:space-between;align-items:baseline;gap:var(--s-3)}
.prog-n{font-size:var(--fs-sm)}
.prog-lv{font-family:var(--font-display);font-size:var(--fs-micro);
  letter-spacing:var(--track-wide);color:var(--accent)}
.prog-bar{height:3px;background:var(--line-soft);margin:var(--s-3) 0 var(--s-2);
  overflow:hidden}
.prog-bar i{display:block;height:100%;background:var(--accent)}
.prog-v{font-family:var(--font-display);font-size:var(--fs-xs);color:var(--text-faint);
  font-variant-numeric:tabular-nums}

/* --- 模式 7：時間軸清單／空狀態 --- */
.events{list-style:none;margin:0;padding:0;border-top:1px solid var(--line-soft)}
.ev{display:grid;grid-template-columns:44px 1fr auto auto auto;gap:var(--s-4);
  align-items:center;padding:var(--s-3) var(--s-2);
  border-bottom:1px solid var(--line-soft);font-size:var(--fs-sm)}
.ev-r{font-size:var(--fs-xs);letter-spacing:.1em;text-align:center;padding:2px 0}
.ev.win .ev-r{color:var(--accent)}
.ev.loss .ev-r{color:var(--text-faint)}
.ev-k,.ev-d,.ev-t{font-family:var(--font-display);font-size:var(--fs-xs);
  color:var(--text-muted);font-variant-numeric:tabular-nums}
.ranks{display:grid;gap:var(--s-4);grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.rank{border:1px solid var(--line);padding:var(--s-4);background:var(--surface)}
.rank-q{font-size:var(--fs-xs);letter-spacing:var(--track-wide);color:var(--text-faint)}
.rank-t{font-family:var(--font-display);font-size:var(--fs-md);margin:var(--s-2) 0}
.rank-lp{color:var(--accent);font-size:var(--fs-xs)}
.rank-w{font-size:var(--fs-xs);color:var(--text-muted)}
.note{color:var(--text-muted);font-size:var(--fs-sm);margin:var(--s-4) 0 0}
@media (max-width:640px){.ev{grid-template-columns:40px 1fr auto;row-gap:var(--s-1)}
  .ev-d,.ev-t{display:none}}
"""

SCRIPT = """const TOTAL=__TOTAL__;
const q=document.getElementById('q');
if(q){
 const tiles=[...document.querySelectorAll('#skin-wall .t')],
  tally=document.getElementById('tally'),none=document.getElementById('none'),
  idx=document.getElementById('index'),toggle=document.getElementById('idxbtn');
 function apply(v){v=v.trim().toLowerCase();let n=0;
  for(const t of tiles){const hit=!v||t.dataset.k.includes(v);
   t.classList.toggle('hide',!hit);if(hit)n++}
  tally.textContent=n.toLocaleString()+' / TOTAL'.replace('TOTAL',TOTAL.toLocaleString());
  none.classList.toggle('on',n===0);}
 q.addEventListener('input',()=>apply(q.value));
 toggle.addEventListener('click',()=>{const o=idx.classList.toggle('open');
  toggle.setAttribute('aria-expanded',o)});
 idx.addEventListener('click',ev=>{const b=ev.target.closest('.ix');if(!b)return;
  q.value=b.dataset.n;apply(q.value);idx.classList.remove('open');
  toggle.setAttribute('aria-expanded','false');
  document.querySelector('.bar').scrollIntoView({block:'start'});});
}
"""


def esc(value) -> str:
    """跳脫所有取自 API 的字串。quote=True 是必要的——召喚師名稱是
    使用者自訂的，未跳脫引號可從屬性值逸出。"""
    return _html.escape(str(value), quote=True)
