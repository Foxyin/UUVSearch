#!/usr/bin/env python3
"""topconf-figure scene engine: check a scene.json and render it to vector PDF/PNG.

  python scripts/scene.py check  scene.json
  python scripts/scene.py render scene.json --out build/fig1 --dpi 200
  python scripts/scene.py tikz   scene.json --out build/fig1.tex

Geometry is millimetres, origin at the top-left corner, y pointing down.
Everything is drawn by TikZ from explicit coordinates: no model touches the
final render, so output is reproducible and editable.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROLES = {
    "data":    {"fill": "DCE8F7", "draw": "5B84B8"},
    "model":   {"fill": "EEF1F4", "draw": "7A828C"},
    "accent":  {"fill": "FBE3CB", "draw": "C8792A"},
    "neutral": {"fill": "FFFFFF", "draw": "9AA0A6"},
    "muted":   {"fill": "F4F6F8", "draw": "C4C9CE"},
}
ARROW_KINDS = {"data": "", "sup": "dashed", "feedback": "dashed"}
MIN_FONT = 6.0
CJK = re.compile(r"[\u3000-\u9fff\uff00-\uffef]")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------- loading

def load(path: Path) -> dict:
    scene = json.loads(path.read_text(encoding="utf-8-sig"))
    scene.setdefault("canvas", {})
    scene["canvas"].setdefault("width", 180)
    scene["canvas"].setdefault("height", 80)
    scene.setdefault("style", {})
    scene["style"].setdefault("font_size", 8.0)
    scene["style"].setdefault("stroke", 0.6)
    scene["style"].setdefault("radius", 1.2)
    scene.setdefault("nodes", [])
    return scene


def text_width_mm(s: str, size_pt: float) -> float:
    """Rough rendered width: CJK ~1em, latin ~0.52em."""
    em = size_pt * 0.3528
    latin = len(s) - len(CJK.findall(s))
    return (len(CJK.findall(s)) * 1.0 + latin * 0.52) * em


# ---------------------------------------------------------------- check

def check(scene: dict) -> tuple[list[str], list[str]]:
    errs: list[str] = []
    warns: list[str] = []
    cw, ch = scene["canvas"]["width"], scene["canvas"]["height"]
    ids: dict[str, dict] = {}

    for i, n in enumerate(scene["nodes"]):
        nid = n.get("id")
        if not nid:
            errs.append(f"node #{i} 缺 id")
            continue
        if nid in ids:
            errs.append(f"重复 id: {nid}")
        ids[nid] = n
        t = n.get("type", "box")
        if t not in {"box", "group", "text", "badge", "arrow", "image"}:
            errs.append(f"{nid}: 未知 type {t!r}")
        if t in {"arrow"}:
            for end in ("from", "to"):
                if n.get(end) and n[end] not in ids and n[end] not in {x.get("id") for x in scene["nodes"]}:
                    errs.append(f"{nid}: {end} 指向不存在的节点 {n[end]!r}")
            for j, vp in enumerate(n.get("via") or []):
                if not (isinstance(vp, (list, tuple)) and len(vp) == 2):
                    errs.append(f"{nid}: via[{j}] 应为 [x, y]")
                    continue
                vx, vy = float(vp[0]), float(vp[1])
                if vx < 0 or vy < 0 or vx > cw or vy > ch:
                    errs.append(f"{nid}: via[{j}] 出画 ({vx},{vy}) (画布 {cw}x{ch})")
            continue
        if "x" not in n or "y" not in n:
            errs.append(f"{nid}: 缺 x/y")
            continue
        x, y = n["x"], n["y"]
        w = n.get("w", 0)
        h = n.get("h", 0)
        if t in {"box", "image"}:
            if w <= 0 or h <= 0:
                errs.append(f"{nid}: 需要正数 w/h")
            left, right = x - w / 2, x + w / 2
            top, bottom = y - h / 2, y + h / 2
        elif t == "group":
            left, right, top, bottom = x, x + w, y, y + h
        else:
            left = right = x
            top = bottom = y
        if left < 0 or top < 0 or right > cw or bottom > ch:
            errs.append(f"{nid}: 出画 {left:.1f},{top:.1f} → {right:.1f},{bottom:.1f} (画布 {cw}x{ch})")
        if t == "image":
            src = n.get("src", "")
            if not src:
                errs.append(f"{nid}: image 缺 src")
            elif not (scene.get("_base", Path(".")) / src).exists() and not Path(src).exists():
                errs.append(f"{nid}: 图片不存在 {src}")
        if t == "box" and n.get("label"):
            size = float(n.get("label_size") or scene["style"]["font_size"])
            need = text_width_mm(n["label"], size)
            if need > w * 0.94:
                warns.append(f"{nid}: 文字宽约 {need:.1f}mm 超过框宽 {w:.1f}mm（会溢出或换行）")
            if size < MIN_FONT:
                warns.append(f"{nid}: 字号 {size}pt < {MIN_FONT}pt，印刷会糊")

    boxes = [n for n in scene["nodes"] if n.get("type", "box") == "box"]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if a.get("group") == b.get("group"):
                continue
            ax0, ax1 = a["x"] - a["w"] / 2, a["x"] + a["w"] / 2
            ay0, ay1 = a["y"] - a["h"] / 2, a["y"] + a["h"] / 2
            bx0, bx1 = b["x"] - b["w"] / 2, b["x"] + b["w"] / 2
            by0, by1 = b["y"] - b["h"] / 2, b["y"] + b["h"] / 2
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > 0.5 and oy > 0.5:
                errs.append(f"{a['id']} 与 {b['id']} 重叠 {ox:.1f}x{oy:.1f}mm")
    return errs, warns


def cmd_check(scene_path: Path) -> int:
    scene = load(scene_path)
    scene["_base"] = scene_path.parent
    errs, warns = check(scene)
    print(f"{scene_path}  canvas {scene['canvas']['width']}x{scene['canvas']['height']}mm  nodes {len(scene['nodes'])}")
    for w in warns:
        print("  warn :", w)
    for e in errs:
        print("  ERROR:", e)
    print("  OK" if not errs else f"  {len(errs)} 个错误")
    return 1 if errs else 0


# ---------------------------------------------------------------- tikz

def esc(s: str) -> str:
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%")
             .replace("$", r"\$").replace("#", r"\#").replace("_", r"\_").replace("{", r"\{")
             .replace("}", r"\}").replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}"))


def render_tikz(scene: dict, scene_dir: Path) -> str:
    st = scene["style"]
    H = scene["canvas"]["height"]
    fs = st["font_size"]
    body: list[str] = []
    images: list[dict] = []

    for n in scene["nodes"]:
        t = n.get("type", "box")
        if t == "arrow":
            continue
        nid = n["id"]
        safe = re.sub(r"[^A-Za-z0-9_]", "_", nid)
        cy = H - n["y"]
        if t == "group":
            x0, y0 = n["x"], H - n["y"] - n["h"]
            x1, y1 = n["x"] + n["w"], H - n["y"]
            body.append(f"\\draw[draw=c_neutral_draw, dashed, rounded corners={st['radius'] * 1.6}mm] "
                        f"({x0:.1f},{y0:.1f}) rectangle ({x1:.1f},{y1:.1f});")
            if n.get("label"):
                body.append(f"\\node[anchor=north west, inner sep=1pt, font=\\sffamily\\footnotesize, text=black!70] "
                            f"at ({x0 + 1.5:.1f},{y1 - 0.8:.1f}) {{{esc(n['label'])}}};")
        elif t == "box":
            role_name = n.get("role", "model") if n.get("role", "model") in ROLES else "model"
            shape = {"round": f"rounded corners={st['radius']}mm", "ellipse": "ellipse",
                     "rect": ""}.get(n.get("shape", "round"), f"rounded corners={st['radius']}mm")
            dash = ", dashed" if n.get("dashed") else ""
            size = float(n.get("label_size") or fs)
            weight = "\\bfseries" if n.get("bold", True) else ""
            body.append(
                f"\\node[{shape}, draw=c_{role_name}_draw, fill=c_{role_name}_fill, line width={st['stroke']}pt, "
                f"minimum width={n['w']:.1f}mm, minimum height={n['h']:.1f}mm, inner sep=1.2mm{dash}] "
                f"({safe}) at ({n['x']:.1f},{cy:.1f}) "
                f"{{\\sffamily{weight}\\fontsize{{{size}}}{{{size * 1.2}}}\\selectfont {esc(n['label'])}}};")
        elif t == "text":
            size = float(n.get("label_size") or fs)
            weight = "\\bfseries" if n.get("bold") else ""
            body.append(f"\\node[anchor=west, inner sep=0pt, font=\\sffamily{weight}\\fontsize{{{size}}}"
                        f"{{{size * 1.2}}}\\selectfont, text={n.get('color', 'black!78')}] "
                        f"({safe}) at ({n['x']:.1f},{cy:.1f}) {{{esc(n['label'])}}};")
        elif t == "badge":
            role_name = n.get("role", "accent") if n.get("role", "accent") in ROLES else "accent"
            body.append(f"\\node[circle, draw=c_{role_name}_draw, fill=c_{role_name}_fill, line width=0.5pt, "
                        f"minimum size=4.6mm, inner sep=0pt, font=\\sffamily\\scriptsize\\bfseries] "
                        f"({safe}) at ({n['x']:.1f},{cy:.1f}) {{{esc(str(n.get('label', '')))}}};")
        elif t == "image":
            images.append(n)

    for n in scene["nodes"]:
        if n.get("type") != "arrow":
            continue
        a = re.sub(r"[^A-Za-z0-9_]", "_", n["from"])
        b = re.sub(r"[^A-Za-z0-9_]", "_", n["to"])
        kind = n.get("kind", "data")
        dash = {"sup": "dashed", "feedback": "dashed", "grad": "dotted"}.get(kind, "solid")
        if n.get("dashed") and dash == "solid":
            dash = "dashed"
        style = f"->, >=Stealth, line width={st.get('arrow_width', 0.7)}pt, {dash}"
        if kind == "feedback":
            path = f"({a}.north) to[out=90, in=90, looseness=1.1] ({b}.north)"
        elif kind == "sup":
            path = f"({a}.south) -- ({b}.south)"
        elif n.get("via"):
            pts = " -- ".join(f"({float(vx):.1f},{H - float(vy):.1f})" for vx, vy in n["via"])
            path = f"({a}) -- {pts} -- ({b})"
        else:
            path = f"({a}) -- ({b})"
        label = n.get("label")
        if label:
            pos = n.get("label_pos", "above")
            shift = {"left": ", xshift=-2.4mm", "right": ", xshift=2.4mm",
                     "below": ", yshift=-1.2mm"}.get(pos, ", yshift=1.2mm")
            lab = (f" node[midway{ ', ' + pos if pos not in {'left', 'right'} else ''}{shift}, "
                   f"font=\\sffamily\\scriptsize, text=black!70] {{{esc(label)}}}")
        else:
            lab = ""
        body.append(f"\\draw[{style}] {path}{lab};")

    imgs = []
    for n in images:
        p = Path(n["src"])
        if not p.is_absolute():
            p = (scene_dir / p).resolve()
        imgs.append(f"\\node at ({n['x']:.1f},{H - n['y']:.1f}) "
                    f"{{\\includegraphics[width={n['w']:.1f}mm,height={n['h']:.1f}mm]{{{p.as_posix()}}}}};")

    cw = scene["canvas"]["width"]
    head = ["\\documentclass[border=3pt]{standalone}",
            "\\usepackage{tikz}", "\\usetikzlibrary{arrows.meta,positioning,shapes.geometric}"]
    labels_all = " ".join(str(n.get("label", "")) for n in scene["nodes"])
    if CJK.search(labels_all):
        head.append("\\usepackage[UTF8,fontset=windows]{ctex}")
    head.append(r"\usepackage{graphicx}")
    head += [f"\\definecolor{{c_{k}_fill}}{{HTML}}{{{v['fill']}}}" for k, v in ROLES.items()]
    head += [f"\\definecolor{{c_{k}_draw}}{{HTML}}{{{v['draw']}}}" for k, v in ROLES.items()]
    head += ["\\begin{document}",
             f"\\begin{{tikzpicture}}[x=1mm,y=1mm,font=\\sffamily]",
             f"\\useasboundingbox (0,0) rectangle ({cw:.1f},{H:.1f});"]
    tail = ["\\end{tikzpicture}", "\\end{document}"]
    return "\n".join(head + body + imgs + tail) + "\n"


def cmd_tikz(scene_path: Path, out: Path) -> int:
    scene = load(scene_path)
    scene["_base"] = scene_path.parent
    errs, warns = check(scene)
    if errs:
        for e in errs:
            print("  ERROR:", e)
        return 1
    tex = render_tikz(scene, scene_path.parent)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tex, encoding="utf-8")
    print(f"{out}  ({len(tex.splitlines())} 行)")
    for w in warns:
        print("  warn :", w)
    return 0


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def cmd_render(scene_path: Path, out_base: Path, dpi: int, keep: bool) -> int:
    scene = load(scene_path)
    scene["_base"] = scene_path.parent
    errs, warns = check(scene)
    if errs:
        for e in errs:
            print("  ERROR:", e)
        print("渲染中止：先修 scene")
        return 1
    for w in warns:
        print("  warn :", w)

    xelatex = shutil.which("xelatex")
    if not xelatex:
        print("找不到 xelatex（需要 TeX Live 或 MiKTeX）")
        return 2

    out_base.parent.mkdir(parents=True, exist_ok=True)
    tex_path = out_base.with_suffix(".tex")
    tex_path.write_text(render_tikz(scene, scene_path.parent), encoding="utf-8")
    code, log = run([xelatex, "-interaction=nonstopmode", "-halt-on-error", tex_path.name], out_base.parent)
    if code != 0:
        tail = "\n".join(log.strip().splitlines()[-25:])
        print("xelatex 失败：\n" + tail)
        return 3

    pdf = out_base.with_suffix(".pdf")
    png = out_base.with_suffix(".png")
    rc, out = run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", pdf.name, out_base.name], out_base.parent)
    if rc != 0:
        print("pdftoppm 失败：", out.strip()[:300])
        return 4
    print(f"PDF {pdf}  ({pdf.stat().st_size / 1024:.0f} KB)")
    if png.exists():
        from PIL import Image
        with Image.open(png) as im:
            print(f"PNG {png}  {im.size[0]}x{im.size[1]}px @ {dpi}dpi")
    if not keep:
        for p in out_base.parent.glob(out_base.stem + ".*"):
            if p.suffix.lower() not in {".pdf", ".png"}:
                p.unlink(missing_ok=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("check")
    p1.add_argument("scene")
    p2 = sub.add_parser("tikz")
    p2.add_argument("scene")
    p2.add_argument("--out", default="build/figure.tex")
    p3 = sub.add_parser("render")
    p3.add_argument("scene")
    p3.add_argument("--out", default="build/figure")
    p3.add_argument("--dpi", type=int, default=200)
    p3.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    if a.cmd == "check":
        return cmd_check(Path(a.scene))
    if a.cmd == "tikz":
        return cmd_tikz(Path(a.scene), Path(a.out))
    return cmd_render(Path(a.scene), Path(a.out), a.dpi, a.keep)


if __name__ == "__main__":
    raise SystemExit(main())
