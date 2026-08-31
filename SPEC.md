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

## 2. Sơ đồ tọa độ

```
   x→0                                                      848
  +------------------------------------------------------------+
  |  MEDALION         +--------------------+                   |
  |  350 x 115        |                    |                   |
  |                   +--------------------+                   |
  |        +------------------------------------------+        |
  |        |                                          |        |
  |        |  Ô NỘI DUNG (panel)                      |        |
  |        |  621 x 933 px                            |        |
  |        |                                          |        |
  |        |                                          |        |
  |        |  ← cảnh riêng từng lá →                  |        |
  |        |                                          |        |
  |        |                                          |        |
  |        |  (106,120) → (727,1053)                  |        |
  |        |                                          |        |
  |        |                                          |        |
  |        +------------------------------------------+        |
  |      +-----------------------------------------------+     |
  |      | DẢI TÊN (title) 690 x 200 — chữ dưới đầu lâu  |     |
  |      +-----------------------------------------------+     |
  +------------------------------------------------------------+
0 / 106 / 727 / 848
```

---

## 3. Bảng tọa độ các vùng

Tọa độ theo chuẩn ImageMagick: `x,y` là góc trên-trái, rồi đến `rộng × cao`.

| Vùng | Góc (x,y) | Kích thước | Góc đối diện | Nội dung |
|---|---|---|---|---|
| **Ô nội dung** `panel` | `106,120` | 621 × 933 | `727,1053` | Cảnh của lá — phần duy nhất thay đổi giữa các lá |
| **Medalion** `emblem` | `250,10` | 350 × 115 | `600,125` | Huy hiệu riêng của lá, không chữ, không số |
| **Dải tên** `title` | `80,1045` | 690 × 200 | `770,1245` | Toàn bộ dải hoa văn dưới, lấy nguyên từ lá nguồn |

### Dải khung — phần ngoài ô nội dung, giống hệt nhau ở mọi lá

| Cạnh | Khoảng | Độ dày |
|---|---|---|
| Trái | x 0 → 106 | **106 px** |
| Phải | x 727 → 848 | **121 px** |
| Trên | y 0 → 120 | **120 px** |
| Dưới | y 1053 → 1264 | **211 px** |

---

## 4. Thông số viền & ghép

| Thông số | Giá trị | Ý nghĩa |
|---|---|---|
| `feather` | **3 px** | Làm mờ mép mặt nạ (`-blur 0×3`) để đường nối không sắc |
| `edge_guard` | **18 px** | Nét đen dày 36 px sát mép ngoài — **khoá viền**, không cho feather lem ra khung |
| `bg` | `#e8dcc0` | Màu nền dự phòng khi ảnh nguồn thiếu chiều |
| `max_kb` | **800 KB** | Ngưỡng dung lượng; vượt thì giảm chất lượng 90 → 60 |

### Vì sao `feather` là 3 mà không phải 12

`feather` là độ lệch chuẩn (sigma) của bộ lọc làm mờ Gaussian. Dải chuyển tiếp trải ra
khoảng **±3 sigma** quanh mép ô:

| `feather` | Dải chuyển | Hậu quả |
|---|---|---|
| 12 | ±36 px | Nội dung lá lem ~32 px **ra ngoài** ô, khung lem ~44 px **vào trong** ô |
| **3** | **±9 px** | Lem chỉ còn ~8 px |

Đo trên 78 lá (vành sát mép ô, so với base):

| | feather 12 | feather 3 |
|---|---|---|
| Lem trung bình | 0.0520 | **0.0206** (giảm 60 %) |
| Lem cao nhất (`pentacles-09`) | 0.1595 | **0.0830** (giảm 48 %) |
| Vật lạ ngoài ô | 0.281 % | **0.065 %** |
| Seam trung bình | 0.0438 | 0.0473 (tệ thêm 0.0035) |

