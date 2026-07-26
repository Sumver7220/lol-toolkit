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
  --nav-h:44px;
  --more-h:44px;
}

*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font-text);
  line-height:1.55;-webkit-font-smoothing:antialiased}
/* 單一子命令的頁面不輸出 <nav>（見 page._nav_html），.bar 卻無條件
   釘在 top:var(--nav-h)，若不歸零會在搜尋列上方留下一條死帶，讓
   造型 tile 從上面穿過去。body 有沒有 has-nav 由 page.render_page
   依導覽列是否輸出來決定。 */
body:not(.has-nav){--nav-h:0px}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:99;
  opacity:var(--grain);background-image:radial-gradient(#fff 1px,transparent 1px);
  background-size:3px 3px}
.wrap{max-width:1680px;margin:0 auto;padding:0 var(--s-6)}
.num{font-family:var(--font-display);font-variant-numeric:tabular-nums;letter-spacing:-.03em}

/* --- 外殼：全站區塊導覽 --- */
/* z-index 必須高於 .bar 的 40，否則造型區塊的搜尋列會蓋住導覽列。 */
.nav{position:sticky;top:0;z-index:50;
  background:color-mix(in srgb,var(--bg) 92%,transparent);
  backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;gap:var(--s-2);align-items:stretch;height:var(--nav-h)}
.nv{display:flex;align-items:center;gap:6px;padding:0 var(--s-3);
  color:var(--text-muted);text-decoration:none;font-size:var(--fs-sm);
  border-bottom:2px solid transparent;white-space:nowrap}
.nv:hover{color:var(--text)}
/* 作用中項目的金線是必要的非顏色線索，不能只靠文字顏色區分。 */
.nv.on{color:var(--text);border-bottom-color:var(--accent)}
.nv:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.nv b{font-family:var(--font-display);font-variant-numeric:tabular-nums;
  font-weight:400;font-size:var(--fs-xs);color:var(--text-faint)}
.nv.on b{color:var(--accent)}
.anchor{scroll-margin-top:var(--nav-h)}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;
  overflow:hidden;clip-path:inset(50%);white-space:nowrap;border:0}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}

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
/* scroll-margin-top：英雄索引挑完會捲回這條列，沒有這條偏移落點會被
   導覽列蓋住。（尚未釘住時才有作用——已釘住的 sticky 元素本來就在位置上。） */
