# 🖤 SENSUAL TAROT 78 LÁ — MASTER PROMPT v2

Bản viết lại để sửa **4 lỗi**:

1. **AI đếm sai số lượng cốc / xu / kiếm / gậy** → khối **COUNT LOCK** (số + chữ + bố cục + quy tắc hiển thị +
   lệnh tự kiểm), và **bố cục đếm được** (hàng, lưới, nhóm 3+3+2…) thay vì "rải rác".
2. **Độ gợi cảm của các lá nữ chưa đủ** → khối **FEMALE FIGURE DIRECTIVE** + viết lại scene các lá có nhân vật nữ.
3. **Lá bài không phủ kín khung** (viền tối/sáng thừa quanh lá) → mệnh đề **FULL BLEED** + `--trim` ở hậu kỳ.
4. **Hoạ tiết viền + màu lệch nhau giữa các lá** → **ghép lên khung chuẩn** bằng `scripts/compose_card.py`:
   chỉ giữ lại 3 vùng nội dung riêng của mỗi lá (cảnh · emblem · tên), phần còn lại lấy từ `17-the-star.jpg`.

> Tham chiếu mỗi lần tạo (3 ảnh, đúng thứ tự):
> 1. `cards/card-blank.jpg` — phôi
> 2. `cards/17-the-star.jpg` — neo phong cách **và** khung chuẩn
> 3. `cards/title-style.png` — mẫu chữ tên (cắt từ dải dưới của The Star)

---

## 1. MASTER PROMPT TEMPLATE v2

Copy nguyên khối này, `{EMBLEM}` `{SCENE}` `{TITLE}` `{COUNT_LOCK}` `{FEMME}` lấy từ `01-CARD-TABLE.md`
(hoặc in sẵn bằng `python3 scripts/build_prompts.py prompt <slug>` / lấy file trong `prompts/out/<slug>.txt`).

```text
A single tarot card built upon the FIRST reference image (the deck's blank ornamental template): keep its
symmetric ornamental golden frame, the four corner filigree flourishes, the top-center medallion and the
bottom band with the small skull ornament EXACTLY as they are — do not redraw, move, recolor or resize any
part of the frame. FULL BLEED: the card itself fills the entire image EDGE TO EDGE, corner to corner — there
is no background, no margin, no dark band, no drop shadow and no second border outside the ornamental frame;
every pixel of the image belongs to the card. Fill the empty parchment center with the new scene, painted in
the EXACT master art style of the SECOND reference image (a Major Arcana card of the same deck): identical
illustration technique and linework, identical muted antique color palette, identical paper grain and vellum
texture. The THIRD reference image is the cropped bottom title band of THE STAR — it is the mandatory
LETTERING SAMPLE for this deck.

LAYOUT (draw in this order):
— TOP: inside the top-center ornamental medallion place this card's EMBLEM: {EMBLEM} — small antique-gold
  heraldic emblem, centered, no text, no numerals.
— MIDDLE (the empty parchment area only): {SCENE}
— BOTTOM: in the bottom band, directly beneath the small skull ornament, the title "{TITLE}" — centered, on
  one line, spelled exactly like that.

TITLE LOCK: the title must be rendered in the EXACT lettering of the title in the THIRD reference image —
identical typeface, weight, letter-spacing and tracking, gold tone and shading, cap height and stroke width,
identical position directly beneath the skull ornament. Copy that letterform character by character for the
new words; do not invent a different font, do not use a modern sans-serif. The only text on the card is this title.

{COUNT_LOCK}

{FEMME}

THEME: sensual classic tarot in the tradition of vintage art-nude tarot decks — elegant adult figures entirely
at ease in their bodies, graceful nude and semi-nude poses, silk and sheer gauze that follows the body's line,
warm candlelit and low-sun atmosphere, painterly skin in golden light against cool shadow.

NEGATIVE: wrong or mismatched title font, modern or sans-serif lettering, extra words, misspelled title,
dark margin, empty band, background or mat around the card, drop shadow, vignette, card floating
inside the frame, extra or miscounted suit objects, duplicated, fused, cropped or half-hidden objects, extra
limbs, extra fingers, six-fingered hands, extra heads, modern clothing, neon or oversaturated color, glossy
3D render, plastic airbrushed skin, text or numbers anywhere except the bottom title band, watermark,
signature, artist name, double border, multiple cards, collage.

No other text, no watermark, single card only.
```

---

## 2. Khối COUNT LOCK (điểm sửa lỗi đếm sai)

### 2.1 Với 56 lá ẩn phụ — script tự sinh theo công thức:

