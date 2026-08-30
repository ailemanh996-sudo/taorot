#!/usr/bin/env python3
"""Hậu kỳ ảnh bài: chuẩn hoá 848x1264, strip metadata, nén về <=800KB (bắt đầu q90).

Dùng ImageMagick (`convert` / `magick`); tự dùng Pillow nếu có.

Cách dùng (từ repo root):
  # 1. Ảnh thô đã đặt tên đúng slug:  raw/wands-08.png ...
  python3 scripts/process_cards.py raw/

  # 2. Ảnh thô tên bất kỳ (ảnh AI tải về) -> gán theo thứ tự bộ bài
  python3 scripts/process_cards.py raw/ --autoname

  # 3. Một ảnh, chỉ định slug
  python3 scripts/process_cards.py raw/xyz.png --slug wands-08

Tuỳ chọn:
  --size WxH        mặc định 848x1264
  --fit cover|contain   cover = crop lấp đầy (mặc định), contain = vừa khung + nền parchment
  --max-kb 800      ngưỡng dung lượng, vượt thì giảm quality dần từ 90
  --bg '#e8dcc0'    màu nền khi --fit contain
  --trim           tự cắt dải viền ngoài (nền tối) còn sót lại trước khi resize
  --trim-thr 0.18  ngưỡng sáng để coi là "nội dung" (0-1)
  --dry-run         chỉ in kế hoạch
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
DATA = ROOT / "prompts" / "cards.json"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def imagemagick():
    if shutil.which("magick"):
        return ["magick"]
    if shutil.which("convert"):
        return ["convert"]
    return None


def deck_order():
    return [c["slug"] for c in json.loads(DATA.read_text(encoding="utf-8"))["cards"]]


def slug_from_name(path):
    """raw/wands-08.png -> wands-08 ; raw/Eight_of_Wands_v2.png -> None"""
    stem = path.stem.lower().replace("_", "-").replace(" ", "-")
    order = deck_order()
    if stem in order:
        return stem
    return None


def profile(path, axis, n=256):
    """Trung bình độ sáng theo cột (axis='col') hoặc hàng (axis='row')."""
    wh = subprocess.run(["identify", "-format", "%w %h", str(path)],
                        capture_output=True, text=True).stdout.split()
    w, h = (int(wh[0]), int(wh[1]))
    step = max(1, (w if axis == "col" else h) // n)
    vals = []
    for i in range(0, (w if axis == "col" else h), step):
        geo = (f"{step}x{h}+{i}+0" if axis == "col" else f"{w}x{step}+0+{i}")
        out = subprocess.run(["convert", str(path), "-crop", geo, "+repage", "-colorspace", "Gray",
                              "-format", "%[fx:mean]", "info:"], capture_output=True, text=True).stdout
        try:
            vals.append((i, float(out)))
        except ValueError:
            pass
    return vals, (w, h)


def trim_box(path, thr=0.18):
    """Tìm bbox nội dung theo ngưỡng sáng; trả (x, y, w, h) hoặc None."""
    cols, (w, h) = profile(path, "col")
    rows, _ = profile(path, "row")
    def span(vals, limit):
        hits = [i for i, v in vals if v > thr]
        if not hits:
            return 0, limit
        return min(hits), max(hits) + (vals[1][0] - vals[0][0] if len(vals) > 1 else 1)
    x0, x1 = span(cols, w)
    y0, y1 = span(rows, h)
    if x0 == 0 and y0 == 0 and x1 >= w and y1 >= h:
        return None
    return x0, y0, x1 - x0, y1 - y0


def target_size_kb(p, quality):
    return p.stat().st_size / 1024 if p.exists() else 10 ** 9


def process(src, dst, size, fit, max_kb, bg, dry, trim=None):
    w, h = (int(x) for x in size.lower().split("x"))
    im = imagemagick()
    if not im:
        sys.exit("Không tìm thấy ImageMagick (convert/magick) và Pillow cũng không có.")
    pre = []
    if trim is not None:
        box = trim_box(src, trim)
        if box:
            bx, by, bw, bh = box
            pre = ["-crop", f"{bw}x{bh}+{bx}+{by}", "+repage"]
            if dry:
                print(f"      trim: cắt viền ngoài -> {bw}x{bh} tại +{bx}+{by}")
    resize = (f"{w}x{h}^" if fit == "cover" else f"{w}x{h}")
    base = im + [str(src)] + pre + ["-strip", "-colorspace", "sRGB", "-resize", resize]
    if fit == "cover":
        base += ["-gravity", "center", "-extent", f"{w}x{h}"]
    else:
        base += ["-background", bg, "-gravity", "center", "-extent", f"{w}x{h}"]

    q = 90
    if dry:
        print(f"  [dry] {src.name} -> {dst.name}  {w}x{h} ({fit}) q<=90, <= {max_kb}KB")
        return None
    last = None
    while q >= 60:
        cmd = base + ["-quality", str(q), "-interlace", "Plane", str(dst)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        last = dst.stat().st_size / 1024
        if last <= max_kb:
            break
        q -= 5
    return last, q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="thư mục ảnh thô hoặc 1 file ảnh")
    ap.add_argument("--slug", help="slug đích (khi src là 1 file)")
    ap.add_argument("--name", help="tên file đích bất kỳ, không phải slug (vd: card-blank)")
    ap.add_argument("--autoname", action="store_true", help="gán slug theo thứ tự bộ bài")
    ap.add_argument("--size", default="848x1264")
    ap.add_argument("--fit", default="cover", choices=["cover", "contain"])
    ap.add_argument("--max-kb", type=int, default=800)
    ap.add_argument("--bg", default="#e8dcc0")
    ap.add_argument("--trim", nargs="?", type=float, const=0.18, default=None,
                    help="cắt dải viền ngoài tối, ngưỡng sáng 0-1 (mặc định 0.18)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    src = Path(a.src)
    files = [src] if src.is_file() else sorted(p for p in src.iterdir() if p.suffix.lower() in IMG_EXT)
    if not files:
        sys.exit(f"Không có ảnh trong {src}")

    CARDS.mkdir(exist_ok=True)
    jobs = []
    if a.name:
        jobs.append((files[0], a.name))
    elif src.is_file() and a.slug:
        jobs.append((files[0], a.slug))
    else:
        order = deck_order()
        pending = [s for s in order if not (CARDS / f"{s}.jpg").exists()]
        cursor = 0
        for f in files:
            s = slug_from_name(f)
            if s is None and a.autoname:
                if cursor >= len(pending):
                    print(f"  ! bỏ qua {f.name}: đã đủ 78 lá")
                    continue
                s = pending[cursor]
                cursor += 1
            if s is None:
                print(f"  ! bỏ qua {f.name}: không đoán được slug (đổi tên theo slug hoặc dùng --autoname)")
                continue
            jobs.append((f, s))

    print(f"{len(jobs)} ảnh -> {CARDS.relative_to(ROOT)}/  ({a.size}, {a.fit}, <= {a.max_kb}KB)")
    for f, s in jobs:
        dst = CARDS / f"{s}.jpg"
        r = process(f, dst, a.size, a.fit, a.max_kb, a.bg, a.dry_run, a.trim)
        if r:
            kb, q = r
            flag = "  <-- vẫn quá nặng" if kb > a.max_kb else ""
            print(f"  {s:<18} {kb:7.0f} KB  q{q}{flag}")
    print("xong.")


if __name__ == "__main__":
    main()
