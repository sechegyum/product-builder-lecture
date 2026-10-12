#!/usr/bin/env python3
"""
out/*.svg -> svg-canva/*.svg  (텍스트를 패스로 변환)

Canva 에는 Pretendard 가 없어서 SVG 를 그대로 올리면 폰트가 치환되고
글자 폭이 달라져 레이아웃이 밀린다. 글자를 패스로 바꿔두면 어디서 열어도
보이는 그대로다. 대신 텍스트 편집은 안 된다.

    python3 svg_outline.py [입력폴더] [출력폴더]
"""
import pathlib, re, sys, xml.etree.ElementTree as ET
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
FONT_DIR = pathlib.Path.home() / ".fonts"
WEIGHTS = {300: "Light", 400: "Regular", 500: "Medium", 600: "SemiBold",
           700: "Bold", 800: "ExtraBold", 900: "Black"}
# Pretendard 에 없는 글자(✦ 등)를 받아줄 대체 폰트. 브라우저 폴백과 같은 순서다.
FALLBACK = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
_cache = {}


def _load(path):
    if path not in _cache:
        _cache[path] = TTFont(path)
    return _cache[path]


def font(weight):
    w = min(WEIGHTS, key=lambda k: abs(k - weight))
    return _load(str(FONT_DIR / f"Pretendard-{WEIGHTS[w]}.otf"))


def pick(weight, ch):
    """그 글자를 가진 폰트를 고른다. 없으면 대체 폰트로 넘어간다"""
    f = font(weight)
    if ord(ch) in f.getBestCmap():
        return f
    for path in FALLBACK:
        g = _load(path)
        if ord(ch) in g.getBestCmap():
            return g
    return f


def glyph_path(f, ch):
    """한 글자의 path d 와 advance 를 폰트 단위로 돌려준다"""
    name = f.getBestCmap().get(ord(ch))
    if name is None:
        return "", f["hmtx"]["space"][0] if "space" in f.getGlyphOrder() else 0
    pen = SVGPathPen(f.getGlyphSet())
    f.getGlyphSet()[name].draw(pen)
    return pen.getCommands(), f["hmtx"][name][0]


def runs_of(el, inherited):
    """<text> 아래 텍스트와 <tspan> 을 (문자열, 속성) 목록으로 편다"""
    out = []
    attrs = {**inherited, **{k: v for k, v in el.attrib.items()}}
    if el.text:
        out.append((el.text, attrs))
    for child in el:
        if child.tag == f"{{{SVG}}}tspan":
            out += runs_of(child, attrs)
        if child.tail:
            out.append((child.tail, attrs))
    return out


def outline(el, inherited):
    attrs = {**inherited, **el.attrib}
    size = float(attrs.get("font-size", 16))
    ls = float(attrs.get("letter-spacing", 0))
    anchor = attrs.get("text-anchor", "start")
    x0, y0 = float(attrs.get("x", 0)), float(attrs.get("y", 0))

    runs = runs_of(el, inherited)
    total = 0.0
    for text, a in runs:
        wt = int(float(a.get("font-weight", 400)))
        for ch in text:
            f = pick(wt, ch)
            total += glyph_path(f, ch)[1] * size / f["head"].unitsPerEm + ls

    x = {"start": x0, "middle": x0 - total / 2, "end": x0 - total}[anchor]

    g = ET.Element(f"{{{SVG}}}g")
    for text, a in runs:
        wt = int(float(a.get("font-weight", 400)))
        fill = a.get("fill", "#000000")
        for ch in text:
            f = pick(wt, ch)
            s = size / f["head"].unitsPerEm
            d, adv = glyph_path(f, ch)
            if d.strip():
                p = ET.SubElement(g, f"{{{SVG}}}path")
                p.set("d", d)
                p.set("fill", fill)
                p.set("transform", f"translate({x:.2f} {y0:.2f}) scale({s:.6f} {-s:.6f})")
            x += adv * s + ls
    return g


def walk(parent, inherited):
    for i, el in enumerate(list(parent)):
        attrs = {**inherited, **el.attrib}
        if el.tag == f"{{{SVG}}}text":
            parent[i] = outline(el, inherited)
        else:
            walk(el, attrs)


def main():
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "out")
    dst = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "svg-canva")
    dst.mkdir(exist_ok=True)
    for f in sorted(src.glob("*.svg")):
        tree = ET.parse(f)
        walk(tree.getroot(), {})
        out = dst / f.name
        tree.write(out, encoding="utf-8", xml_declaration=True)
        print(f"  ✓ {out}")


if __name__ == "__main__":
    main()