.bar{position:sticky;top:var(--nav-h);z-index:40;scroll-margin-top:var(--nav-h);
  background:color-mix(in srgb,var(--bg) 92%,transparent);
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

/* --- 圖像牆折疊（屬於 .wall 模式本身，所有牆共用） --- */
.wall-box{position:relative;scroll-margin-top:var(--nav-h)}
.wall-box.folded .wall{overflow:hidden}
/* 遮罩疊在 .wall-box 而非 .wall 上——後者裁切內容。bottom 讓開按鈕高度。 */
.wall-box.folded::after{content:"";position:absolute;left:0;right:0;
  bottom:var(--more-h);height:var(--s-24);pointer-events:none;
  background:linear-gradient(transparent,var(--bg))}
.more{display:block;width:100%;height:var(--more-h);background:var(--surface-2);
  border:1px solid var(--line);border-top:0;color:var(--text-muted);
  font:inherit;font-size:var(--fs-xs);letter-spacing:.1em;cursor:pointer;
  border-radius:0 0 2px 2px}
.more:hover{color:var(--text);border-color:var(--accent)}
.more:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
/* .more 是 display:block，不補這條的話 hidden 屬性會被蓋掉 */
.more[hidden]{display:none}

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
  .nv b{display:none}
  .nv{padding:0 var(--s-2)}
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

/* --- 造型收藏區塊外殼：讓 .bar 的 sticky 只在本區塊內生效 --- */
/* .bar 的 containing block 原本是 <body>，會一路釘到頁尾。包一層
   .sec-skins 之後，sticky 只會黏到這個容器的下緣，捲到後續區塊
   （挑戰進度、對戰紀錄……）時就會正常隨頁面捲走，不再疊在上方。 */
.sec-skins{position:relative}
"""

SCRIPT = """const TOTAL=__TOTAL__;
const NAVH=parseFloat(getComputedStyle(document.documentElement)
 .getPropertyValue('--nav-h'))||0;
const navs=[...document.querySelectorAll('.nv')];
if(navs.length){
 const byId=new Map(navs.map(a=>[a.getAttribute('href').slice(1),a]));
 const anchors=[...document.querySelectorAll('.anchor')];
 const seen=new Set();
 /* 頁尾露出＝已經捲到底。最後一個區塊若比 60% 視窗高矮（例如排位的空狀態
    只有一行），它永遠進不了下面那條觀察帶，金線會卡在倒數第二個區塊。
    捲到底時使用者看的就是最後一個區塊，這個語意比「誰進了觀察帶」更貼近
    實際，因此用它覆蓋。 */
 let atEnd=false;
 const mark=()=>{
  let cur=null;
  if(atEnd&&anchors.length)cur=anchors[anchors.length-1].id;
  else for(const a of anchors){if(seen.has(a.id)){cur=a.id;break}}
  for(const a of navs){
   const on=cur!==null&&byId.get(cur)===a;
   a.classList.toggle('on',on);
   if(on)a.setAttribute('aria-current','true');
   else a.removeAttribute('aria-current');
  }
 };
 const io=new IntersectionObserver(es=>{
  for(const e of es){
   if(e.isIntersecting)seen.add(e.target.id);else seen.delete(e.target.id);
  }
  mark();
 },{rootMargin:(-NAVH)+'px 0px -60% 0px'});
 for(const a of anchors)io.observe(a);
 /* 哨兵用第二個觀察器而非捲動事件：捲動事件會形成回呼迴圈。預設 rootMargin
    ——要的就是「頁尾進到視窗裡」這個原始語意，不要任何偏移。 */
 const foot=document.querySelector('footer');
 if(foot){
  new IntersectionObserver(es=>{
   for(const e of es)atEnd=e.isIntersecting;
   mark();
  }).observe(foot);
 }
}
/* 圖像牆折疊：預設只露約半個視窗高，按鈕展開。 */
const RATIO=.5,MARGIN=2,MINROWS=2;
const unfold=new Map(),repaint=[];
for(const box of document.querySelectorAll('.wall-box')){
 const wall=box.querySelector('.wall'),btn=box.querySelector('.more');
 if(!wall||!btn)continue;
 const label=btn.textContent.trim();
 /* forced 是搜尋造成的暫時展開（按鈕整個藏起來），open 是使用者按的
    （按鈕留著讓他收回去）。兩者混用會出現按鈕文字閃動。 */
 let open=false,forced=false;
 /* 把被裁掉的 tile 移出 Tab 順序：overflow:hidden 只是視覺裁切，聚焦到
    看不見的 tile 會讓折疊視窗自己捲動且捲不回來，而且展開按鈕在 DOM 上
    排在牆之後，不這樣做要按幾百次 Tab 才到得了。tabIndex=-1 不影響點擊，
    正是視覺隱藏內容該有的語意。n 為保留在 Tab 順序裡的 tile 數。 */
 const seat=n=>{const ts=wall.children;
  for(let i=0;i<ts.length;i++)ts[i].tabIndex=i<n?0:-1};
 const paint=()=>{
  /* 先處理展開狀態再量測：搜尋時第一張 tile 可能帶著 .hide，
     量到的高度是 0，先量就會提早 return 把 maxHeight 留在原地。 */
  if(forced||open){
   box.classList.remove('folded');wall.style.maxHeight='';seat(Infinity);
   btn.hidden=forced;return;
  }
  const t=box.querySelector('.t'),cs=getComputedStyle(wall);
  const h=t?t.getBoundingClientRect().height:0;
  /* 量不到高度（牆是空的或整面都藏起來）就當作沒有折疊，狀態一併清乾淨。 */
  if(!h){btn.hidden=true;box.classList.remove('folded');wall.style.maxHeight='';
   seat(Infinity);return}
  const gap=parseFloat(cs.rowGap)||0,pad=parseFloat(cs.paddingTop)||0;
  /* tile 是正方形，欄寬等於 tile 高，欄數才能從寬度反推；.wall 用 gap
     簡寫，兩軸相等，所以這裡拿 rowGap 當欄距是成立的。 */
  const cols=Math.max(1,Math.round((wall.clientWidth+gap)/(h+gap)));
  const rows=Math.ceil(wall.children.length/cols);
  const fold=Math.max(MINROWS,Math.floor((innerHeight*RATIO+gap)/(h+gap)));
  /* 只差幾排就折起來反而多一次點擊，不划算。 */
  if(rows<fold+MARGIN){
   btn.hidden=true;box.classList.remove('folded');wall.style.maxHeight='';
   seat(Infinity);return;
  }
  btn.hidden=false;box.classList.add('folded');
  wall.style.maxHeight=(pad+fold*h+(fold-1)*gap)+'px';
  seat(fold*cols);
 };
 btn.addEventListener('click',()=>{
  const was=open;open=!open;
  btn.textContent=open?'收起':label;
  btn.setAttribute('aria-expanded',open?'true':'false');
  paint();
  /* 收起時牆會縮短，捲軸位置會落在後面的區塊，捲回這個區塊的開頭。捲的是
     .anchor 外殼而不是牆本身：外殼上方若有 sticky 工具列，捲到外殼開頭時
     那條列就在它自然的位置上，牆從它下方開始，這裡不必知道它有多高（窄螢幕
     會換行變高）。也不能改捲那條列本身——已經釘住的 sticky 元素其 rect 永遠
     等於落點，scrollIntoView 會判定「已經到位」而完全不捲動。 */
  if(was)(box.closest('.anchor')||box).scrollIntoView({block:'start'});
 });
 unfold.set(wall.id,v=>{forced=v;paint()});
 repaint.push(paint);
 paint();
}
/* 用 resize 事件而非 ResizeObserver：折疊會改動牆自身的 max-height，
   觀察那面牆會讓回呼觸發自己形成無限迴圈；而且折疊高度同時取決於視窗
   高度，resize 兩者都涵蓋。 */
addEventListener('resize',()=>{for(const p of repaint)p()});
const q=document.getElementById('q');
if(q){
 const tiles=[...document.querySelectorAll('#skin-wall .t')],
  tally=document.getElementById('tally'),none=document.getElementById('none'),
  idx=document.getElementById('index'),toggle=document.getElementById('idxbtn');
 function apply(v){v=v.trim().toLowerCase();let n=0;
  for(const t of tiles){const hit=!v||t.dataset.k.includes(v);
   t.classList.toggle('hide',!hit);if(hit)n++}
  tally.textContent=n.toLocaleString()+' / TOTAL'.replace('TOTAL',TOTAL.toLocaleString());
  none.classList.toggle('on',n===0);
  /* 命中的 tile 可能落在被裁掉的區域，搜尋期間先攤開整面牆。 */
  const u=unfold.get('skin-wall');if(u)u(!!v);}
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
