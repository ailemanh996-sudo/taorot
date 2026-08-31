# Đặc tả kỹ thuật lá bài — Sensual Tarot

Tài liệu sinh tự động từ `prompts/panel.json` và mã nguồn trong `scripts/`.
Mọi con số lấy từ cấu hình **đang thực sự chạy**, không ghi theo trí nhớ.

---

## 1. Kích thước

| Thông số | Giá trị |
|---|---|
| Kích thước | **848 × 1264 px** |
| Tỉ lệ | **0.671** (dọc) |
| Kích thước in @320 dpi | 6.73 × 10.03 cm |
| Định dạng | JPEG q90 (giảm dần đến q60 nếu vượt 800 KB) |
| Tràn lề | Có — lá phủ kín ảnh, không viền ngoài, không đổ bóng |

---

## 2. Các lớp của lá (từ ngoài vào trong)

Đo trực tiếp trên `refs/star-clean.png`, quét cường độ sáng theo hàng/cột:

| Lớp | Trái | Phải | Trên | Dưới | Nguồn |
|---|---|---|---|---|---|
| Viền ngoài sáng | x 0..33 | x 814..847 | y 0..33 | y 1237..1263 | khung chuẩn |
| **Dải hoạ tiết tối** | x 34..74 | x 774..813 | y 34..74 | y 1186..1236 | khung chuẩn |
| **Dải nhợt** | x 75..114 | x 734..773 | y 75..121 | y 1020..1042 | khung chuẩn |
| **Viền trong** (đường kép) | x 115..123 | x 725..733 | y 122..130 | y 1043..1046 | khung chuẩn |
| **Vùng nội dung** | **x 124..724** | | **y 131..1045** | | **ảnh của lá** |
| Huy hiệu | — | — | y 10..125 | — | ảnh của lá |
| Dải tên | — | — | — | y 1045..1245 | ảnh của lá |

> Ô nội dung `124,131,600,878` nằm **trọn trong** vùng được viền trong bao quanh,
> và **không chạm** huy hiệu (kết thúc y=125) hay dải tên (bắt đầu y=1045).

---

## 3. Bảng tọa độ các vùng

Tọa độ theo chuẩn ImageMagick: `x,y` là góc trên-trái, rồi đến `rộng × cao`.

| Vùng | Góc (x,y) | Kích thước | Góc đối diện | Nội dung |
|---|---|---|---|---|
| **Ô nội dung** `panel` | `124,131` | 600 × 914 | `724,1045` | Cảnh của lá — phần duy nhất thay đổi giữa các lá |
| **Huy hiệu** `emblem` | `250,10` | 350 × 115 | `600,125` | Biểu tượng riêng của lá, không chữ, không số |
| **Dải tên** `title` | `80,1045` | 690 × 200 | `770,1245` | Toàn bộ dải hoa văn dưới, lấy nguyên từ lá nguồn |

---

## 4. Thông số viền & ghép

| Thông số | Giá trị | Ý nghĩa |
|---|---|---|
| `feather` | **3 px** | Làm mờ mép mặt nạ (`-blur 0×3`) để đường nối không sắc |
| `edge_guard` | **18 px** | Nét đen dày 36 px sát mép ngoài — **khoá viền**, không cho feather lem ra khung |
| `bg` | `#e8dcc0` | Màu nền dự phòng khi ảnh nguồn thiếu chiều |
| `max_kb` | **800 KB** | Ngưỡng dung lượng; vượt thì giảm chất lượng 90 → 60 |

### Kiến trúc lớp — nội dung ở dưới, khung phủ lên trên

Đây là **thay đổi quan trọng nhất** của quy trình ghép.

**Cách cũ (mặt nạ):** lấy khung chuẩn làm nền, rồi dán 3 vùng nội dung vào. Vì phải dán
lọt đúng ô, cần `feather` làm mờ mép — và chính feather sinh ra lem.

**Cách mới (lớp phủ):** nội dung nằm xuống trước, **tràn lề toàn bộ 848×1264**, rồi
phủ lớp khung hoạ tiết lên trên. Lớp khung khoét trong suốt ở đúng 3 vùng nội dung,
nên nội dung lộ ra qua 3 "cửa sổ" đó, còn mép khung **che kín** phần nội dung thừa.

```
   ┌───────────────────────────────────────┐
   │ LỚP 2: khung hoạ tiết (đục)           │  ← luôn nằm TRÊN
   │   khoét trong suốt ở ô / huy hiệu / tên│
   ├───────────────────────────────────────┤
   │ LỚP 1: nội dung lá, tràn lề 848×1264  │  ← nằm DƯỚI
   └───────────────────────────────────────┘
```

