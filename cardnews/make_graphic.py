#!/usr/bin/env python3
"""
쓸 사진이 없는 회차용. 카드 색상 토큰으로 추상 그래픽을 그린다.

    python3 make_graphic.py dots 1000 290 graphic-dots.png

모티프
  dots  점 격자 + 연결선. 네트워크 · 추적 · 매칭 같은 소재에
"""
import pathlib, subprocess, sys, tempfile
from PIL import Image

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
HERE = pathlib.Path(__file__).parent
BG, PANEL, TRACK = "#F6F3FD", "#FFFFFF", "#E7E1F7"

GRAD = ('<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#4A6CF7"/><stop offset="0.55" stop-color="#B455C4"/>'
        '<stop offset="1" stop-color="#E0568A"/></linearGradient>')

# 강조할 격자 좌표 (열, 행) 과 그 사이를 잇는 선
MARKED = [(2, 1), (5, 3), (8, 0), (10, 2), (6, 4)]
LINKS = [(0, 1), (1, 3), (2, 3), (1, 4)]


def dots(w, h):
    cols, rows = 13, 5
    mx, my = 74, 52
    sx = (w - mx * 2) / (cols - 1)
    sy = (h - my * 2) / (rows - 1)
    at = lambda c, r: (mx + sx * c, my + sy * r)

    p = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
         f'<rect x="16" y="16" width="{w-32}" height="{h-32}" rx="22" fill="{PANEL}"/>',
         f'<defs>{GRAD}</defs>']
    for a, b in LINKS:                       # 연결선을 먼저 깔아 점 아래로
        x1, y1 = at(*MARKED[a]); x2, y2 = at(*MARKED[b])
        p.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                 f'stroke="url(#g)" stroke-width="3" opacity="0.42"/>')
    for r in range(rows):
        for c in range(cols):
            x, y = at(c, r)
            if (c, r) not in MARKED:
                p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{TRACK}"/>')
    for i, (c, r) in enumerate(MARKED):      # 강조 점 + 첫 점에 파동
        x, y = at(c, r)
        if i == 0:
            for rad, op in ((34, 0.10), (24, 0.16)):
                p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad}" fill="url(#g)" opacity="{op}"/>')
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" fill="#FFFFFF"/>')
        p.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="url(#g)"/>')
    return "".join(p)


MOTIFS = {"dots": dots}


def main():
    motif = sys.argv[1] if len(sys.argv) > 1 else "dots"
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 290
    out = HERE / "assets" / (sys.argv[4] if len(sys.argv) > 4 else f"graphic-{motif}.png")
    if motif not in MOTIFS:
        sys.exit(f"모티프 '{motif}' 가 없습니다. 있는 것: {', '.join(MOTIFS)}")
    out.parent.mkdir(exist_ok=True)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}">{MOTIFS[motif](w, h)}</svg>')
    with tempfile.TemporaryDirectory() as td:
        html = pathlib.Path(td) / "g.html"
        html.write_text('<!doctype html><meta charset="utf-8">'
                        '<style>html,body{margin:0;padding:0}svg{display:block}</style>' + svg,
                        encoding="utf-8")
        shot = pathlib.Path(td) / "g.png"
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={w},{h+160}", f"--screenshot={shot}",
                        f"file://{html}"], check=True, capture_output=True)
        Image.open(shot).convert("RGB").crop((0, 0, w, h)).save(out, quality=95)
    print(f"  ✓ {out}  {w}×{h}  ({motif})")


if __name__ == "__main__":
    main()
