#!/usr/bin/env python3
"""Build final image prompts for the 78-card Sensual Tarot deck.

Usage (from repo root):
  python3 scripts/build_prompts.py check              # validate cards.json (counts, fields)
  python3 scripts/build_prompts.py prompt wands-08    # print the finished prompt for one card
  python3 scripts/build_prompts.py all                # write prompts/out/<slug>.txt for all 78
  python3 scripts/build_prompts.py md                 # regenerate prompts/01-CARD-TABLE.md
  python3 scripts/build_prompts.py batch wands        # print slugs of one suit (for 10-image batches)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "prompts" / "cards.json"
TEMPLATE = ROOT / "prompts" / "template.md"
OUTDIR = ROOT / "prompts" / "out"
TABLE = ROOT / "prompts" / "01-CARD-TABLE.md"

# rank -> the number of suit objects the classic iconography requires
EXPECTED = {"ace": 1, "02": 2, "03": 3, "04": 4, "05": 5, "06": 6,
            "07": 7, "08": 8, "09": 9, "10": 10,
            "page": 1, "knight": 1, "queen": 1, "king": 1}

FEMME = """FEMALE FIGURE DIRECTIVE (mandatory for every woman in the scene): render her with heightened yet tasteful sensuality — a mature adult woman, confident and entirely at ease in her own skin. Favour: a long bare back with the line of the spine caught by low golden light, bare shoulders with silk or wet gauze slipping off one of them, the curve of waist and hip clearly drawn, a hand lifted into loosened hair, an arched or reclining posture. Give her a languid, alive expression — parted lips, heavy-lidded eyes meeting the viewer or a slow sidelong glance. Drapery is silk or sheer gauze that clings and reveals the body's line rather than hiding it. Nudity is fine-art: bare breasts, back and hips may be shown as soft classical anatomy, painterly and never graphic or clinical.
HARD LIMITS: no explicit sexual acts, no exposed genitals, no spread legs, no hand or object at the genitals, no sexual fluids, no fetish or bondage gear, no minors, no pornographic framing or camera angle."""

NO_COUNT = """COUNT LOCK — not applicable. This card contains no repeated suit objects (no cups, coins, swords or wands). Do not add decorative suit objects, and do not let any object in the scene multiply."""


def count_lock(c):
    if not c.get("count"):
        return NO_COUNT
    n, obj, layout = c["count"]["n"], c["count"]["obj"], c["count"]["layout"]
    nums = " ".join(f"{i}," for i in range(1, n + 1)).rstrip(",")
    return (
        f"COUNT LOCK — EXACTLY {n} {obj} (hard constraint; count before you draw). "
        f"The parchment scene contains exactly {n} {obj} — not {n - 1}, not {n + 1}. "
        f"Placement is locked: {layout}. "
        f"Every one of the {n} must be fully visible: nothing occluded by a body, limb, cloth, cloud or another object, "
        f"nothing fused, broken, cropped by the golden frame, or half-hidden behind a figure. "
        f"Keep them at one consistent size, shape, material and color so they read as a single countable set, "
        f"with a clear gap of background between each one. "
        f"Place no other {obj[:-1] if obj.endswith('s') else obj} anywhere else on the card — not in the frame, "
        f"not in the background, not held by a figure, not as decoration. "
        f"The emblem in the top medallion is a separate heraldic motif and does NOT count toward the {n}. "
        f"Before finishing, count them: {nums}. If the total is not {n}, redraw."
    )


def build(c):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    return (tpl
            .replace("{EMBLEM}", c["emblem"])
            .replace("{SCENE}", c["scene"])
            .replace("{TITLE}", c["title"])
            .replace("{COUNT_LOCK}", count_lock(c))
            .replace("{FEMME}", FEMME if c.get("femme") else "FEMALE FIGURE DIRECTIVE — not applicable to this card."))


def check(cards):
    errs, warns = [], []
    seen = set()
    for c in cards:
        s = c["slug"]
        if s in seen:
            errs.append(f"{s}: duplicate slug")
        seen.add(s)
        for f in ("emblem", "scene", "title"):
            if not c.get(f, "").strip():
                errs.append(f"{s}: empty {f}")
        # forbidden vague quantity words
        for w in ("several", "some ", "a few", "a pile of", "a handful", "various", "many"):
            if w in c["scene"].lower() or w in (c.get("count") or {}).get("layout", "").lower():
                warns.append(f"{s}: vague quantity word '{w.strip()}' — use an exact digit")
        if c["group"] != "major":
            rank = s.split("-")[-1]
            exp = EXPECTED.get(rank)
            n = (c.get("count") or {}).get("n")
            if exp is None:
                errs.append(f"{s}: unknown rank '{rank}'")
            elif n != exp:
                errs.append(f"{s}: count.n={n} but iconography requires {exp}")
            # the number must literally appear in the layout text, as a digit or a word
            words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                     6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
            lay = (c.get("count") or {}).get("layout", "").lower()
            if exp and str(exp) not in lay and words.get(exp, "@") not in lay:
                warns.append(f"{s}: layout text never states the number '{exp}' as digit or word")
    if len(cards) != 78:
        errs.append(f"deck has {len(cards)} cards, expected 78")
    for w in warns:
        print(f"WARN  {w}")
    for e in errs:
        print(f"ERROR {e}")
    print(f"\n{len(cards)} cards, {len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


def md_table(cards):
    out = ["# Bảng 78 lá — EMBLEM · COUNT LOCK · SCENE · TITLE",
           "",
           "Sinh tự động từ `prompts/cards.json` bằng `python3 scripts/build_prompts.py md`.",
           "Cột **COUNT LOCK** là phần sửa lỗi AI đếm sai số lượng cốc / xu / kiếm / gậy.",
           ""]
    groups = [("major", "MAJOR ARCANA — 22 lá"), ("wands", "WANDS — 14 lá"),
              ("cups", "CUPS — 14 lá"), ("swords", "SWORDS — 14 lá"),
              ("pentacles", "PENTACLES — 14 lá")]
    for g, head in groups:
        out += [f"## {head}", ""]
        rows = [c for c in cards if c["group"] == g]
        if g == "major":
            out += ["| # | Slug | Emblem | Scene | Title |", "|---|------|--------|-------|-------|"]
            for c in rows:
                extra = ""
                if c.get("count"):
                    extra = f" **[COUNT: {c['count']['n']} {c['count']['obj']} — {c['count']['layout']}]**"
                out.append(f"| {c['n']} | {c['slug']} | {c['emblem']} | {c['scene']}.{extra} | {c['title']} |")
        else:
            out += ["| Slug | Emblem | Count lock (cứng) | Scene | Title |", "|------|--------|-------------------|-------|-------|"]
            for c in rows:
                out.append(f"| {c['slug']} | {c['emblem']} | **{c['count']['n']} {c['count']['obj']}** — {c['count']['layout']} | {c['scene']} | {c['title']} |")
        out += [""]
    return "\n".join(out) + "\n"


def main():
    cards = json.loads(DATA.read_text(encoding="utf-8"))["cards"]
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        return check(cards)
    if cmd == "prompt":
        slug = sys.argv[2]
        c = next((x for x in cards if x["slug"] == slug), None)
        if not c:
            print(f"no card '{slug}'")
            return 1
        print(build(c))
        return 0
    if cmd == "all":
        OUTDIR.mkdir(parents=True, exist_ok=True)
        for c in cards:
            (OUTDIR / f"{c['slug']}.txt").write_text(build(c), encoding="utf-8")
        print(f"wrote {len(cards)} prompts to {OUTDIR.relative_to(ROOT)}/")
        return 0
    if cmd == "md":
        TABLE.write_text(md_table(cards), encoding="utf-8")
        print(f"wrote {TABLE.relative_to(ROOT)}")
        return 0
    if cmd == "batch":
        g = sys.argv[2]
        print(", ".join(c["slug"] for c in cards if c["group"] == g))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
