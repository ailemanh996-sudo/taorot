const state = { data: null, filter: 'all', onlyMissing: false, query: '', view: [], idx: -1 };

const $ = (id) => document.getElementById(id);

async function load() {
  const res = await fetch('deck.json', { cache: 'no-store' });
  state.data = await res.json();
  $('count-done').textContent = state.data.done;
  $('count-total').textContent = state.data.total;
  $('bar-fill').style.width = (100 * state.data.done / state.data.total) + '%';
  render();
}

function visible() {
  const q = state.query.trim().toLowerCase();
  return state.data.cards.filter((c) => {
    if (state.filter !== 'all' && c.group !== state.filter) return false;
    if (state.onlyMissing && c.file) return false;
    if (q && !(c.title.toLowerCase().includes(q) || c.slug.includes(q) || c.scene.toLowerCase().includes(q))) return false;
    return true;
  });
}

function render() {
  const grid = $('grid');
  state.view = visible();
  $('empty').hidden = state.view.length > 0;
  grid.innerHTML = state.view.map((c, i) => `
    <article class="card ${c.femme ? 'femme' : ''}" data-i="${i}">
      <div class="frame">
        ${c.file
          ? `<img src="${c.file}" alt="${c.title}" loading="lazy">`
          : `<div class="ph"><div class="num">${c.n}</div><div class="ttl">${c.title}</div></div>`}
      </div>
      <div class="cap"><span class="t">${c.title}</span><span class="s">${c.slug}</span></div>
      ${c.file ? `<span class="badge">${c.w}×${c.h} · ${c.kb}KB</span>` : ''}
    </article>`).join('');
  grid.querySelectorAll('.card').forEach((el) => el.addEventListener('click', () => open(+el.dataset.i)));
}

function open(i) {
  state.idx = i;
  const c = state.view[i];
  $('lb-kicker').textContent = `${c.groupLabel} · ${c.n}`;
  $('lb-title').textContent = c.title;
  $('lb-emblem').textContent = c.emblem;
  $('lb-file').textContent = c.file ? `${c.file} — ${c.w}×${c.h}, ${c.kb} KB` : 'chưa tạo (bỏ ảnh vào cards/)';
  $('lb-scene').textContent = c.scene;
  const img = $('lb-image');
  if (c.file) { img.src = c.file; img.hidden = false; } else { img.removeAttribute('src'); img.hidden = true; }
  $('lb-prompt').hidden = true;
  $('lb-prompt').textContent = '';
  $('lightbox').hidden = false;
  document.body.style.overflow = 'hidden';
}

function close() {
  $('lightbox').hidden = true;
  document.body.style.overflow = '';
}

function step(d) {
  if (state.idx < 0) return;
  open((state.idx + d + state.view.length) % state.view.length);
}

async function showPrompt() {
  const c = state.view[state.idx];
  const box = $('lb-prompt');
  if (!box.hidden) { box.hidden = true; return; }
  if (!box.textContent) {
    box.textContent = 'đang tải…';
    try {
      const r = await fetch(`prompts/out/${c.slug}.txt`, { cache: 'no-store' });
      box.textContent = r.ok ? (await r.text()) : 'chưa có file prompt';
    } catch (e) { box.textContent = 'lỗi tải prompt'; }
  }
  box.hidden = false;
}

async function copyPrompt() {
  const c = state.view[state.idx];
  const box = $('lb-prompt');
  let text = box.textContent;
  if (!text) {
    const r = await fetch(`prompts/out/${c.slug}.txt`, { cache: 'no-store' });
    text = await r.text();
    box.textContent = text;
  }
  try {
    await navigator.clipboard.writeText(text);
    const b = $('btn-copy');
    const old = b.textContent;
    b.textContent = 'Đã copy ✓';
    setTimeout(() => { b.textContent = old; }, 1400);
  } catch (e) {
    box.hidden = false;
    box.select && box.select();
  }
}

document.querySelectorAll('.tab').forEach((t) => t.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach((x) => x.classList.remove('active'));
  t.classList.add('active');
  state.filter = t.dataset.group;
  render();
}));
$('only-missing').addEventListener('change', (e) => { state.onlyMissing = e.target.checked; render(); });
$('search').addEventListener('input', (e) => { state.query = e.target.value; render(); });
$('lb-close').addEventListener('click', close);
$('lb-prev').addEventListener('click', () => step(-1));
$('lb-next').addEventListener('click', () => step(1));
$('btn-prompt').addEventListener('click', showPrompt);
$('btn-copy').addEventListener('click', copyPrompt);
document.addEventListener('keydown', (e) => {
  if ($('lightbox').hidden) return;
  if (e.key === 'Escape') close();
  if (e.key === 'ArrowLeft') step(-1);
  if (e.key === 'ArrowRight') step(1);
});
$('lightbox').addEventListener('click', (e) => { if (e.target.id === 'lightbox') close(); });

load();