```text
COUNT LOCK — EXACTLY {N} {OBJECT} (hard constraint; count before you draw).
The parchment scene contains exactly {N} {OBJECT} — not {N-1}, not {N+1}.
Placement is locked: {LAYOUT}
Every one of the {N} must be fully visible: nothing occluded by a body, limb, cloth, cloud or another object,
nothing fused, broken, cropped by the golden frame, or half-hidden behind a figure. Keep them at one consistent
size, shape, material and color so they read as a single countable set, with a clear gap of background between
each one. Place no other {OBJECT-singular} anywhere else on the card — not in the frame, not in the background,
not held by a figure, not as decoration. The emblem in the top medallion is a separate heraldic motif and does
NOT count toward the {N}. Before finishing, count them: 1, 2, 3 … {N}. If the total is not {N}, redraw.
```

**5 lớp khoá** — AI thường sai ở một lớp, các lớp còn lại vẫn giữ được:

| Lớp | Cách khoá | Ví dụ (8 gậy) |
|-----|-----------|----------------|
| 1. Số | chữ số + chữ + "not N−1, not N+1" | `EXACTLY 8 wands — not 7, not 9` |
| 2. Bố cục | mô tả **hình học**, không rải rác | `ONE single parallel diagonal row — 1 row of 8` |
| 3. Nhóm con | chia 3+3+2, 4+3+2+1… (dễ đếm hơn 1 cụm 9) | Cốc 8 = `3 + 3 + 2` · Xu 10 = `4+3+2+1` |
| 4. Hiển thị | cấm che khuất / cắt / dính nhau | `nothing occluded, fused, cropped, half-hidden` |
| 5. Tự kiểm | bắt model đếm lại trước khi xong | `count them: 1,2,3,4,5,6,7,8. If not 8, redraw` |

### 2.2 Khoá bổ sung cho các lá Major có vật phẩm chất liệu:
* **01-magician** → đúng 4 món trên bàn: 1 cốc + 1 kiếm + 1 gậy + 1 xu, **mỗi loại đúng 1** (lỗi hay gặp: AI nhân đôi cốc).
* **10-wheel** → đúng 1 kiếm (trên tay nhân sư).
* **11-justice**, **14-temperance** (2 cốc), **17-the-star** (2 bình), **21-world** (2 gậy) → khoá tương tự.
* Các Major còn lại: `COUNT LOCK — not applicable… do not add decorative suit objects.`

### 2.3 10 quy tắc chống đếm sai (áp dụng khi tự viết scene mới)

1. Luôn ghi **cả số lẫn chữ**: `8 (eight) wands`. Không bao giờ dùng `several / some / a few / a pile of / many`.
2. **Bố cục thắng số đếm**: hàng ngang, cột dọc, lưới 3×3, kim tự tháp 4-3-2-1, vòng tròn 3+2+3. Tránh "rải trên mặt đất".
3. Với số lớn (8, 9, 10) bắt buộc **chia nhóm** và ghi phép cộng: `3 + 3 + 3 = 9`.
4. Bắt tất cả object **cùng kích thước, cùng màu, cùng chất liệu** → model nhận diện thành một "tập" thay vì vật rời.
5. Đặt **trên nền trống** (bầu trời, tường phẳng, cát) thay vì lẫn vào lá cây/đồ vật.
6. Cấm che khuất: thêm `all N fully visible, none hidden behind a figure`.
7. Cấm cắt khung: thêm `wholly inside the parchment area, never cropped by the golden frame`.
8. Tách emblem khỏi scene: `the emblem does NOT count toward the N` (tránh model gộp emblem vào tổng).
9. Chốt bằng lệnh tự kiểm: `Before finishing, count them: 1, 2, 3 … N`.
10. Đưa COUNT LOCK lên **ngay sau LAYOUT**, trước THEME — model ưu tiên chỉ thị xuất hiện sớm.

### 2.4 Xử lý khi vẫn sai
* Sai **thừa** (9 thay vì 8): scene đang có vật "na ná" (bình = cốc, gậy trong tay = gậy trong cảnh) → thêm
  `the {objects} in the parchment area are the only {objects} in the whole image; no other vessel/staff/blade/disc anywhere`.
* Sai **thiếu** (7 thay vì 8): đang bị che khuất hoặc dính nhau → thêm `spread them wider`, `more empty space between each one`,
  hoặc đổi bố cục sang lưới/hàng thẳng.
* Sai ở số lớn (9, 10): hạ xuống nhóm nhỏ hơn (3+3+3) hoặc chấp nhận bố cục "kệ/hàng" như một lựa chọn thẩm mỹ của bộ bài.
* Vẫn lỗi: tạo lại cùng prompt 2–3 lần rồi chọn — tỉ lệ đúng tăng rõ rệt so với sửa prompt mù.

