#!/usr/bin/env python3
"""Đo "đường nối": vùng trong hộp tên (phần dán từ lá nguồn) so với khung chuẩn.

Sau khi ghép, phần dải dưới NẰM NGOÀI hộp tên lấy từ khung chuẩn nên khớp tuyệt đối;
phần TRONG hộp tên lấy từ lá nguồn. Nếu dải của lá nguồn khác khung chuẩn (khác màu hay
khác hoạ tiết) sẽ lộ một hình chữ nhật mờ. Script này đo chính điều đó.

  python3 scripts/check_seam.py              # đo tất cả lá trong cards/
  python3 scripts/check_seam.py 12-hanged    # một lá

Ngưỡng (RMSE so với khung chuẩn, cùng toạ độ):
  < 0.06  mịn      - không thấy
  0.06-0.10 hơi thấy
  > 0.10  RÕ       - nên tạo lại lá đó
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_card import CARDS, load_panel, ref  # noqa: E402

BASE = ref("frame-master.jpg")
# vùng TRONG hộp tên nhưng TRÁNH chữ (chữ nằm khoảng x200..660, y1100..1235)
PROBES = {
    "trái": lambda tx: (tx + 3, 1090, 24, 150),
    "phải": lambda tx: (tx + TW - 27, 1090, 24, 150),
    "trên": lambda tx: (tx + 125, 1082, 250, 10),
}


def rmse(a, b, reg):
    x, y, w, h = reg
    t = Path("/tmp/_seam")
    t.mkdir(exist_ok=True)
    for n, f in (("a", a), ("b", b)):
        subprocess.run(["convert", str(f), "-crop", f"{w}x{h}+{x}+{y}", "+repage",
                        str(t / f"{n}.png")], capture_output=True)
    r = subprocess.run(["convert", str(t / "a.png"), str(t / "b.png"), "-metric", "RMSE",
                        "-compare", "-format", "%[distortion]", "info:"],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip().split()[0])
    except Exception:
        return -1


def main():
    panel = load_panel()
    global TW
    tx, ty, TW, th = panel["title"]
    args = sys.argv[1:]
    files = ([CARDS / f"{a}.jpg" for a in args] if args
             else sorted(f for f in CARDS.glob("*.jpg")
                         if f.stem not in ("card-blank", "title-style")))
    print(f"{'lá':<16}" + "".join(f"{k:>10}" for k in PROBES) + "   đánh giá")
    print("-" * 62)
    bad = []
    for f in files:
        vals = {k: rmse(f, BASE, fn(tx)) for k, fn in PROBES.items()}
        m = max(vals.values())
        tag = "mịn" if m < 0.06 else ("hơi thấy" if m < 0.10 else "RÕ")
        if m >= 0.10:
            bad.append((f.stem, m))
        print(f"{f.stem:<16}" + "".join(f"{v:10.4f}" for v in vals.values()) + f"   {tag}")
    print("-" * 62)
    if bad:
        print("nên tạo lại: " + ", ".join(f"{n} ({v:.3f})" for n, v in bad))
    else:
        print("tất cả đều mịn.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
