#!/usr/bin/env python3
"""
쓸 사진이 없는 회차용. 카드 색상 토큰으로 추상 그래픽을 그린다.

    python3 make_graphic.py dots 1000 290 graphic-dots.png

모티프
  dots     점 격자 + 연결선. 네트워크 · 추적 · 매칭 같은 소재에
  circuit  어두운 기판 + 배선 + 칩. 반도체 · AI 글의 사진 자리에
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


# ── circuit — 어두운 기판 ────────────────────────────
# 반도체 글에 쓸 사진이 없을 때. 스톡 사진을 찾느니 그리는 게 낫다 —
# 해상도를 원하는 만큼 뽑을 수 있고, AI 사진처럼 칩에 깨진 글자가 안 박힌다.
#
# 매크로 렌즈 흉내를 세 겹으로 낸다. 멀리 흐린 층 · 중간 층 · 선명한 층.
# 한 겹으로 그리면 벽지처럼 평평해져서 글자를 올려도 깊이가 안 산다.
DARK = ("#0A1A26", "#061016")          # 기판 바탕
TRACE = ("#174453", "#1E5A6B", "#246F82")
LIVE = ("#36C9E0", "#4A6CF7", "#B455C4")   # 살아 있는 배선 — 브랜드 색을 섞는다


def _trace(rnd, x, y, w, h, step):
    """45도로만 꺾는 배선 한 줄. 기판 배선은 직각과 45도만 쓴다."""
    d, n = [f"M{x:.0f} {y:.0f}"], rnd.randint(3, 7)
    dx, dy = rnd.choice([(1, 0), (0, 1), (1, 1), (1, -1)])
    for _ in range(n):
        L = step * rnd.randint(1, 4)
        x, y = x + dx * L, y + dy * L
        if not (-80 < x < w + 80 and -80 < y < h + 80):
            break
        d.append(f"L{x:.0f} {y:.0f}")
        dx, dy = rnd.choice([(dx, dy), (dy, dx), (-dy, dx), (dx and 0 or 1, dy and 0 or 1)])
    return " ".join(d) if len(d) > 2 else ""


def _bundle(rnd, w, h, step, n=4):
    """나란히 붙어 가는 배선 다발. 실제 기판은 선이 혼자 다니지 않는다."""
    x, y = rnd.uniform(-w * 0.1, w), rnd.uniform(-h * 0.1, h)
    dx, dy = rnd.choice([(1, 1), (1, -1), (1, 0), (0, 1)])
    g = step * 0.22
    out = []
    for i in range(n):
        ox, oy = (-dy * g * i, dx * g * i)
        d = _trace(rnd, x + ox, y + oy, w, h, step * 1.6)
        if d:
            out.append(f'<path d="{d}" fill="none" stroke="{rnd.choice(TRACE)}" '
                       f'stroke-width="{rnd.uniform(2, 3.2):.1f}" opacity="0.8"/>')
    return "".join(out)


def _pads(rnd, w, h, k, r, col, op):
    return "".join(
        f'<circle cx="{rnd.uniform(0, w):.0f}" cy="{rnd.uniform(0, h):.0f}" '
        f'r="{r}" fill="none" stroke="{col}" stroke-width="{max(2, r//3)}" opacity="{op}"/>'
        for _ in range(k))


def _chip(x, y, s, rnd):
    """칩 패키지 하나. 글자는 넣지 않는다 — 가짜 글자가 제일 티 난다."""
    pin, gap = s * 0.055, s * 0.105
    p = [f'<rect x="{x-s/2:.0f}" y="{y-s/2:.0f}" width="{s:.0f}" height="{s:.0f}" rx="{s*0.045:.0f}" '
         f'fill="#0C2C38" stroke="#2E7C8E" stroke-width="3"/>']
    n = int(s / gap) - 1
    off = (s - (n - 1) * gap) / 2
    for i in range(n):                      # 네 변에 핀
        a = x - s / 2 + off + i * gap
        for px, py, pw, ph in ((a, y - s / 2 - pin, pin * 0.62, pin),
                               (a, y + s / 2, pin * 0.62, pin),
                               (x - s / 2 - pin, a, pin, pin * 0.62),
                               (x + s / 2, a, pin, pin * 0.62)):
            p.append(f'<rect x="{px:.0f}" y="{py:.0f}" width="{pw:.0f}" height="{ph:.0f}" '
                     f'rx="2" fill="#53A3B5" opacity="0.85"/>')
    dx0, dw = x - s * 0.3, s * 0.6
    p.append(f'<rect x="{dx0:.0f}" y="{y-s*0.3:.0f}" width="{dw:.0f}" height="{dw:.0f}" '
             f'rx="{s*0.03:.0f}" fill="url(#die)" opacity="0.34"/>')
    for i in range(1, 6):                   # 다이 위 격자. 민짜로 두면 그림처럼 보인다
        q = dx0 + dw * i / 6
        p.append(f'<line x1="{q:.0f}" y1="{y-s*0.3:.0f}" x2="{q:.0f}" y2="{y+s*0.3:.0f}" '
                 f'stroke="#9BD7E4" stroke-width="1" opacity="0.14"/>')
        q = y - s * 0.3 + dw * i / 6
        p.append(f'<line x1="{dx0:.0f}" y1="{q:.0f}" x2="{dx0+dw:.0f}" y2="{q:.0f}" '
                 f'stroke="#9BD7E4" stroke-width="1" opacity="0.14"/>')
    p.append(f'<rect x="{x-s/2:.0f}" y="{y-s/2:.0f}" width="{s:.0f}" height="{s*0.16:.0f}" '
             f'rx="{s*0.045:.0f}" fill="#FFFFFF" opacity="0.06"/>')   # 윗면 반사
    return "".join(p)


def circuit(w, h):
    import random
    rnd = random.Random(11)                 # 고정 씨앗 — 같은 그림이 다시 나와야 한다
    step = max(w, h) / 26

    d = [f'<defs>',
         f'<linearGradient id="bg" x1="0" y1="0" x2="0.7" y2="1">'
         f'<stop offset="0" stop-color="{DARK[0]}"/><stop offset="1" stop-color="{DARK[1]}"/></linearGradient>',
         '<linearGradient id="die" x1="0" y1="0" x2="1" y2="1">'
         '<stop offset="0" stop-color="#4A6CF7"/><stop offset="1" stop-color="#B455C4"/></linearGradient>',
         '<radialGradient id="gl1" cx="0.5" cy="0.5" r="0.5">'
         '<stop offset="0" stop-color="#36C9E0" stop-opacity="0.30"/>'
         '<stop offset="1" stop-color="#36C9E0" stop-opacity="0"/></radialGradient>',
         '<radialGradient id="gl2" cx="0.5" cy="0.5" r="0.5">'
         '<stop offset="0" stop-color="#B455C4" stop-opacity="0.26"/>'
         '<stop offset="1" stop-color="#B455C4" stop-opacity="0"/></radialGradient>',
         '<radialGradient id="vig" cx="0.5" cy="0.5" r="0.72">'
         '<stop offset="0.45" stop-color="#000000" stop-opacity="0"/>'
         '<stop offset="1" stop-color="#000000" stop-opacity="0.55"/></radialGradient>',
         f'<filter id="far"><feGaussianBlur stdDeviation="{max(w,h)/95:.1f}"/></filter>',
         f'<filter id="mid"><feGaussianBlur stdDeviation="{max(w,h)/320:.1f}"/></filter>',
         '</defs>',
         f'<rect width="{w}" height="{h}" fill="url(#bg)"/>',
         f'<rect x="{w*0.30:.0f}" y="{-h*0.22:.0f}" width="{w*0.95:.0f}" height="{w*0.95:.0f}" fill="url(#gl1)"/>',
         f'<rect x="{-w*0.25:.0f}" y="{h*0.42:.0f}" width="{w*0.9:.0f}" height="{w*0.9:.0f}" fill="url(#gl2)"/>']

    # 1) 먼 층 — 흐리게. 보케처럼 둥근 빛도 몇 개 섞는다
    far = []
    for _ in range(26):
        p = _trace(rnd, rnd.uniform(0, w), rnd.uniform(0, h), w, h, step * 1.4)
        if p:
            far.append(f'<path d="{p}" fill="none" stroke="{rnd.choice(TRACE)}" '
                       f'stroke-width="{rnd.uniform(5, 11):.1f}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    for _ in range(9):
        far.append(f'<circle cx="{rnd.uniform(0, w):.0f}" cy="{rnd.uniform(0, h):.0f}" '
                   f'r="{rnd.uniform(14, 34):.0f}" fill="{rnd.choice(LIVE)}" '
                   f'opacity="{rnd.uniform(0.10, 0.22):.2f}"/>')
    d.append(f'<g filter="url(#far)">{"".join(far)}</g>')

    # 2) 중간 층 — 살짝만 흐리게
    mid = [_pads(rnd, w, h, 22, int(step * 0.30), "#235E6E", "0.5")]
    for _ in range(6):
        mid.append(_bundle(rnd, w, h, step))
    for _ in range(26):
        p = _trace(rnd, rnd.uniform(0, w), rnd.uniform(0, h), w, h, step)
        if p:
            mid.append(f'<path d="{p}" fill="none" stroke="{rnd.choice(TRACE)}" '
                       f'stroke-width="{rnd.uniform(2.5, 5):.1f}" opacity="{rnd.uniform(0.55, 0.9):.2f}"/>')
    d.append(f'<g filter="url(#mid)">{"".join(mid)}</g>')

    # 3) 선명한 층 — 칩과 그 둘레. 눈이 멈추는 자리다
    cx, cy, cs = w * 0.64, h * 0.62, max(w, h) * 0.19
    sharp = []
    for _ in range(14):                     # 칩에서 뻗어 나가는 배선
        a = rnd.uniform(0, 6.283)
        import math
        sx, sy = cx + math.cos(a) * cs * 0.62, cy + math.sin(a) * cs * 0.62
        p = _trace(rnd, sx, sy, w, h, step * 0.9)
        if p:
            live = rnd.random() < 0.3
            sharp.append(f'<path d="{p}" fill="none" '
                         f'stroke="{rnd.choice(LIVE) if live else rnd.choice(TRACE)}" '
                         f'stroke-width="{rnd.uniform(2, 3.6):.1f}" '
                         f'opacity="{0.75 if live else 0.95:.2f}"/>')
    sharp.append(_pads(rnd, w, h, 14, int(step * 0.22), "#2E7C8E", "0.8"))
    for _ in range(16):                     # SMD 부품
        bx, by = rnd.uniform(0, w), rnd.uniform(0, h)
        bw, bh = step * rnd.uniform(0.5, 1.1), step * rnd.uniform(0.28, 0.5)
        sharp.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{bw:.0f}" height="{bh:.0f}" rx="3" '
                     f'fill="#123540" stroke="#2E7C8E" stroke-width="2" opacity="0.9"/>')
    sharp.append(_chip(cx, cy, cs, rnd))
    sharp.append(_chip(w * 0.20, h * 0.30, cs * 0.52, rnd))
    sharp.append(_chip(w * 0.88, h * 0.16, cs * 0.38, rnd))
    d.append("".join(sharp))

    # 기판 층 전체를 살짝 기울인다. 정면으로 두면 벽지가 되고, 기울이면 사진이 된다.
    # 모서리가 비지 않게 키워서 돌린다.
    body = "".join(d[14:])
    head = "".join(d[:14])
    return (head + f'<g transform="translate({w/2:.0f},{h/2:.0f}) scale(1.24) rotate(-9) '
            f'translate({-w/2:.0f},{-h/2:.0f})">{body}</g>'
            + f'<rect width="{w}" height="{h}" fill="url(#vig)"/>')


MOTIFS = {"dots": dots, "circuit": circuit}


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