---

## 3. Khối FEMALE FIGURE DIRECTIVE (tăng độ gợi cảm)

Chèn tự động cho mọi lá có nhân vật nữ (`femme: true` trong `cards.json`):

```text
FEMALE FIGURE DIRECTIVE (mandatory for every woman in the scene): render her with heightened yet tasteful
sensuality — a mature adult woman, confident and entirely at ease in her own skin. Favour: a long bare back
with the line of the spine caught by low golden light, bare shoulders with silk or wet gauze slipping off one
of them, the curve of waist and hip clearly drawn, a hand lifted into loosened hair, an arched or reclining
posture. Give her a languid, alive expression — parted lips, heavy-lidded eyes meeting the viewer or a slow
sidelong glance. Drapery is silk or sheer gauze that clings and reveals the body's line rather than hiding it.
Nudity is fine-art: bare breasts, back and hips may be shown as soft classical anatomy, painterly and never
graphic or clinical.

HARD LIMITS: no explicit sexual acts, no exposed genitals, no spread legs, no hand or object at the genitals,
no sexual fluids, no fetish or bondage gear, no minors, no pornographic framing or camera angle.
```

**Các lá nữ đã được viết lại scene theo hướng gợi cảm hơn** (giữ nguyên biểu tượng học, chỉ đổi cách mô tả cơ thể / ánh sáng / vải):

* **Major:** 00-fool · 01-magician · 02-priestess · 03-empress · 06-lovers · 07-chariot · 08-strength · 11-justice ·
  14-temperance · 15-devil · 16-tower · 17-star · 18-moon · 19-sun · 20-judgement · 21-world
* **Wands:** 02 · 04 · 06 · page · queen
* **Cups:** 02 · 03 · 06 · 10 · page · queen
* **Swords:** 02 · 06 · 08 · 09 · page · queen
* **Pentacles:** 03 · 05 · 08 · 09 · 10 · page · queen

Các lá vốn trung tính được **gán nữ** trong bản sensual này: `00-fool`, `01-magician`, `07-chariot`,
`14-temperance`, `21-world` và toàn bộ **4 Page** — đổi lại thành nam trong `cards.json` (`"femme": false`) + sửa scene nếu bạn muốn giữ nguyên giới tính gốc.

---

## 3b. Full-bleed — không còn viền ngoài

Lá phôi **phải** phủ kín khung: nếu phôi còn dải nền tối ở mép, model sẽ học theo và vẽ kèm viền tối quanh
mọi lá bài. Hai lớp bảo vệ:

1. **Khoá ở prompt** — mệnh đề `FULL BLEED …` ở ngay đầu template + các cụm `dark margin / background /
   drop shadow / vignette / card floating inside the frame` trong NEGATIVE.
2. **Khoá ở hậu kỳ** — `python3 scripts/process_cards.py raw/ --trim` tự dò dải viền ngoài (theo ngưỡng sáng,
   mặc định `0.18`) và cắt bỏ trước khi resize về 848×1264. Dùng `--trim-thr` để chỉnh ngưỡng; `--trim`
   không làm gì nếu ảnh đã phủ kín khung.

Kiểm tra nhanh một ảnh đã full-bleed chưa:

```bash
convert cards/<slug>.jpg -fuzz 8% -trim -format "%wx%h" info:   # trả về 848x1264 là đạt
```

## 3c. Khung chuẩn & đồng màu — `compose_card.py`

Model chỉ "xấp xỉ" khung khi nhìn tham chiếu → hoạ tiết và màu lệch giữa các lá. Đo bằng RMSE trên dải khung
trái (0 = giống hệt) trước khi sửa: `0.033 … 0.281` (chariot lệch nhất). Sau khi ghép: `0.003 … 0.004`.

**Cách hoạt động:** lấy `17-the-star.jpg` làm khung chuẩn. Từ mỗi lá AI sinh ra chỉ giữ 3 vùng nội dung
riêng, dán lên khung chuẩn với viền mềm 12px; phần còn lại (khung vàng, 4 góc filigree, medallion, đầu lâu)
là của khung chuẩn nên **giống hệt nhau trên mọi lá**. Trước khi dán, ảnh được cân màu theo khung chuẩn
(per-channel polynomial, hệ số tính trên dải khung trái).

Vùng dán lưu trong `prompts/panel.json` (đo từ bản đồ khác biệt Star vs Fool):

| Vùng | Toạ độ (x, y, w, h) |
|------|---------------------|
| `panel` — cảnh giữa | 106, 120, 621, 933 |
| `emblem` — huy hiệu trong medallion | 250, 10, 350, 115 |
| `title` — chữ tên ở dải dưới | 262, 1090, 330, 145 |

