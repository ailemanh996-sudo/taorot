# taorot

Bộ bài Tarot 78 lá — bản **Sensual Tarot** dựng trên lá phôi (blank ornamental template).

## Cấu trúc

```
cards/                    # card-blank.jpg (phôi) + 17-the-star.jpg (neo phong cách) — chưa có, cần thêm
prompts/
  00-MASTER-PROMPT.md     # template v2 + quy tắc chống đếm sai + chỉ thị nhân vật nữ
  01-CARD-TABLE.md        # bảng 78 lá (sinh tự động từ cards.json)
  cards.json              # nguồn dữ liệu duy nhất
  template.md             # template có placeholder
  out/<slug>.txt          # 78 prompt hoàn chỉnh, copy-paste trực tiếp
scripts/build_prompts.py  # check · prompt · all · md · batch
```

## Dùng nhanh

```bash
python3 scripts/build_prompts.py check            # validate 78 lá
python3 scripts/build_prompts.py prompt wands-08  # in prompt 1 lá
python3 scripts/build_prompts.py all              # xuất 78 prompt ra prompts/out/
python3 scripts/build_prompts.py md               # sinh lại prompts/01-CARD-TABLE.md
```

Sửa nội dung lá nào thì sửa trong `prompts/cards.json`, rồi chạy lại `all` + `md`.

## Hai điểm sửa của bản v2

1. **FULL BLEED** — lá bài phủ kín khung 848×1264, không viền tối / nền / bóng đổ (khoá ở prompt + `--trim` ở hậu kỳ).
2. **COUNT LOCK** — khoá số lượng cốc / xu / kiếm / gậy bằng 5 lớp (số+chữ · bố cục hình học ·
   nhóm con · cấm che khuất/cắt khung · lệnh tự kiểm đếm lại).
3. **FEMALE FIGURE DIRECTIVE** — tăng độ gợi cảm cho các lá nữ, vẫn trong giới hạn fine-art nudity.

Chi tiết: `prompts/00-MASTER-PROMPT.md`.
