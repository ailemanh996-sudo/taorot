#!/usr/bin/env python3
"""Ghép nội dung lá bài lên KHUNG CHUẨN để mọi lá đồng nhất hoạ tiết + màu.

Ý tưởng: lấy 17-the-star.jpg làm "khung chuẩn" (base). Từ mỗi lá AI sinh ra chỉ giữ lại
3 vùng nội dung riêng — cảnh ở giữa, emblem trong medallion, chữ tên ở dải dưới — dán lên
base với viền mềm (feather). Phần còn lại (khung vàng, 4 góc filigree, medallion, đầu lâu)
là của base nên GIỐNG HỆT NHAU trên mọi lá. Trước khi dán, ảnh được cân màu theo base.

Dùng:
  python3 scripts/compose_card.py raw/                      # ghép tất cả ảnh trong raw/
  python3 scripts/compose_card.py raw/08-strength.png       # một lá
  python3 scripts/compose_card.py --check                   # đo độ lệch khung/màu hiện tại
  python3 scripts/compose_card.py raw/ --base refs/17-the-star.jpg

Vùng dán lấy từ prompts/panel.json (có thể chỉnh tay).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
REFS = ROOT / "refs"          # ảnh MẪU (không phải lá bài): khung trống, khung chuẩn, mẫu chữ


def ref(name):
    """Đường dẫn ảnh mẫu. Ưu tiên refs/, fallback về cards/ (tương thích ngược)."""
    p = REFS / name
    return p if p.exists() else CARDS / name
PANEL = ROOT / "prompts" / "panel.json"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}

DEFAULT_PANEL = {
    "panel": [106, 120, 621, 933],
    "emblem": [250, 10, 350, 115],
    "title": [262, 1090, 330, 145],
    "feather": 12,
    "edge_guard": 18,
    "size": [848, 1264],
    "max_kb": 800,
}


def im():
    return ["magick"] if shutil.which("magick") else ["convert"]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def size_of(path):
    out = run(["identify", "-format", "%w %h", str(path)]).stdout.split()
    return int(out[0]), int(out[1])


def channel_stats(path, region):
    """mean/sd từng kênh RGB trong một vùng."""
    x, y, w, h = region
    tmp = Path("/tmp/_stat.png")
    run(im() + [str(path), "-crop", f"{w}x{h}+{x}+{y}", "+repage", str(tmp)])
    out = []
    for ch in "RGB":
        r = run(im() + [str(tmp), "-channel", ch, "-separate", "-format",
                        "%[fx:mean] %[fx:standard_deviation]", "info:"])
        m, s = (float(v) for v in r.stdout.split())
        out.append((m, s))
    return out


def frame_region(W, H, panel):
    """Dải dọc mép trái — thuần khung vàng/hoạ tiết, dùng để cân màu và đo độ lệch."""
    return (0, int(H * 0.25), int(W * 0.10), int(H * 0.55))


def color_match(src, dst, base, region):
    """Chỉnh src theo thống kê màu của base trong region -> dst."""
    sb = channel_stats(base, region)
    ss = channel_stats(src, region)
    cmd = im() + [str(src)]
    for idx, ((mb, sb_), (ms, ss_)) in enumerate(zip(sb, ss)):
        a = sb_ / ss_ if ss_ > 1e-6 else 1.0
        a = max(0.5, min(2.0, a))
        b = mb - a * ms
        ch = "RGB"[idx]
        # IM: Polynomial lấy hệ số theo luỹ thừa GIẢM dần -> "a,b" = a*x + b
        cmd += ["-channel", ch, "-function", "Polynomial", f"{a:.6f},{b:.6f}"]
    cmd += ["+channel", str(dst)]
    run(cmd)
    return dst


def match_band(src, base, tmp, panel):
    """Cân màu RIÊNG cho dải dưới.

    Cân màu toàn cục lấy mẫu ở khung trái; nhưng nhiều lá (vd The Hanged Man) có dải dưới
    lệch sáng/màu đồng đều so với khung chuẩn trong khi khung lại khớp -> khi dán ô chữ tên
    lên sẽ lộ một mảng khác màu. Ở đây tính hệ số trên hai mảnh bên trái/phải của hộp tên
    (tức phần dải sẽ bị thay bằng khung chuẩn) rồi áp dụng cho toàn dải.
    """
    W, H = panel["size"]
    y0, h = 1045, 200                      # dải dưới
    tx, ty, tw, th = panel["title"]
    regs = [(0, y0, tx, h), (tx + tw, y0, W - (tx + tw), h)]
    regs = [r for r in regs if r[2] > 20]

    def stat_pair(img, tag):
        parts = []
        for i, r in enumerate(regs):
            f = tmp / f"{tag}{i}.png"
            run(im() + [str(img), "-crop", f"{r[2]}x{r[3]}+{r[0]}+{r[1]}", "+repage", str(f)])
            parts.append(str(f))
        out = tmp / f"{tag}_all.png"
        run(im() + parts + ["+append", str(out)])
        return channel_stats(out, (0, 0, *size_of(out)))

    sb, ss = stat_pair(base, "b"), stat_pair(src, "s")
    band = tmp / "band.png"
    run(im() + [str(src), "-crop", f"{W}x{h}+0+{y0}", "+repage", str(band)])
    cmd = im() + [str(band)]
    for i, ((mb, sb_), (ms, ss_)) in enumerate(zip(sb, ss)):
        a = max(0.5, min(2.0, sb_ / ss_ if ss_ > 1e-6 else 1.0))
        b = mb - a * ms
        cmd += ["-channel", "RGB"[i], "-function", "Polynomial", f"{a:.6f},{b:.6f}"]
    cmd += ["+channel", str(tmp / "band2.png")]
    run(cmd)
    run(im() + [str(src), str(tmp / "band2.png"), "-geometry", f"+0+{y0}",
                "-compose", "over", "-composite", str(src)])
    return src


def build_mask(path, panel, W, H):
    cmd = im() + ["-size", f"{W}x{H}", "xc:black", "-fill", "white"]
    for key in ("panel", "emblem", "title"):
        x, y, w, h = panel[key]
        cmd += ["-draw", f"rectangle {x},{y} {x + w - 1},{y + h - 1}"]
    cmd += ["-blur", f"0x{panel['feather']}"]
    # khoá mép ngoài: luôn giữ nguyên khung chuẩn, feather không được lem ra viền
    guard = panel.get("edge_guard", 18)
    cmd += ["-stroke", "black", "-strokewidth", str(guard * 2), "-fill", "none",
            "-draw", f"rectangle 0,0 {W - 1},{H - 1}", str(path)]
    run(cmd)
    return path


def compose(src, base, out, panel):
    W, H = panel["size"]
    tmp = Path("/tmp/_compose")
    tmp.mkdir(exist_ok=True)
    work = tmp / "work.png"
    mask = tmp / "mask.png"

    # 1. đưa về đúng kích thước chuẩn
    cmd = im() + [str(src)]
    if run(im() + [str(src), "-fuzz", "8%", "-trim", "-format", "%wx%h", "info:"]).stdout.strip() \
            != f"{size_of(src)[0]}x{size_of(src)[1]}":
        cmd += ["-fuzz", "8%", "-trim", "+repage"]
    # fixed aspect: co theo chiều ngang (giữ tỉ lệ nhân vật như nhau giữa các lá),
    # rồi crop/pad chiều dọc về đúng H — thay vì cover-crop làm cảnh bị cắt khác nhau
    cmd += ["-strip", "-colorspace", "sRGB", "-resize", f"{W}x",
            "-gravity", "center", "-background", panel.get("bg", "#e8dcc0"),
            "-extent", f"{W}x{H}", str(work)]
    run(cmd)

    # 2. cân màu toàn cục theo khung chuẩn, rồi cân riêng dải dưới
    color_match(work, work, base, frame_region(W, H, panel))
    match_band(work, base, tmp, panel)

    # 3. dán 3 vùng nội dung lên khung chuẩn
    build_mask(mask, panel, W, H)
    run(im() + [str(base), str(work), str(mask), "-composite", str(tmp / "out.png")])

    # 4. nén: q90, giảm dần nếu vượt ngưỡng
    q = 90
    while q >= 60:
        run(im() + [str(tmp / "out.png"), "-strip", "-quality", str(q),
                    "-interlace", "Plane", str(out)])
        if out.stat().st_size / 1024 <= panel["max_kb"]:
            break
        q -= 5
    return out.stat().st_size / 1024, q


def diff_region(a, b, region):
    x, y, w, h = region
    r = run(im() + [str(a), "-crop", f"{w}x{h}+{x}+{y}", "+repage",
                    "(", "+clone", ")", "(+clone)"])
    # đơn giản: dùng compare với RMSE
    tmp = Path("/tmp/_cmp")
    tmp.mkdir(exist_ok=True)
    ca, cb = tmp / "a.png", tmp / "b.png"
    run(im() + [str(a), "-crop", f"{w}x{h}+{x}+{y}", "+repage", str(ca)])
    run(im() + [str(b), "-crop", f"{w}x{h}+{x}+{y}", "+repage", str(cb)])
    r = run(im() + [str(ca), str(cb), "-metric", "RMSE", "-compare",
                    "-format", "%[distortion]", "info:"])
    try:
        return float(r.stdout.strip().split()[0])
    except Exception:
        return float(r.stderr.strip().split()[0]) if r.stderr else -1


def load_panel():
    if PANEL.exists():
        cfg = json.loads(PANEL.read_text())
        return {**DEFAULT_PANEL, **cfg}
    return dict(DEFAULT_PANEL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", help="thư mục hoặc file ảnh nguồn")
    ap.add_argument("--base", default=str(ref("frame-master.jpg")))
    ap.add_argument("--out", default=str(CARDS))
    ap.add_argument("--check", action="store_true", help="đo độ lệch khung giữa các lá")
    a = ap.parse_args()

    panel = load_panel()
    base = Path(a.base)
    if not base.exists():
        sys.exit(f"thiếu khung chuẩn {base}")

    if a.check or not a.src:
        W, H = panel["size"]
        reg = frame_region(W, H, panel)
        print(f"Độ lệch vùng khung so với {base.name} (RMSE, 0 = giống hệt):")
        for f in sorted(CARDS.glob("*.jpg")):
            if f.stem in ("card-blank", "title-style"):
                continue
            d = diff_region(f, base, reg)
            flag = "ok" if d < 0.02 else ("lệch nhẹ" if d < 0.05 else "LỆCH NHIỀU")
            print(f"  {f.stem:<18} {d:.4f}  {flag}")
        return 0

    src = Path(a.src)
    files = [src] if src.is_file() else sorted(p for p in src.iterdir() if p.suffix.lower() in IMG_EXT)
    out_dir = Path(a.out)
    out_dir.mkdir(exist_ok=True)
    keep = CARDS.parent / "raw" / "precompose"
    keep.mkdir(parents=True, exist_ok=True)

    print(f"Ghép {len(files)} lá lên khung chuẩn {base.name}")
    for f in files:
        slug = f.stem
        dst = out_dir / f"{slug}.jpg"
        if dst.exists() and dst != base:
            shutil.copy2(dst, keep / f"{slug}.jpg")
        kb, q = compose(f, base, dst, panel)
        print(f"  {slug:<18} {kb:6.0f} KB  q{q}")
    print("xong.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
