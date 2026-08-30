#!/usr/bin/env python3
"""Quét cards/ và sinh deck.json cho gallery.

  python3 scripts/build_gallery.py
"""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
DATA = ROOT / "prompts" / "cards.json"
OUT = ROOT / "deck.json"
GROUPS = {"major": "Major Arcana", "wands": "Wands", "cups": "Cups",
          "swords": "Swords", "pentacles": "Pentacles"}


def dims(p):
    if shutil.which("identify"):
        r = subprocess.run(["identify", "-format", "%w %h", str(p)],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            w, h = r.stdout.split()
            return int(w), int(h)
    return None, None


def main():
    cards = json.loads(DATA.read_text(encoding="utf-8"))["cards"]
    out = []
    done = 0
    for c in cards:
        f = None
        for ext in (".jpg", ".png", ".webp"):
            p = CARDS / f"{c['slug']}{ext}"
            if p.exists():
                f = p
                break
        item = {"slug": c["slug"], "n": c["n"], "group": c["group"],
                "groupLabel": GROUPS[c["group"]], "emblem": c["emblem"],
                "title": c["title"], "scene": c["scene"],
                "femme": bool(c.get("femme")), "file": None}
        if f:
            w, h = dims(f)
            item["file"] = f.relative_to(ROOT).as_posix()
            item["w"], item["h"] = w, h
            item["kb"] = round(f.stat().st_size / 1024)
            done += 1
        out.append(item)
    payload = {"deck": "Sensual Tarot", "total": len(out), "done": done,
               "size": "848x1264", "cards": out}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {done}/{len(out)} lá đã có ảnh")


if __name__ == "__main__":
    main()
