#!/usr/bin/env python3
"""Đo độ khớp của một lá thô so với khung chuẩn, trước khi ghép.

Báo cáo 3 con số cho mỗi ảnh:
  frame  — RMSE dải khung trái (hoạ tiết viền + màu của khung)
  band   — RMSE dải dưới, TRỪ vùng chữ tên (dải tên có hoạ tiếu khác khung chuẩn không?)
  title  — toạ độ thực của chữ tên + có nằm gọn trong hộp tên (prompts/panel.json) không

frame/band càng thấp càng tốt (< 0.02 = khớp, > 0.08 = lá này lệch khung, nên tạo lại).
Dùng để chọn giữa nhiều bản (variant) của cùng một lá.

  python3 scripts/check_card.py raw/01-magician.png raw/variants/01-magician-b.png
  python3 scripts/check_card.py raw/           # tất cả ảnh thô
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_card import (CARDS, ROOT, channel_stats, frame_region, im, load_panel,  # noqa: E402
                         ref, run)

BAND = (60, 1050, 730, 200)   # vùng dải tên, đo `band` (cả hoạ tiết)
TITLE_SCAN = (60, 1095, 730, 145)  # chỉ dải chữ, để đo bbox chữ (tránh lẫn đầu lâu)


def prep(src, dst, W, H):
    """Đưa ảnh thô về đúng khung (W,H); trả về tỉ lệ gốc để cảnh báo lệch."""
    cmd = im() + [str(src)]
    wh = run(["identify", "-format", "%wx%h", str(src)]).stdout.strip()
    if run(im() + [str(src), "-fuzz", "8%", "-trim", "-format", "%wx%h", "info:"]).stdout.strip() != wh:
        cmd += ["-fuzz", "8%", "-trim", "+repage"]
    cmd += ["-strip", "-colorspace", "sRGB", "-resize", f"{W}x",
            "-gravity", "center", "-background", "#e8dcc0", "-extent", f"{W}x{H}", str(dst)]
    run(cmd)
    return dst


def colormatch(src, dst, base, region):
    sb, ss = channel_stats(base, region), channel_stats(src, region)
    cmd = im() + [str(src)]
    for i, ((mb, sb_), (ms, ss_)) in enumerate(zip(sb, ss)):
        a = max(0.5, min(2.0, sb_ / ss_ if ss_ > 1e-6 else 1.0))
        b = mb - a * ms
        cmd += ["-channel", "RGB"[i], "-function", "Polynomial", f"{a:.6f},{b:.6f}"]
    cmd += ["+channel", str(dst)]
    run(cmd)
    return dst


def rmse(a, b):
    r = run(im() + [str(a), str(b), "-metric", "RMSE", "-compare",
                    "-format", "%[distortion]", "info:"])
    try:
        return float(r.stdout.strip().split()[0])
    except Exception:
        return float("nan")


def crop(src, dst, reg):
    x, y, w, h = reg
    run(im() + [str(src), "-crop", f"{w}x{h}+{x}+{y}", "+repage", str(dst)])
    return dst


def band_rmse_outside_title(src, base, tmp, title_box):
    """RMSE dải dưới, bỏ qua hộp chữ tên (đo 2 mảnh trái/phải của hộp)."""
    x, y, w, h = BAND
    tx, ty, tw, th = title_box
    parts = []
    if tx > x:                       # mảnh trái hộp tên
        parts.append((x, y, max(0, tx - x), h))
    if tx + tw < x + w:              # mảnh phải hộp tên
        parts.append((tx + tw, y, x + w - (tx + tw), h))
    vals = []
    for i, r in enumerate(parts):
        if r[2] <= 0:
            continue
        crop(src, tmp / f"bs{i}.png", r)
        crop(base, tmp / f"bb{i}.png", r)
        vals.append(rmse(tmp / f"bs{i}.png", tmp / f"bb{i}.png"))
    return max(vals) if vals else float("nan")


def title_bbox(src, base, tmp, rel=0.35):
    global BAND
    """Tìm vùng chữ tên bằng profile cột/hàng của ảnh sai khác.

    Ngưỡng TUYỆT ĐỐI bắt nhầm cả hoạ tiết dải (vì dải các lá luôn hơi khác khung chuẩn),
    nên dùng ngưỡng TƯƠNG ĐỐI: lấy đoạn liên tiếp mà profile > rel * đỉnh.
    """
    saved = BAND
    BAND = TITLE_SCAN
    crop(src, tmp / "ts.png", BAND)
    crop(base, tmp / "tb.png", BAND)
    run(im() + [str(tmp / "tb.png"), str(tmp / "ts.png"), "-compose", "Difference", "-composite",
                "-colorspace", "Gray", str(tmp / "td.png")])
    x, y, w, h = BAND

    def profile(geo, n):
        out = run(im() + [str(tmp / "td.png"), "-resize", geo, "-depth", "8", "txt:-"]).stdout
        vals = []
        for line in out.splitlines()[1:]:
            m = re.match(r"(\d+),(\d+):\s*\(\s*(\d+)", line)
            if m:
                vals.append(int(m.group(3)))
        return vals[:n]

    cols = profile(f"{w}x1!", w)
    rows = profile(f"1x{h}!", h)

    def span(vals):
        if not vals:
            return None
        peak = max(vals)
        if peak < 15:                      # khác biệt quá nhỏ -> không có chữ
            return None
        cut = peak * rel
        idx = [i for i, v in enumerate(vals) if v > cut]
        return min(idx), max(idx) + 1

    sc, sr = span(cols), span(rows)
    BAND = saved
    if not sc or not sr:
        return None
    return (TITLE_SCAN[0] + sc[0], TITLE_SCAN[1] + sr[0], sc[1] - sc[0], sr[1] - sr[0])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        return 1
    panel = load_panel()
    W, H = panel["size"]
    base = ref("frame-master.jpg")
    tmp = Path("/tmp/_check")
    tmp.mkdir(exist_ok=True)

    files = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            files += sorted(x for x in p.iterdir()
                            if x.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
        else:
            files.append(p)

    print(f"{'ảnh':<22}{'tỉ lệ':>7}{'frame':>8}{'band':>8}   chữ tên (x,y,w,h)        khớp hộp?")
    print("-" * 88)
    results = []
    for f in files:
        ow, oh = (int(v) for v in run(["identify", "-format", "%w %h", str(f)]).stdout.split())
        ratio = ow / oh
        prep(f, tmp / "s.png", W, H)
        colormatch(tmp / "s.png", tmp / "m.png", base, frame_region(W, H, panel))
        fr = rmse(*(crop(x, tmp / f"c{i}.png", frame_region(W, H, panel))
                    for i, x in enumerate((tmp / "m.png", base))))
        bd = band_rmse_outside_title(tmp / "m.png", base, tmp, panel["title"])
        bb = title_bbox(tmp / "m.png", base, tmp)
        tx, ty, tw, th = panel["title"]
        fits = bb is not None and bb[0] >= tx and bb[0] + bb[2] <= tx + tw \
            and bb[1] >= ty and bb[1] + bb[3] <= ty + th
        rflag = f"{ratio:.3f}{'!' if abs(ratio - W / H) > 0.01 else ' '}"
        print(f"{f.stem:<22}{rflag:>7}{fr:8.4f}{bd:8.4f}   "
              f"{str(bb) if bb else '(không thấy)':<24}  {'OK' if fits else '← VƯỢT HỘP'}")
        results.append((f, fr, bd, fits))
    print("-" * 88)
    print(f"tỉ lệ chuẩn {W/H:.3f} (! = lệch, cần tạo lại) · khung < 0.02 · dải tên < 0.05 · chữ nằm gọn trong hộp")
    ok = [r for r in results if r[3]]
    if len(ok) > 1:
        best = min(ok, key=lambda r: r[1] + r[2])
        print(f"→ bản tốt nhất: {best[0]}  (frame {best[1]:.4f} + band {best[2]:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