```bash
python3 scripts/compose_card.py raw/          # ghép tất cả ảnh trong raw/ lên khung chuẩn
python3 scripts/compose_card.py --check       # đo độ lệch khung từng lá so với khung chuẩn
```

> ⚠️ Lưu ý ImageMagick: `-function Polynomial` nhận hệ số theo **luỹ thừa giảm dần** — `"a,b"` = `a·x + b`.
> Truyền ngược (`"b,a"`) sẽ làm ảnh cháy sáng.

## 4. Quy trình chạy

```bash
# 1. Kiểm tra dữ liệu (78 lá, số lượng khớp biểu tượng học, không có từ chỉ số lượng mơ hồ)
python3 scripts/build_prompts.py check

# 2. In prompt hoàn chỉnh cho 1 lá và paste vào generate_image
python3 scripts/build_prompts.py prompt 08-strength

# 3. Hoặc xuất sẵn 78 file, mở copy-paste dần
python3 scripts/build_prompts.py all     # -> prompts/out/<slug>.txt
```

**Generate:** `generate_image` với
`images: [cards/card-blank.jpg, cards/17-the-star.jpg, cards/title-style.png]`, prompt lấy ở bước 2/3.

**Hậu kỳ:** `python3 scripts/compose_card.py raw/` — một lệnh làm cả 3 việc: cắt viền ngoài (`-trim`),
cân màu theo khung chuẩn, ghép lên khung chuẩn, chuẩn hoá 848×1264 và nén ≤ 800KB (q90).
(Dùng `process_cards.py` khi chỉ cần resize/nén mà không ghép khung.)

**Chia batch theo giới hạn 10 ảnh/lượt (8 lượt):**

| Lượt | Nội dung | Số lá |
|------|----------|-------|
| 1 | Major 0 → VIII | 10 |
| 2 | Major IX → XX + XXI | 12 → gộp 10 + 2 dư sang lượt 3 |
| 3 | 2 Major dư + Wands A → 07 | 10 |
| 4 | Wands 08 → King (08, 09, 10, P, N, Q, K) + Cups A, 02, 03 | 10 |
| 5 | Cups 04 → 10 + P, N, Q | 10 |
| 6 | Cups King + Swords A → 08 | 10 |
| 7 | Swords 09, 10, P, N, Q, K + Pentacles A → 04 | 10 |
| 8 | Pentacles 05 → King | 6 |

---

## 5. QA checklist (duyệt từng ảnh trước khi nhận)

- [ ] Đếm tay số cốc / xu / kiếm / gậy **trong vùng giấy** — đúng N? (đừng tính emblem ở medallion)
- [ ] Có object nào bị che, dính, cắt khung không?
- [ ] Ảnh phủ kín khung, **không có dải viền tối / nền / bóng đổ** quanh lá?
- [ ] Khung viền vàng, 4 góc hoa văn, medallion, dải tên + đầu lâu **giống phôi 100%**?
- [ ] Tên lá đúng chính tả, **đúng font của The Star**, chỉ nằm ở dải dưới?
- [ ] `python3 scripts/compose_card.py --check` → RMSE khung < 0.01?
- [ ] Nhân vật nữ đủ gợi cảm nhưng vẫn đúng giới hạn fine-art (không lộ genital, không tư thế khiêu dâm)?
- [ ] Tay đủ ngón, không dư chi, không dư đầu?
- [ ] Màu trầm antique khớp `17-the-star.jpg`?

---

## 6. File trong repo

| File | Vai trò |
|------|---------|
| `prompts/00-MASTER-PROMPT.md` | Tài liệu này — template + quy tắc |
| `prompts/01-CARD-TABLE.md` | Bảng 78 lá (emblem · count lock · scene · title) — sinh tự động |
| `prompts/cards.json` | Nguồn dữ liệu duy nhất (sửa ở đây, không sửa tay file md) |
| `prompts/template.md` | Template có placeholder |
| `prompts/out/<slug>.txt` | 78 prompt hoàn chỉnh, copy-paste trực tiếp |
| `prompts/panel.json` | Toạ độ 3 vùng nội dung dùng khi ghép khung |
| `scripts/build_prompts.py` | `check` · `prompt` · `all` · `md` · `batch` |
| `scripts/process_cards.py` | resize 848×1264 · `--trim` cắt viền · nén ≤ 800KB |
| `scripts/compose_card.py` | ghép lên khung chuẩn + cân màu · `--check` đo độ lệch |
| `scripts/build_gallery.py` | quét `cards/` → `deck.json` cho gallery |
| `cards/card-blank.jpg` · `17-the-star.jpg` · `title-style.png` | 3 ảnh tham chiếu bắt buộc |
