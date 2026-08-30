# Tiến độ bộ bài Tarot — 78 lá

_Cập nhật: 2026-08-30_
_Commit: `b14301d`_

## Tổng quan: **50/78 lá (64%)**

| Bộ | Trạng thái | Xong |
|---|---|---|
| Ẩn chính | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ | **22/22** |
| Wands — Gậy | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ | **14/14** |
| Cups — Chén | ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ | **14/14** |
| Swords — Kiếm | ░░░░░░░░░░░░░░ | **0/14** |
| Pentacles — Xu | ░░░░░░░░░░░░░░ | **0/14** |

## Chất lượng (đo tự động, 50 lá đã có)

| Chỉ số | Kết quả | Ngưỡng |
|---|---|---|
| Tỉ lệ 848×1264 | 50/50 đạt | đúng 0.671 |
| Đường nối (seam) | 0.034 – 0.057, trung bình 0.042 | < 0.06 mịn |
| Chữ tên nằm trong hộp | 50/50 đạt | — |
| Vật lạ trong khung | 0.004% – 0.200%, trung bình 0.114% | < 0.3% |
| Khung đồng nhất toàn bộ | có (`compose_card.py` dập từ `frame-master.jpg`) | — |

### 10 lá đường nối mịn nhất

| Lá | Seam |
|---|---|
| `cups-10` | 0.0335 |
| `cups-04` | 0.0336 |
| `20-judgement` | 0.0342 |
| `cups-king` | 0.0342 |
| `11-justice` | 0.0348 |
| `09-hermit` | 0.0351 |
| `cups-knight` | 0.0353 |
| `00-fool` | 0.0354 |
| `05-hierophant` | 0.0354 |
| `cups-06` | 0.0354 |

## Việc đã giải quyết

- **Hai cây nến dính khung**: nằm trong ảnh nền `frame-master`; xoá bằng cách tạo lá Star sạch rồi lấy mặt nạ. Từ 3.94% xuống 0.000%.
- **Máy chép bối cảnh lá Star**: prompt từng chỉ nói "vẽ theo phong cách". Thêm điều khoản **REFERENCE DISCIPLINE** — ảnh tham khảo 2 chỉ cung cấp phong cách, cấm chép nội dung.
- **Đếm sai số vật**: mỗi lá có phép cộng riêng (`1+5`, `3+3+2`, `4+4+2`, `3×3`). Huy hiệu `wands-06` dùng mẹo đếm **khe hở** thay vì đếm thân.
- **Thừa tay**: thêm `extra arm, three arms, more than two arms` vào NEGATIVE chung của template.
- **Cánh ngược chiều**: thêm luật "nếu nhân vật nhìn từ sau, cánh cũng nhìn từ sau".
- **Kiểm duyệt từ chối ảnh**: đổi sang lối tả vải trước — "vai trần", "lụa ướt dính", "nghiên cứu nhân thể cổ điển".

## Còn mở

1. Xác nhận chữ **XVII** đã mất khỏi huy hiệu lá Star (không có OCR trong môi trường — cần soi bằng mắt).
2. Đo lại vòng 6 px quanh mép trong (lần đo trước 0.11–0.38, chưa đo lại từ khi có nền mới).
3. Bộ **Swords** (14 lá) và **Pentacles** (14 lá).

## Quy trình (mỗi lá)

```
1. python3 scripts/build_prompts.py all      # sinh prompt từ cards.json
2. generate_image  (3 ảnh tham khảo: card-blank, 17-the-star, title-style)
3. python3 scripts/check_card.py raw/<slug>.png
4. python3 scripts/compose_card.py raw/<slug>.png
5. python3 scripts/check_seam.py <slug>
6. python3 scripts/build_gallery.py
```
