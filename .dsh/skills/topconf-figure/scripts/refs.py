#!/usr/bin/env python3
"""Query the local top-conference figure pack (no network, no API key).

  python scripts/refs.py --pattern teaser --limit 5
  python scripts/refs.py --theme cv --keyword slam
  python scripts/refs.py --pattern framework --json

Each card is a few lines: enough to choose a reference, cheap enough to keep in
context. Only after picking a card should you open the image itself.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SHARED_PACK = Path(r"C:\Users\17053\Desktop\skills_manager\download\topconf-figure-gallery")
OCEAN_PACK = Path(r"C:\Users\17053\Desktop\skills_manager\download\ocean-figure-refs")
PACK_ALIASES = {"gallery": SHARED_PACK, "ocean": OCEAN_PACK}
FETCH_TOOL = Path(r"C:\Users\17053\Desktop\skills_manager\tools\fetch_gallery_refs.py")
# 本 skill 目录下自带的参照包（可选，装到别的项目后即使读不到共享目录也能用）
LOCAL_PACK = Path(__file__).resolve().parent.parent / "pack"


def default_pack() -> Path:
    for cand in (LOCAL_PACK, SHARED_PACK):
        if (cand / "refs.json").exists():
            return cand
    return SHARED_PACK

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", help="gallery | ocean | <目录/refs.json>（默认自动找本地 pack/ 再找共享画廊）")
    ap.add_argument("--pattern", help="teaser | framework | pipeline | architecture | conceptual | taxonomy")
    ap.add_argument("--theme", help="cv | decision | control | modeling")
    ap.add_argument("--keyword", "-k", help="substring in title (case-insensitive)")
    ap.add_argument("--year", type=int, help="exact year, e.g. 2025")
    ap.add_argument("--tier", action="store_true", help="only oral/spotlight/outstanding")
    ap.add_argument("--limit", "-n", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--need", metavar="TERMS",
                    help="覆盖检查：逗号分隔的主题词（如 underwater,sonar）；有词零命中则 exit 3")
    ap.add_argument("--paths", action="store_true", help="print absolute image paths only")
    a = ap.parse_args()

    if a.pack in PACK_ALIASES:
        root = PACK_ALIASES[a.pack]
    elif a.pack:
        root = Path(a.pack)
    else:
        root = default_pack()
    pack_file = root if root.suffix == ".json" else root / "refs.json"
    if not pack_file.exists():
        print(f"找不到参照包: {pack_file}", file=sys.stderr)
        return 2
    refs = json.loads(pack_file.read_text(encoding="utf-8-sig"))["refs"]

    if a.need:
        terms = [t.strip() for t in a.need.replace("，", ",").split(",") if t.strip()]
        print(f"参照库覆盖检查（{len(refs)} 条）")
        gaps: list[str] = []
        for t in terms:
            tl = t.lower()
            hits = [r for r in refs
                    if tl in r.get("title", "").lower()
                    or tl == (r.get("pattern") or "")
                    or tl == (r.get("theme") or "")]
            if hits:
                print(f"  ✓ {t:<22} {len(hits):>3} 条   例: {', '.join(r['id'] for r in hits[:3])}")
            else:
                print(f"  ✗ {t:<22}   0 条")
                gaps.append(t)
        if gaps:
            print(f"\n⚠ 覆盖不足：{', '.join(gaps)}")
            print("  不要拿相近原型硬套。按 SKILL.md「参照不够用」一节向用户报告，给这三个选项：")
            print(f'  A. 在线补一张：python "{FETCH_TOOL}" --pick <id>')
            print(f'  B. 重抓整包：  python "{FETCH_TOOL}" --refresh')
            print("  C. 先按通用三段式出初稿，标注「需人工确认」")
            return 3
        return 0

    def keep(r: dict) -> bool:
        if a.pattern and r.get("pattern") != a.pattern:
            return False
        if a.theme and r.get("theme") != a.theme:
            return False
        if a.keyword and a.keyword.lower() not in r.get("title", "").lower():
            return False
        if a.year and int(r.get("year", 0)) != a.year:
            return False
        if a.tier and not r.get("tier"):
            return False
        return True

    hits = [r for r in refs if keep(r)]
    hits.sort(key=lambda r: (0 if r.get("tier") else 1, -(r.get("score") or 0)))
    hits = hits[: a.limit]

    if a.paths:
        for r in hits:
            print((root.parent / r["local"] if root.suffix != ".json" else root.parent / r["local"]).resolve())
        return 0
    if a.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return 0

    if not hits:
        print("没有匹配的参照图：放宽 pattern/theme/keyword 再试")
        return 1
    print(f"{len(hits)} refs (from {pack_file.parent.name})")
    for r in hits:
        tag = "★" if r.get("tier") else " "
        print(f"{tag} {r['id']:<26} {r['venue'].upper()}/{r['year']}  {r['pattern']}"
              f"{'/' + r['theme'] if r.get('theme') else ''}  {r['w']}x{r['h']}")
        print(f"    {r['title'][:96]}")
        print(f"    {r['local']}")
    print("\n确认某张合适后再读图：read_image <pack>/<local>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
