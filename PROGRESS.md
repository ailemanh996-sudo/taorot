# Tiến độ bộ bài Taorot

**78 / 78 — HOÀN THÀNH** · kèm **mặt sau lá bài**

## Mặt sau đã chọn

`backs/card-back.jpg` — 848 × 1264 (tỉ lệ 0.671, khớp mặt trước)

| | |
|---|---|
| Chủ đề | Hai thiên thần nhỏ ở **tư thế đối ngược**: một ở dưới cúi nhìn xuống, một ở trên ngẩng nhìn lên |
| Đối xứng | **0.2108 — đối thế chủ ý, không phải ảnh gương** |
| Đồng nhất màu | lệch sáng 17.7 · **1 tông màu** (nền giấy cổ + vàng cổ) |

Bản này **cố ý không đối xứng gương**: hai thiên thần ở tư thế trái ngược nhau thì không thể đồng thời là ảnh phản chiếu của nhau. Đây là lựa chọn đã được xác nhận.

Các phương án khác lưu ở `backs/options/` (back-01 … back-06).

| Bộ bài | Số lá | Trạng thái |
|---|---|---|
| Ẩn Chính (Major Arcana) | 22 / 22 | ✅ xong |
| Gậy (Wands) | 14 / 14 | ✅ xong |
| Cốc (Cups) | 14 / 14 | ✅ xong |
| Kiếm (Swords) | 14 / 14 | ✅ xong |
| Tiền (Pentacles) | 14 / 14 | ✅ xong |

```
Ẩn Chính  ██████████████████████  22/22
Gậy       ██████████████         14/14
Cốc       ██████████████         14/14
Kiếm      ██████████████         14/14
Tiền      ██████████████         14/14
```

---

## Chất lượng đo được (toàn bộ 78 lá)

| Chỉ số | Kết quả | Ngưỡng |
|---|---|---|
| Tỉ lệ khung 848 × 1264 | 78 / 78 | 0.671 |
| Chữ tên nằm gọn trong hộp | 78 / 78 | OK |
| Đường nối (seam) — 234 điểm đo | **trung bình 0.0389** | < 0.06 mịn |
| — thấp nhất | 0.0282 | |
| — cao nhất | **0.0809** (`pentacles-10`) | < 0.10 đạt |
| Lá mịn hoàn toàn | **77 / 78** | |
| Mực dải tên | 66 – 74 % | 66 – 74 % |
| Vật lạ lọt vào khung | cao nhất 0.29 % | < 0.3 % |

`pentacles-10` là lá duy nhất có một điểm đo ở mức 0.0809 (*hơi thấy*) — vẫn dưới ngưỡng 0.10.

---

## Quy trình 6 bước

1. Sửa dữ liệu trong `prompts/cards.json` (không viết tay 78 chuỗi prompt)
2. `python3 scripts/build_prompts.py all` rồi `check` → phải báo `78 cards, 0 error(s), 0 warning(s)`
3. `generate_image` với 3 ảnh tham chiếu → `raw/<slug>.png`
4. `scripts/check_card.py raw/` → tỉ lệ 0.671, chữ tên `OK`
5. `scripts/compose_card.py raw/<slug>.png` (**một lá mỗi lần**) rồi `scripts/check_seam.py`
6. `scripts/build_gallery.py` → commit + push

---

## Các lỗi đã giải quyết

| Lỗi | Cách xử lý |
|---|---|
| AI đếm sai số vật (chén / gậy / kiếm / tiền) | **COUNT LOCK** chia nhóm + **đếm khe hở** |
| Nhóm vật bị vẽ thừa | Gọi đích danh lỗi trong prompt: *"lá này đã hỏng, từng ra 9 kiếm"* |
| Cảnh tối làm dải tên bị tối | **BAND TONE LOCK** + đo % mực (phát hiện `swords-06` 85.6 %) |
| **Chữ "dark" lặp nhiều lần làm tối cả dải tên** | Tránh hẳn chữ "dark" — `swords-king` từ 80.1 % mực xuống 69.7 % |
| Lửa nến của The Star lọt sang mọi lá | Tạo `refs/star-clean.png` — khung chuẩn, đặt làm base mặc định |
| Ref 2 rò rỉ nội dung | Điều **REFERENCE DISCIPLINE**: ref 2 chỉ cung cấp phong cách |
| Cánh thiên thần bị ngược ở tư thế nhìn sau | Dùng góc ba-phần-tư |
| Kiểm duyệt chặn ảnh mô tả khoả thân | **Tả vải trước, cơ thể sau**; đổi "khoả thân" → "vai trần" |
| Sửa đi sửa lại làm hỏng đường nối | Nếu cần sửa lần hai → **vẽ lại từ đầu** |
| Huy hiệu "thiên thần nhỏ" tự gắn cánh cho nhân vật | Đổi thành "chạm bướm" |
| Mâu thuẫn giữa trường `scene` và `hair` | Luôn đối chiếu hai trường trước khi tạo |

---

## Việc còn mở

1. **Đếm số vật bằng mắt** trên 56 lá Ẩn phụ — máy không đếm được, cần người xem
2. Xác nhận chữ "XVII" đã biến mất khỏi medalion của The Star (không có OCR)
3. Đo lại vòng 6 px bên trong khung
4. `00-fool` (0.0627) và `17-the-star` (0.0832) là hai lá có dải tên yếu nhất
5. `pentacles-10` — điểm đo trên cùng 0.0809, có thể làm lại nếu thấy rõ

---

## Cấu trúc thư mục

- `prompts/cards.json` — dữ liệu gốc của 78 lá
- `prompts/template.md` — khuôn prompt chung
- `prompts/out/` — 78 file prompt đã sinh
- `scripts/` — `build_prompts.py`, `check_card.py`, `compose_card.py`, `check_seam.py`, `build_gallery.py`
- `cards/` — **78 lá hoàn chỉnh** (tác phẩm bền vững)
- `refs/` — `card-blank.jpg` (tham chiếu sinh ảnh), `17-the-star.jpg` (neo phong cách, không sửa),
  `title-style.png` (mẫu chữ), **`star-clean.png` (khung chuẩn — base mặc định)**, `frame-master.jpg` (cũ, không còn dùng)
- `raw/` — ảnh thô, **không lưu vào git**
