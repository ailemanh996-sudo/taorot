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
| `feather` | **12 px** | Làm mờ mép mặt nạ (`-blur 0×12`) để đường nối không sắc |
| `edge_guard` | **18 px** | Nét đen dày 36 px sát mép ngoài — **khoá viền**, không cho feather lem ra khung |
| `bg` | `#e8dcc0` | Màu nền dự phòng khi ảnh nguồn thiếu chiều |
| `max_kb` | **800 KB** | Ngưỡng dung lượng; vượt thì giảm chất lượng 90 → 60 |

> **`edge_guard` là then chốt.** Bỏ nó thì feather 12 px sẽ làm nhòe mép ngoài
> và lộ nền đen — lỗi đã từng xảy ra trong dự án.

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