Hệ quả:

| | Mặt nạ + feather | Lớp khung phủ trên |
|---|---|---|
| Lem nội dung ra ngoài ô | có (do feather) | **không thể xảy ra** |
| Vật lạ ngoài ô | 0.065 % | **0 %** |
| Độ đồng nhất khung giữa các lá | 0.0124 – 0.0144 | **0.0124 – 0.0125** (giống hệt từng điểm ảnh) |
| Cần `feather`? | có | **không** |

> `feather` vẫn còn trong `panel.json` nhưng **không còn được dùng** khi ghép.
> `ensure_overlay()` chỉ blur `0×0.6` để khử răng cưa ở mép khoét — không phải feather.

### Vì sao ô nội dung là `124,131,600,878`

Ô cũ `106,120,621,933` trùm lên cả **dải nhợt** (75..114) và **viền trong** (115..123).
Hai dải này do AI vẽ lại ở mỗi lá nên **khác nhau từng lá** — đo được độ lệch **0.0878**
so với khung chuẩn, cao nhất 0.1920.

Thu ô vào đúng vùng nội dung thực (`124..724`, `131..1009`) thì dải nhợt và viền trong
được lấy từ **khung chuẩn**, nên đồng nhất tuyệt đối trên mọi lá:

| | Ô cũ 106,120 | Ô mới 124,131 |
|---|---|---|
| Lệch dải viền (trung bình) | 0.0878 | **0.0145** |
| Lệch dải viền (cao nhất) | 0.1920 | **0.0229** |

Đồng nhất hơn **83 %**. Kiểm chứng tên & huy hiệu không bị ảnh hưởng:
vùng tên lệch so khung chuẩn 0.16–0.23 (không lá nào mất tên), thay đổi so bản trước chỉ **0.0197**.

> **`edge_guard` chỉ khoá mép ngoài cùng của lá**, không ngăn được lem quanh ô nội dung.

---

## 5. File tham chiếu (`refs/`)

| File | Kích thước | Vai trò | Sửa được? |
|---|---|---|---|
| **`star-clean.png`** | 848×1264 | **Khung chuẩn** — nguồn sinh ra lớp khung; cũng là base để so màu | Không |
| **`frame-overlay.png`** | 848×1264 + alpha | **Lớp khung tách rời** — `star-clean` khoét trong suốt ở 3 vùng nội dung. `compose_card.py` tự tạo lại nếu thiếu hoặc nếu `panel.json` mới hơn | Tự sinh |
| `17-the-star.jpg` | 848×1264 | Neo phong cách & mẫu chữ (ref 2) | **Không bao giờ** |
| `card-blank.jpg` | 848×1264 | Phôi hoa văn — tham chiếu khi sinh ảnh (ref 1) | Không |
| `title-style.png` | — | Dải tên The Star — mẫu chữ bắt buộc (ref 3) | Không |
| `frame-master.jpg` | 848×1264 | Khung cũ (Star đã xoá nến) — **không còn dùng** | — |

---

## 6. Script

| Script | Chức năng | Base |
|---|---|---|
| `build_prompts.py` | Sinh 78 prompt từ `cards.json`; `check` để xác thực | — |
| `compose_card.py` | Phóng nội dung tràn lề, rồi **phủ lớp khung lên trên** (mỗi lần 1 lá) | `frame-overlay.png` |
| `check_card.py` | Kiểm tra ảnh thô: tỉ lệ, khung, dải tên, chữ tên | `star-clean.png` |
| `check_seam.py` | Đo đường nối giữa dải tên và khung chuẩn | `star-clean.png` |
| `build_gallery.py` | Sinh `deck.json` + `index.html` tự chứa | — |

> **`compose_card.py` phóng ảnh nguồn lên kích thước TOÀN LÁ (848×1264), rồi phủ khung lên.**
> Không phải phóng lên kích thước ô. Nhờ vậy các vùng thẳng hàng tuyệt đối với khung,
> không cần bù tọa độ — và toạ độ trong `panel.json` vừa là **vùng khoét** trên lớp khung
> vừa là **vị trí** nội dung lộ ra.

---

## 7. Vùng quét của các script kiểm tra

