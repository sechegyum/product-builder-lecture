#!/usr/bin/env python3
"""
config.json 의 candles -> assets/chart-*.png (사진 슬롯용 일봉 차트)

4번 카드 안의 작은 차트와 별개로, 2·3번 카드 사진 자리에 넣을
큰 일봉 차트를 만든다. 색·둥근모서리는 카드 디자인 토큰을 따른다.

    python3 make_chart.py [폭] [높이] [결과파일]
"""
import json, pathlib, subprocess, sys, tempfile
from PIL import Image

HERE = pathlib.Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
UP, DOWN = "#E0568A", "#5A8FD6"
GRID, BG, PANEL = "#F1EDFA", "#F6F3FD", "#FFFFFF"


def build_svg(candles, w, h):
    pad = 26
    x0, x1 = pad, w - pad
    yt, yb = pad + 6, h - pad - 58          # 가격 영역
    vt, vb = h - pad - 46, h - pad          # 거래량 영역
    lo = min(c[2] for c in candles) * 0.985
    hi = max(c[1] for c in candles) * 1.015
    py = lambda v: yb - (v - lo) / (hi - lo) * (yb - yt)
    step = (x1 - x0) / len(candles)
    bw = step * 0.58

    p = [f'<rect width="{w}" height="{h}" fill="{BG}"/>',
         f'<rect x="{pad-10}" y="{pad-10}" width="{w-2*(pad-10)}" height="{h-2*(pad-10)}" '
         f'rx="22" fill="{PANEL}"/>']
    for f in (0, .33, .66, 1):
        y = py(lo + (hi - lo) * f)
        p.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" '
                 f'stroke="{GRID}" stroke-width="2"/>')
    for i, (o, high, low, cl, v) in enumerate(candles):
        cx = x0 + step * (i + .5)
        col = UP if cl >= o else DOWN
        p.append(f'<line x1="{cx:.1f}" y1="{py(high):.1f}" x2="{cx:.1f}" y2="{py(low):.1f}" '
                 f'stroke="{col}" stroke-width="2"/>')
        t, b = py(max(o, cl)), py(min(o, cl))
        p.append(f'<rect x="{cx-bw/2:.1f}" y="{t:.1f}" width="{bw:.1f}" '
                 f'height="{max(b-t, 2.5):.1f}" rx="2" fill="{col}"/>')
        vh = max(v * (vb - vt), 1.5)
        p.append(f'<rect x="{cx-bw/2:.1f}" y="{vb-vh:.1f}" width="{bw:.1f}" '
                 f'height="{vh:.1f}" rx="2" fill="{col}" opacity="0.32"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{"".join(p)}</svg>')


def main():
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    h = int(sys.argv[2]) if len(sys.argv) > 2 else 340
    out = HERE / "assets" / (sys.argv[3] if len(sys.argv) > 3 else "chart.png")
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    candles = cfg.get("candles")
    if not candles:
        sys.exit("config.json 에 candles 가 없습니다. 실데이터를 먼저 넣으세요.")

    out.parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        html = pathlib.Path(td) / "c.html"
        html.write_text('<!doctype html><meta charset="utf-8">'
                        '<style>html,body{margin:0;padding:0}svg{display:block}</style>'
                        + build_svg(candles, w, h), encoding="utf-8")
        shot = pathlib.Path(td) / "c.png"
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={w},{h+160}", f"--screenshot={shot}",
                        f"file://{html}"], check=True, capture_output=True)
        Image.open(shot).convert("RGB").crop((0, 0, w, h)).save(out, quality=95)
    print(f"  ✓ {out}  {w}×{h}  ({len(candles)}봉)")


if __name__ == "__main__":
    main()
