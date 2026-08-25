#!/usr/bin/env python3
"""
배경 시안 비교용. 표지 카드를 배경만 바꿔 여러 장 뽑는다.

    python3 bg_variants.py config.json bg-out

generate.py 는 건드리지 않는다. DEFS 만 갈아끼워 card1() 을 다시 부른다.
고른 안이 생기면 그 조각을 generate.py 의 DEFS 에 옮기면 된다.
"""
import json, pathlib, sys
import generate as G

BASE = '''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1">
    <stop offset="0" stop-color="#FBF9FF"/><stop offset="1" stop-color="#EFEAFC"/>
  </linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#4A6CF7"/><stop offset="0.5" stop-color="#B455C4"/><stop offset="1" stop-color="#E0568A"/>
  </linearGradient>
  <linearGradient id="dom" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#4A6CF7"/><stop offset="0.55" stop-color="#B455C4"/><stop offset="1" stop-color="#E0568A"/>
  </linearGradient>
{extra}</defs>
<rect width="1080" height="1080" fill="url(#bg)"/>
{layer}'''

VARIANTS = {
    # 0. 지금 쓰는 것 — 비교 기준
    "0-현재-원": ("", '<circle cx="920" cy="180" r="200" fill="#B455C4" opacity="0.06"/>'),

    # 1. 아무것도 없이 그라데이션만
    "1-없음": ("", ""),

    # 2. 미세한 그레인. 종이 질감처럼 깔린다
    "2-그레인": ('''  <filter id="gr" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="3" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
''', '<rect width="1080" height="1080" filter="url(#gr)" opacity="0.055"/>'),

    # 3. 테두리 없는 빛번짐. 지금 원에서 '선명한 경계'만 뺀 것
    "3-소프트글로우": ('''  <radialGradient id="gl" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#B455C4" stop-opacity="0.16"/>
    <stop offset="0.55" stop-color="#B455C4" stop-opacity="0.05"/>
    <stop offset="1" stop-color="#B455C4" stop-opacity="0"/>
  </radialGradient>
''', '<rect x="480" y="-260" width="880" height="880" fill="url(#gl)"/>'),

    # 4. 아주 옅은 격자. 데이터 화면 느낌
    "4-그리드": ('''  <pattern id="gd" width="72" height="72" patternUnits="userSpaceOnUse">
    <path d="M72 0 L0 0 0 72" fill="none" stroke="#B455C4" stroke-width="1" opacity="0.09"/>
  </pattern>
''', '<rect width="1080" height="1080" fill="url(#gd)"/>'),

    # 5. 색이 두 군데서 번지는 메쉬
    "5-메쉬": ('''  <radialGradient id="m1" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#4A6CF7" stop-opacity="0.13"/><stop offset="1" stop-color="#4A6CF7" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="m2" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#E0568A" stop-opacity="0.13"/><stop offset="1" stop-color="#E0568A" stop-opacity="0"/>
  </radialGradient>
''', '<rect x="-200" y="-160" width="900" height="900" fill="url(#m1)"/>'
     '<rect x="440" y="500" width="940" height="940" fill="url(#m2)"/>'),

    # 6. 우상단 동심원 호. 선으로만
    "6-코너아크": ("", "".join(
        f'<circle cx="1080" cy="0" r="{r}" fill="none" stroke="#B455C4" '
        f'stroke-width="2" opacity="0.10"/>' for r in (300, 420, 540, 660))),

    # 7. 하단에서 올라오는 옅은 색면
    "8-하단밴드": ('''  <linearGradient id="bd" x1="0" y1="1" x2="0.3" y2="0">
    <stop offset="0" stop-color="#B455C4" stop-opacity="0.13"/>
    <stop offset="1" stop-color="#B455C4" stop-opacity="0"/>
  </linearGradient>
''', '<rect y="540" width="1080" height="540" fill="url(#bd)"/>'),
}


def main():
    cfg = json.loads(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "config.json")
                     .read_text(encoding="utf-8"))
    out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "bg-out")
    out.mkdir(exist_ok=True)
    original = G.DEFS
    for name, (extra, layer) in VARIANTS.items():
        G.DEFS = BASE.format(extra=extra, layer=layer)
        (out / f"{name}.svg").write_text(G.card1(cfg, "end"), encoding="utf-8")
        print(f"  ✓ {out}/{name}.svg")
    G.DEFS = original


if __name__ == "__main__":
    main()