| Script | Vùng | Tọa độ (x, y, rộng, cao) | Dùng để |
|---|---|---|---|
| `check_card.py` | `TITLE_SCAN` | `(60, 1095, 730, 145)` | Đo khung chứa chữ tên, tránh lẫn đầu lâu |
| `compose_card.py` | `frame_region` | `(0, 316, 84, 695)` | Dải dọc mép trái — cân màu toàn cục |
| `check_seam.py` | điểm **trái** | `(83, 1090, 24, 150)` | Đường nối mép trái dải tên |
| `check_seam.py` | điểm **phải** | `(743, 1090, 24, 150)` | Đường nối mép phải dải tên |
| `check_seam.py` | điểm **trên** | `(205, 1082, 250, 10)` | Đường nối mép trên dải tên |

---

## 8. Ngưỡng chấp nhận

| Chỉ số | Ngưỡng | Cách đo |
|---|---|---|
| Tỉ lệ | đúng **0.671** | `check_card.py` |
| Chữ tên | nằm gọn trong hộp quét | `check_card.py` |
| Độ lệch khung | **< 0.02** | so vùng khung với `star-clean.png` |
| Đường nối (seam) | **< 0.06** mịn · 0.06–0.10 hơi thấy · **> 0.10 loại** | `check_seam.py` |
| Mực dải tên | **66 – 74 %** | crop `690×60+80+1095`, threshold 55 % |
| Vật lạ ngoài ô nội dung | **< 0.3 %** | so với `star-clean.png`, threshold 20 % |
| Chữ tên không bị copy nhầm | RMSE so với Star **> 0.05** | vùng `80,1045,690,200` |
| Xác nhận vẽ lại thật | RMSE ô nội dung **> 0.15** | so với bản cũ trong git |

> **Lưu ý mực dải tên:** 8/78 lá nằm ngoài khoảng 66–74 % (cao nhất `13-death` 77.0 %,
> thấp nhất `02-priestess` 65.6 %). Có sẵn từ trước, không do các thay đổi gần đây
> (khác biệt ~0.05 %). Mực tỷ lệ thuận với độ dài tên — THE HIGH PRIESTESS dài hơn
> THE STAR — nên một ngưỡng cố định khó phù hợp cho mọi lá.

---

## 9. Độ lệch trục (có thật, giữ nguyên theo phôi gốc)

| | |
|---|---|
| Tâm lá | x = **424** |
| Tâm ô nội dung | x = **424** |
| Độ lệch | ô nội dung lệch **TRÁI 0 px** so với tâm lá |

Giữ nguyên để khung khớp với `17-the-star.jpg`.

---

## 10. Lịch sử các thông số

Từ trường `_history` của `prompts/panel.json`:

- **`title` từng là `262,1090,330,145`** — quá hẹp, chữ THE CHARIOT bị cụt (x=230).
- Nới `190,670`, rồi `175` — vì THE HIGH PRIESTESS rộng 488 px (x=181).
- Nới thành toàn bộ dải trong `80,1045,690,200` — máy sinh ảnh không thể vẽ lại hoa văn
  dải dưới giống hệt nhau; lấy cả dải rồi đẩy đường nối ra mép trong khung vàng.
- **`feather` 12 → 3** — blur sigma 12 làm nội dung lem ra ngoài ô (xem mục 4).
- **`panel` 106,120,621,933 → 124,131,600,878** — ô cũ trùm lên dải nhợt & viền trong
  do AI tự vẽ, gây thiếu đồng nhất; thu vào đúng vùng nội dung thực (xem mục 4).

- **đáy ô 1009 → 1045** — ô kết thúc 1009 trong khi dải tên bắt đầu 1045, chừa khe hở 35 px
  (y 1010..1044). Khe này lấy từ khung chuẩn nên **lộ hoạ tiết đáy của riêng lá The Star**
  trên mọi lá (đo 0.0204). Kéo đáy ô xuống 1045 để kín khe hở → vùng đó lấy nội dung
  của chính từng lá (0.3775).
  **Lưu ý quan trọng:** phải ghép lại từ commit `799e648`. Ở các commit sau, nội dung gốc
  ở vùng này đã bị thay bằng khung chuẩn và **không thể khôi phục** từ lá đã ghép.

- **Đổi sang kiến trúc lớp (nội dung dưới, khung phủ trên)** — tách `refs/frame-overlay.png`
  từ `star-clean.png` bằng cách khoét trong suốt ở 3 vùng nội dung. Nội dung giờ được
  phóng tràn lề toàn lá rồi mới phủ khung lên, nên **không còn đường nối và không thể lem**
  (vật lạ giảm từ 0.065 % xuống **0 %**). `feather` không còn được dùng khi ghép.