> **`edge_guard` vẫn giữ nguyên 18 px.** Nó chỉ khoá mép *ngoài cùng* của lá,
> không can thiệp vào mép ô nội dung — nên không ngăn được lem quanh ô.

---

## 5. File tham chiếu (`refs/`)

| File | Kích thước | Vai trò | Sửa được? |
|---|---|---|---|
| **`star-clean.png`** | 848×1264 | **Khung chuẩn — base mặc định** để ghép mọi lá | Không |
| `17-the-star.jpg` | 848×1264 | Neo phong cách & mẫu chữ (ref 2) | **Không bao giờ** |
| `card-blank.jpg` | 848×1264 | Phôi hoa văn — tham chiếu khi sinh ảnh (ref 1) | Không |
| `title-style.png` | — | Dải tên The Star — mẫu chữ bắt buộc (ref 3) | Không |
| `frame-master.jpg` | 848×1264 | Khung cũ (Star đã xoá nến) — **không còn dùng** | — |

---

## 6. Script

| Script | Chức năng | Base |
|---|---|---|
| `build_prompts.py` | Sinh 78 prompt từ `cards.json`; `check` để xác thực | — |
| `compose_card.py` | Dán 3 vùng nội dung lên khung chuẩn (mỗi lần 1 lá) | `star-clean.png` |
| `check_card.py` | Kiểm tra ảnh thô: tỉ lệ, khung, dải tên, chữ tên | `star-clean.png` |
| `check_seam.py` | Đo đường nối giữa dải tên và khung chuẩn | `star-clean.png` |
| `build_gallery.py` | Sinh `deck.json` + `index.html` tự chứa | — |

> **`compose_card.py` phóng to ảnh nguồn lên kích thước TOÀN LÁ (848×1264), rồi mới dán.**
> Không phải phóng lên kích thước ô (621×933). Nhờ vậy các vùng nội dung thẳng hàng
> tuyệt đối với khung, không cần bù tọa độ.

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

> **Lưu ý về mực dải tên:** 8/78 lá đang nằm ngoài khoảng 66–74 %
> (cao nhất `13-death` 77.0 %, thấp nhất `02-priestess` 65.6 %). Đây là tình trạng
> **có sẵn từ trước**, không do thay đổi `feather` (khác biệt chỉ ~0.05 %).
> Mực dải tên tỷ lệ thuận với độ dài tên — THE HIGH PRIESTESS dài hơn THE STAR —
> nên ngưỡng cố định này có thể không phù hợp cho mọi lá.

---

## 9. Độ lệch trục (có thật, giữ nguyên theo phôi gốc)

| | |
|---|---|
| Tâm lá | x = **424** |
| Tâm ô nội dung | x = **416** |
| Độ lệch | ô nội dung lệch **TRÁI 8 px** so với tâm lá |
| Dải khung trái / phải | **106 px** / **121 px** — chênh **15 px** |

Giữ nguyên để khung khớp với `17-the-star.jpg`. Nếu muốn căn lại cho cân đối,
phải đổi `panel` **và** ghép lại toàn bộ 78 lá.

---

## 10. Lịch sử các thông số

Từ trường `_history` của `prompts/panel.json`:

- **`title` từng là `262,1090,330,145`** — quá hẹp, chữ THE CHARIOT bị cụt (bắt đầu ở x=230).
- Nới thành `190,670`, rồi `175` — vì THE HIGH PRIESTESS rộng 488 px (bắt đầu ở x=181).
- **Nới tiếp thành toàn bộ dải trong** `80,1045,690,200` — máy sinh ảnh không thể vẽ lại
  hoa văn dải dưới giống hệt nhau; dán một ô nhỏ sẽ lộ hình chữ nhật. Lấy cả dải từ lá nguồn
  và đẩy đường nối ra sát mép trong khung vàng, nơi đường viền tự nhiên che khuất.
- **`feather` 12 → 3** — vì blur sigma 12 làm nội dung lem ra ngoài ô (xem mục 4).
