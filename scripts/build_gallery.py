#!/usr/bin/env python3
"""Quét cards/ và sinh gallery tự chứa (không cần server).

  python3 scripts/build_gallery.py

Sinh ra:
  deck.json    dữ liệu thô
  index.html   trình xem tự chứa — dữ liệu + CSS + JS nhúng sẵn,
               mở bằng cách bấm đúp cũng chạy được.
"""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
BACKS = ROOT / "backs"
DATA = ROOT / "prompts" / "cards.json"
PROMPTS = ROOT / "prompts" / "out"
OUT_JSON = ROOT / "deck.json"
OUT_HTML = ROOT / "index.html"

GROUPS = {"major": "Ẩn Chính", "wands": "Gậy", "cups": "Cốc",
          "swords": "Kiếm", "pentacles": "Tiền"}


def dims(p):
    if shutil.which("identify"):
        r = subprocess.run(["identify", "-format", "%w %h", str(p)],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            w, h = r.stdout.split()
            return int(w), int(h)
    return None, None


def collect():
    cards = json.loads(DATA.read_text(encoding="utf-8"))["cards"]
    out, done = [], 0
    for c in cards:
        f = None
        for ext in (".jpg", ".png", ".webp"):
            p = CARDS / f"{c['slug']}{ext}"
            if p.exists():
                f = p
                break
        prompt = ""
        pf = PROMPTS / f"{c['slug']}.txt"
        if pf.exists():
            prompt = pf.read_text(encoding="utf-8").strip()
        item = {"slug": c["slug"], "n": c["n"], "group": c["group"],
                "groupLabel": GROUPS[c["group"]], "emblem": c["emblem"],
                "title": c["title"], "scene": c["scene"],
                "femme": bool(c.get("femme")), "file": None, "prompt": prompt}
        if f:
            w, h = dims(f)
            item["file"] = f.relative_to(ROOT).as_posix()
            item["w"], item["h"] = w, h
            item["kb"] = round(f.stat().st_size / 1024)
            done += 1
        out.append(item)
    return out, done


def find_back():
    for name in ("card-back.jpg", "back-05.jpg", "card-back.png"):
        p = BACKS / name
        if p.exists():
            w, h = dims(p)
            return {"file": p.relative_to(ROOT).as_posix(), "w": w, "h": h,
                    "kb": round(p.stat().st_size / 1024)}
    return None


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#171310; --bg2:#221c16; --ink:#f2e6cf; --dim:#a8977c;
  --gold:#c9a227; --line:#3a2f24; --card:#2a2219;
}
html{scroll-behavior:smooth}
body{background:radial-gradient(1200px 700px at 50% -10%,#2e2519,#171310 60%);
     color:var(--ink);font:15px/1.55 ui-sans-serif,system-ui,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
     min-height:100vh}
.wrap{max-width:1240px;margin:0 auto;padding:28px 20px 80px}
header{display:flex;flex-wrap:wrap;gap:20px;align-items:flex-end;justify-content:space-between;
       padding-bottom:18px;border-bottom:1px solid var(--line);margin-bottom:22px}
h1{font:600 26px/1.2 ui-serif,Georgia,serif;letter-spacing:.14em;color:var(--gold)}
.sub{color:var(--dim);font-size:13px;margin-top:6px}
.stats{display:flex;gap:22px;align-items:center}
.stat{text-align:right}
.stat b{display:block;font:600 22px/1 ui-serif,Georgia,serif;color:var(--gold)}
.stat span{font-size:11px;color:var(--dim);letter-spacing:.08em;text-transform:uppercase}
.bar{height:4px;width:150px;background:var(--line);border-radius:3px;overflow:hidden;margin-top:8px}
.bar i{display:block;height:100%;background:linear-gradient(90deg,#8a6d1f,var(--gold))}

.backbox{display:flex;gap:22px;align-items:center;background:var(--card);
         border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:26px}
.backbox img{width:104px;border-radius:8px;box-shadow:0 10px 26px #0008;cursor:zoom-in}
.backbox h2{font:600 17px ui-serif,Georgia,serif;color:var(--gold);margin-bottom:4px}
.backbox p{color:var(--dim);font-size:13px}

nav{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:20px}
.tab{background:transparent;border:1px solid var(--line);color:var(--dim);
     padding:7px 14px;border-radius:99px;cursor:pointer;font-size:13px;transition:.15s}
.tab:hover{color:var(--ink);border-color:#5a4a35}
.tab.active{background:var(--gold);border-color:var(--gold);color:#221c16;font-weight:600}
.spacer{flex:1}
#search{background:#1d1813;border:1px solid var(--line);color:var(--ink);
        padding:8px 14px;border-radius:99px;font-size:13px;width:210px;outline:none}
#search:focus{border-color:var(--gold)}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(148px,1fr));gap:18px}
.cell{background:var(--card);border:1px solid var(--line);border-radius:12px;
      padding:10px;cursor:zoom-in;transition:.18s;position:relative}
.cell:hover{transform:translateY(-4px);border-color:var(--gold);box-shadow:0 12px 28px #0007}
.cell img{width:100%;display:block;border-radius:7px;background:#0f0c0a}
.cell .t{font:600 11.5px/1.3 ui-sans-serif,system-ui;letter-spacing:.06em;
         text-align:center;margin-top:9px;color:var(--ink)}
.cell .g{font-size:10px;color:var(--dim);text-align:center;margin-top:3px;letter-spacing:.05em}
.cell .miss{position:absolute;inset:10px;border:1px dashed #5a4a35;border-radius:7px;
            display:grid;place-items:center;color:#6b5a44;font-size:11px}
.suit{margin:34px 0 14px;font:600 13px ui-sans-serif;letter-spacing:.16em;
      color:var(--gold);text-transform:uppercase;display:flex;align-items:center;gap:12px}
.suit:after{content:"";flex:1;height:1px;background:var(--line)}
.empty{color:var(--dim);text-align:center;padding:50px 0}

footer{margin-top:50px;padding-top:18px;border-top:1px solid var(--line);
       color:var(--dim);font-size:12px}

.lb{position:fixed;inset:0;background:#0b0907ee;backdrop-filter:blur(6px);
    display:flex;align-items:center;justify-content:center;z-index:50;padding:24px}
.lb[hidden]{display:none}
.lb-body{display:flex;gap:26px;max-width:1080px;width:100%;max-height:88vh;
         align-items:flex-start;flex-wrap:wrap;justify-content:center}
.lb-img img{max-height:82vh;width:auto;max-width:100%;border-radius:10px;
            box-shadow:0 20px 60px #000}
.lb-meta{max-width:400px;overflow:auto;max-height:82vh}
.lb-kicker{font-size:11px;letter-spacing:.18em;color:var(--gold);text-transform:uppercase}
.lb-meta h2{font:600 26px/1.2 ui-serif,Georgia,serif;margin:6px 0 16px}
.lb-meta dl{display:grid;grid-template-columns:76px 1fr;gap:6px 12px;
            font-size:13px;margin-bottom:16px}
.lb-meta dt{color:var(--dim)}
.lb-meta dd{color:var(--ink)}
.scene{font-size:13px;color:var(--dim);line-height:1.6;margin-bottom:16px;
       padding-left:10px;border-left:2px solid var(--line)}
.lb-actions{display:flex;gap:10px;flex-wrap:wrap}
.lb-actions button{background:transparent;border:1px solid var(--line);color:var(--ink);
                   padding:8px 14px;border-radius:8px;cursor:pointer;font-size:12.5px;transition:.15s}
.lb-actions button:hover{border-color:var(--gold);color:var(--gold)}
.lb-meta pre{white-space:pre-wrap;word-break:break-word;background:#15110e;
             border:1px solid var(--line);border-radius:8px;padding:12px;
             font:11.5px/1.5 ui-monospace,Menlo,Consolas,monospace;
             color:var(--dim);max-height:280px;overflow:auto;margin-top:12px}
.lb-close,.lb-nav{position:fixed;background:#1d1813cc;border:1px solid var(--line);
                  color:var(--ink);border-radius:50%;cursor:pointer;z-index:60}
.lb-close{top:18px;right:20px;width:40px;height:40px;font-size:17px}
.lb-nav{top:50%;transform:translateY(-50%);width:44px;height:44px;font-size:22px}
.lb-prev{left:16px}.lb-next{right:16px}
.lb-close:hover,.lb-nav:hover{border-color:var(--gold);color:var(--gold)}
@media(max-width:820px){
  .lb-body{flex-direction:column;align-items:center}
  .lb-img img{max-height:52vh}
  .lb-meta{max-width:100%}
  .stats{gap:14px}
}
"""

JS = """
const D = window.__DECK__;
const grid = document.getElementById('grid');
const lb = document.getElementById('lightbox');
let view = [], cur = -1;

const el = (t, c, x) => { const e = document.createElement(t);
  if (c) e.className = c; if (x != null) e.textContent = x; return e; };

function cardCell(c, i) {
  const d = el('div', 'cell');
  d.dataset.i = i;
  if (c.file) {
    const im = el('img'); im.src = c.file; im.alt = c.title; im.loading = 'lazy';
    d.appendChild(im);
  } else {
    const m = el('div', 'miss', 'chưa tạo'); d.appendChild(m);
    const im = el('img'); im.style.visibility = 'hidden'; d.appendChild(im);
  }
  d.appendChild(el('div', 't', c.title));
  d.appendChild(el('div', 'g', c.groupLabel));
  d.onclick = () => openLb(i);
  return d;
}

function render(list) {
  view = list; grid.innerHTML = '';
  if (!list.length) { document.getElementById('empty').hidden = false; return; }
  document.getElementById('empty').hidden = true;
  const order = ['major', 'wands', 'cups', 'swords', 'pentacles'];
  const showSuit = new Set(list.map(c => c.group)).size > 1;
  order.forEach(g => {
    const part = list.filter(c => c.group === g);
    if (!part.length) return;
    if (showSuit) grid.appendChild(el('div', 'suit', part[0].groupLabel));
    part.forEach(c => grid.appendChild(cardCell(c, D.cards.indexOf(c))));
  });
}

function filter() {
  const g = document.querySelector('.tab.active').dataset.group;
  const q = document.getElementById('search').value.trim().toLowerCase();
  render(D.cards.filter(c =>
    (g === 'all' || c.group === g) &&
    (!q || c.title.toLowerCase().includes(q) || c.slug.includes(q) ||
     c.scene.toLowerCase().includes(q))));
}

function openLb(i) {
  cur = i; const c = view[i] || D.cards[i];
  document.getElementById('lb-image').src = c.file || '';
  document.getElementById('lb-kicker').textContent =
    c.groupLabel + ' · ' + (c.file ? c.w + '×' + c.h + ' · ' + c.kb + ' KB' : 'chưa có ảnh');
  document.getElementById('lb-title').textContent = c.title;
  document.getElementById('lb-emblem').textContent = c.emblem;
  document.getElementById('lb-file').textContent = c.file || '—';
  document.getElementById('lb-scene').textContent = c.scene;
  const pre = document.getElementById('lb-prompt');
  pre.textContent = c.prompt || '(chưa có prompt)';
  pre.hidden = true;
  lb.hidden = false;
  document.body.style.overflow = 'hidden';
}
function closeLb() { lb.hidden = true; document.body.style.overflow = ''; }
function step(d) {
  const list = document.querySelector('.tab.active').dataset.group === 'all'
    ? D.cards : view;
  let i = list.indexOf(view[cur]);
  if (i < 0) i = cur;
  i = (i + d + list.length) % list.length;
  view = list; openLb(i);
}
function navIn() {
  const list = document.querySelector('.tab.active').dataset.group === 'all'
    ? D.cards : view;
  return list;
}

document.querySelectorAll('.tab').forEach(b => b.onclick = () => {
  document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
  b.classList.add('active'); filter();
});
document.getElementById('search').oninput = filter;
document.getElementById('lb-close').onclick = closeLb;
document.getElementById('lb-prev').onclick = e => { e.stopPropagation(); step(-1); };
document.getElementById('lb-next').onclick = e => { e.stopPropagation(); step(1); };
document.getElementById('btn-prompt').onclick = () => {
  const p = document.getElementById('lb-prompt'); p.hidden = !p.hidden;
};
document.getElementById('btn-copy').onclick = async e => {
  const t = document.getElementById('lb-prompt').textContent;
  try { await navigator.clipboard.writeText(t); e.target.textContent = 'Đã copy ✓'; }
  catch (_) { e.target.textContent = 'Copy thất bại'; }
  setTimeout(() => e.target.textContent = 'Copy prompt', 1600);
};
lb.onclick = e => { if (e.target === lb) closeLb(); };
document.addEventListener('keydown', e => {
  if (lb.hidden) return;
  if (e.key === 'Escape') closeLb();
  if (e.key === 'ArrowLeft') step(-1);
  if (e.key === 'ArrowRight') step(1);
});

document.getElementById('bar-fill').style.width = (D.done / D.total * 100) + '%';
document.getElementById('count-done').textContent = D.done;
document.getElementById('count-total').textContent = D.total;
document.getElementById('count-size').textContent = D.size;
filter();
"""


def main():
    cards, done = collect()
    back = find_back()
    payload = {"deck": "Sensual Tarot", "total": len(cards), "done": done,
               "size": "848x1264", "back": back, "cards": cards}
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                        encoding="utf-8")

    back_html = ""
    if back:
        back_html = (
            '<section class="backbox">'
            f'<img src="{back["file"]}" alt="mặt sau lá bài" id="back-img">'
            '<div><h2>Mặt sau lá bài</h2>'
            f'<p>Hai thiên thần nhỏ ở tư thế đối ngược · {back["w"]}×{back["h"]}'
            f' · {back["kb"]} KB · một tông màu (giấy cổ + vàng cổ)</p></div>'
            '</section>'
        )

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sensual Tarot · {done}/{len(cards)} lá</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
  <div>
    <h1>SENSUAL TAROT</h1>
    <p class="sub">Bộ bài 78 lá · khung 848×1264 · phôi + neo phong cách Star</p>
  </div>
  <div class="stats">
    <div class="stat"><b><span id="count-done">0</span>/<span id="count-total">78</span></b>
      <span>lá đã tạo</span><div class="bar"><i id="bar-fill"></i></div></div>
    <div class="stat"><b id="count-size">—</b><span>kích thước</span></div>
  </div>
</header>

{back_html}

<nav>
  <button class="tab active" data-group="all">Tất cả</button>
  <button class="tab" data-group="major">Ẩn Chính</button>
  <button class="tab" data-group="wands">Gậy</button>
  <button class="tab" data-group="cups">Cốc</button>
  <button class="tab" data-group="swords">Kiếm</button>
  <button class="tab" data-group="pentacles">Tiền</button>
  <span class="spacer"></span>
  <input id="search" type="search" placeholder="Tìm tên lá, slug, cảnh…">
</nav>

<main id="grid" class="grid"></main>
<p id="empty" class="empty" hidden>Không có lá nào khớp.</p>

<footer>Trình xem tự chứa — dữ liệu nhúng sẵn, mở trực tiếp bằng trình duyệt.
Chạy <code>python3 scripts/build_gallery.py</code> để cập nhật.</footer>
</div>

<div id="lightbox" class="lb" hidden>
  <button class="lb-close" id="lb-close" aria-label="đóng">✕</button>
  <button class="lb-nav lb-prev" id="lb-prev" aria-label="trước">‹</button>
  <button class="lb-nav lb-next" id="lb-next" aria-label="sau">›</button>
  <div class="lb-body">
    <div class="lb-img"><img id="lb-image" alt=""></div>
    <div class="lb-meta">
      <div class="lb-kicker" id="lb-kicker"></div>
      <h2 id="lb-title"></h2>
      <dl><dt>Emblem</dt><dd id="lb-emblem"></dd>
          <dt>File</dt><dd id="lb-file"></dd></dl>
      <p class="scene" id="lb-scene"></p>
      <div class="lb-actions">
        <button id="btn-prompt">Xem prompt</button>
        <button id="btn-copy">Copy prompt</button>
      </div>
      <pre id="lb-prompt" hidden></pre>
    </div>
  </div>
</div>

<script>window.__DECK__={json.dumps(payload, ensure_ascii=False)};</script>
<script>{JS}</script>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"wrote {OUT_JSON.name} + {OUT_HTML.name} — {done}/{len(cards)} lá"
          + (" · có mặt sau" if back else " · chưa có mặt sau"))


if __name__ == "__main__":
    main()
