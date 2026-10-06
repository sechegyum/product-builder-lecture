#!/usr/bin/env python3
"""
블로그 썸네일 · 포스터 생성기

generate.py 는 건드리지 않는다. 디자인 토큰(색·폰트·그라데이션)만 가져다 쓰고
레이아웃은 여기서 따로 짠다. 카드뉴스와 블로그는 읽히는 크기가 달라서다.

  · 인스타 카드  손가락 한 뼘        -> 88px 글자, 한 줄 10자까지 읽힌다
  · 블로그 썸네일 검색 결과의 작은 칸 -> 글자를 키우고 한 줄 6~9자로 줄여야 한다

레이아웃 넷을 돌려 쓴다. 같은 색 · 다른 뼈대 -> "다양한데 같은 블로그" 가 된다.

  num   숫자 하나를 화면 절반에          예) -99.26% / 5개월 만에 사라진 시가총액
  vs    두 값을 화살표로 마주 세운다     예) +20% -> -30%
  ask   질문 두세 줄                     예) 지수는 올랐는데 / 나는 왜 잃을까
  list  제목 + 항목 셋                   예) 급등 직후 증자 / 세 건

크기는 두 벌이 같이 나온다.
  1080x1080  정사각 — 네이버 대표이미지 · 인스타
  1200x630   가로  — 오픈그래프 · 카카오/페북 공유 카드
가로판도 글자는 가운데 정사각 안에 둔다. 어디서 잘려도 살아남게.

    python3 thumb.py thumbs.json [출력폴더]
"""
import json, pathlib, subprocess, sys

from generate import INK, SUB, FAINT, DIM, ACCENT, PURPLE, UP, DOWN, LAV, FONT, esc

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
HERE = pathlib.Path(__file__).parent
SIZES = {"sq": (1080, 1080), "wide": (1200, 630)}


def defs(w, h):
    """generate.py 의 DEFS 는 1080 고정이라 크기를 받게 다시 쓴다. 색은 그대로."""
    return f'''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1">
    <stop offset="0" stop-color="#FBF9FF"/><stop offset="1" stop-color="#EFEAFC"/>
  </linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#4A6CF7"/><stop offset="0.5" stop-color="#B455C4"/><stop offset="1" stop-color="#E0568A"/>
  </linearGradient>
  <radialGradient id="m1" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#4A6CF7" stop-opacity="0.13"/><stop offset="1" stop-color="#4A6CF7" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="m2" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#E0568A" stop-opacity="0.13"/><stop offset="1" stop-color="#E0568A" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<rect x="{-w*0.19:.0f}" y="{-h*0.15:.0f}" width="{w*0.84:.0f}" height="{w*0.84:.0f}" fill="url(#m1)"/>
<rect x="{w*0.41:.0f}" y="{h*0.46:.0f}" width="{w*0.87:.0f}" height="{w*0.87:.0f}" fill="url(#m2)"/>'''


def foot(w, h, note, dark=False, dom_x=None, cta=None):
    """좌하단 한 줄 + 우하단 도메인. 카드뉴스의 '밀어서 보기' 같은 인스타 장치는 뺀다."""
    y = h - 52
    s = ""
    if note:
        s += (f'  <text x="{w*0.074:.0f}" y="{y}" font-size="{int(h*0.026)}" font-weight="600" '
              f'letter-spacing="-0.3" fill="{"#A9A0C8" if dark else DIM}">{esc(note)}</text>\n')
    s += (f'  <text x="{(dom_x if dom_x else w - w*0.074):.0f}" y="{y}" text-anchor="end" font-size="{int(h*0.028)}" '
          f'font-weight="700" letter-spacing="-0.5" fill="{"#FFFFFF" if dark else "url(#line)"}">{esc(cta or "snapvestai.com")}</text>')
    return s


def bar(x, y, w, h=13):
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h}" rx="{h//2}" fill="url(#line)"/>'


def tag(x, y, text, size):
    """좌상단 분류 꼬리표. 포맷이 달라도 같은 블로그로 읽히게 하는 장치."""
    return (f'  <text x="{x:.0f}" y="{y:.0f}" font-size="{size}" font-weight="700" '
            f'letter-spacing="2.5" fill="{PURPLE}">{esc(text)}</text>')


# ── num — 숫자 하나 ─────────────────────────────────
def lay_num(c, w, h):
    big = c["big"]
    col = {"up": UP, "down": DOWN, "accent": ACCENT}.get(c.get("tone", "accent"), ACCENT)
    fs = int(h * (0.235 if len(big) <= 7 else 0.185))
    x = w * 0.074
    if (w, h) == (1080, 1080):
        ty, by, sy = 300, 560, 700
    else:
        ty, by, sy = 190, 370, 470
    s = tag(x, ty - 130, c.get("tag", "SNAPVEST"), int(h * 0.026)) + "\n"
    s += (f'  <text x="{x:.0f}" y="{by}" font-size="{fs}" font-weight="700" '
          f'letter-spacing="-6" fill="{col}">{esc(big)}</text>\n')
    s += "  " + bar(x, by + int(h * 0.035), w * 0.22) + "\n"
    for i, t in enumerate(c["lines"][:2]):
        s += (f'  <text x="{x:.0f}" y="{sy + i * int(h*0.072)}" font-size="{int(h*0.052)}" '
              f'font-weight="700" letter-spacing="-2" fill="{INK}">{esc(t)}</text>\n')
    return s


# ── vs — 두 값 대비 ─────────────────────────────────
def lay_vs(c, w, h):
    """위아래로 두 값을 세우고 사이에 화살표. 숫자가 커서 자리를 넉넉히 준다."""
    a, b = c["left"], c["right"]
    fs = int(h * 0.145)
    x = w * 0.074
    if (w, h) == (1080, 1080):
        tag_y, ay, lny, arw, by, rny, bry, capy = 170, 430, 492, 578, 730, 792, 852, 912
    else:
        tag_y, ay, lny, arw, by, rny, bry, capy = 95, 235, 278, 330, 420, 463, None, 512
    s = tag(x, tag_y, c.get("tag", "SNAPVEST"), int(h * 0.026)) + "\n"
    s += (f'  <text x="{x:.0f}" y="{ay}" font-size="{fs}" font-weight="700" '
          f'letter-spacing="-5" fill="{UP}">{esc(a)}</text>\n')
    s += (f'  <text x="{x:.0f}" y="{lny}" font-size="{int(h*0.038)}" font-weight="600" '
          f'letter-spacing="-1" fill="{SUB}">{esc(c.get("left_note",""))}</text>\n')
    s += (f'  <text x="{x:.0f}" y="{arw}" font-size="{int(h*0.055)}" font-weight="700" '
          f'fill="{FAINT}">\u2193</text>\n')
    s += (f'  <text x="{x:.0f}" y="{by}" font-size="{fs}" font-weight="700" '
          f'letter-spacing="-5" fill="{DOWN}">{esc(b)}</text>\n')
    s += (f'  <text x="{x:.0f}" y="{rny}" font-size="{int(h*0.038)}" font-weight="600" '
          f'letter-spacing="-1" fill="{SUB}">{esc(c.get("right_note",""))}</text>\n')
    if bry:
        s += "  " + bar(x, bry, w * 0.22) + "\n"
    if c.get("caption"):
        s += (f'  <text x="{x:.0f}" y="{capy}" font-size="{int(h*0.05)}" font-weight="700" '
              f'letter-spacing="-1.5" fill="{INK}">{esc(c["caption"])}</text>\n')
    return s


# ── ask — 질문 ──────────────────────────────────────
def lay_ask(c, w, h):
    ls = c["lines"][:3]
    fs = int(h * (0.105 if max(len(t) for t in ls) <= 9 else 0.086))
    gap = int(fs * 1.28)
    x = w * 0.074
    top = (h - gap * len(ls)) // 2 + int(fs * 0.85) + (20 if (w, h) == (1080, 1080) else 0)
    s = tag(x, top - gap - int(h * 0.03), c.get("tag", "SNAPVEST"), int(h * 0.026)) + "\n"
    for i, t in enumerate(ls):
        col = ACCENT if i == len(ls) - 1 else INK
        s += (f'  <text x="{x:.0f}" y="{top + i*gap}" font-size="{fs}" font-weight="700" '
              f'letter-spacing="-4" fill="{col}">{esc(t)}</text>\n')
    s += "  " + bar(x, top + (len(ls) - 1) * gap + int(h * 0.035), w * 0.22) + "\n"
    return s


# ── list — 제목 + 항목 셋 ───────────────────────────
def lay_list(c, w, h):
    x = w * 0.074
    if (w, h) == (1080, 1080):
        ty, iy, step = 330, 520, 118
    else:
        ty, iy, step = 210, 330, 82
    s = tag(x, ty - 130, c.get("tag", "SNAPVEST"), int(h * 0.026)) + "\n"
    s += (f'  <text x="{x:.0f}" y="{ty}" font-size="{int(h*0.093)}" font-weight="700" '
          f'letter-spacing="-3.5" fill="{INK}">{esc(c["title"])}</text>\n')
    s += "  " + bar(x, ty + int(h * 0.028), w * 0.22) + "\n"
    for i, t in enumerate(c["items"][:3]):
        s += (f'  <circle cx="{x + 14:.0f}" cy="{iy + i*step - 12}" r="9" fill="{ACCENT}"/>\n'
              f'  <text x="{x + 48:.0f}" y="{iy + i*step}" font-size="{int(h*0.048)}" '
              f'font-weight="700" letter-spacing="-1.5" fill="{INK}">{esc(t)}</text>\n')
    return s


# ── 사진 심기 ───────────────────────────────────────
def _embed(src, w, h, sharpen=True):
    """사진을 슬롯에 꽉 채워 자르고 base64 로 심는다.

    원본이 작으면 늘린 만큼 흐려진다. LANCZOS 로 키우고 언샵으로 윤곽만 살린다.
    그래도 2배 넘게 늘려야 하면 split 레이아웃을 쓰는 게 낫다 — 사진 칸이
    작아서 확대 배율이 그만큼 내려간다.
    """
    import base64, io
    from PIL import Image, ImageFilter
    im = Image.open(HERE / "photos" / src).convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * r)), max(h, round(im.height * r))), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((x, y, x + w, y + h))
    if sharpen and r > 1.2:
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=int(min(r, 3) * 42), threshold=3))
    b = io.BytesIO(); im.save(b, "JPEG", quality=92, subsampling=0)
    return base64.b64encode(b.getvalue()).decode()


def _scrim(x, y, w, h, gid, stops):
    g = "".join(f'<stop offset="{o}" stop-color="#0B0A18" stop-opacity="{a}"/>' for o, a in stops)
    return (f'  <linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">{g}</linearGradient>\n'
            f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gid})"/>\n')


# ── photo — 사진 전면 + 어둠막 ──────────────────────
def lay_photo(c, w, h):
    """사진을 꽉 채우고 어둠을 깔아 흰 글자를 올린다.

    막을 두 겹 깐다. 위에서 내려오는 막 하나, 왼쪽에서 오는 막 하나.
    사진 위의 글자는 대비가 전부라, 한 겹만으로는 밝은 구름 위에서 묻힌다.
    """
    b64 = _embed(c["photo"], w, h)
    ls = c["lines"][:3]
    x = w * 0.074
    n = max(len(t) for t in ls)
    # 한글은 글자폭이 대략 1em. letter-spacing -3.5 만큼 되돌려 받는다.
    fs = int(min(h * 0.108, ((w - 2 * x) + 3.5 * n) / n))
    gap = int(fs * 1.24)
    top = int(h * 0.27)
    s = f'  <image href="data:image/jpeg;base64,{b64}" x="0" y="0" width="{w}" height="{h}"/>\n'
    s += '  <defs>\n'
    s += ('    <linearGradient id="scL" x1="0" y1="0" x2="1" y2="0">'
          '<stop offset="0" stop-color="#0B0A18" stop-opacity="0.80"/>'
          '<stop offset="0.52" stop-color="#0B0A18" stop-opacity="0.42"/>'
          '<stop offset="1" stop-color="#0B0A18" stop-opacity="0"/></linearGradient>\n')
    s += '  </defs>\n'
    s += _scrim(0, 0, w, h * 0.74, "scT", [(0, 0.72), (0.5, 0.34), (1, 0)])
    s += f'  <rect x="0" y="0" width="{w}" height="{h}" fill="url(#scL)"/>\n'
    s += _scrim(int(h * 0.74), w, 0, 0, "_x", [])[:0]
    s += ('    <defs><linearGradient id="scB" x1="0" y1="0" x2="0" y2="1">'
          '<stop offset="0" stop-color="#0B0A18" stop-opacity="0"/>'
          '<stop offset="0.55" stop-color="#0B0A18" stop-opacity="0.45"/>'
          '<stop offset="1" stop-color="#0B0A18" stop-opacity="0.88"/></linearGradient></defs>\n'
          f'  <rect x="0" y="{h*0.62:.0f}" width="{w}" height="{h*0.38:.0f}" fill="url(#scB)"/>\n')
    s += (f'  <text x="{x:.0f}" y="{top - int(h*0.118)}" font-size="{int(h*0.027)}" font-weight="700" '
          f'letter-spacing="3" fill="#CDBDF7">{esc(c.get("tag","SNAPVEST"))}</text>\n')
    for i, t in enumerate(ls):
        s += (f'  <text x="{x:.0f}" y="{top + i*gap}" font-size="{fs}" font-weight="700" '
              f'letter-spacing="-3.5" fill="#FFFFFF">{esc(t)}</text>\n')
    s += "  " + bar(x, top + (len(ls)-1)*gap + int(h*0.034), w * 0.20) + "\n"
    if c.get("sub"):
        s += (f'  <text x="{x:.0f}" y="{top + (len(ls)-1)*gap + int(h*0.112)}" '
              f'font-size="{int(h*0.037)}" font-weight="600" letter-spacing="-1" '
              f'fill="#E2DBF5">{esc(c["sub"])}</text>\n')
    return s


# ── split — 글자 칸 + 사진 칸 ───────────────────────
def lay_split(c, w, h):
    """왼쪽은 브랜드 배경에 글자, 오른쪽은 사진. 원본이 작을 때 이쪽이 낫다.
    사진 칸이 좁아 확대 배율이 절반으로 떨어진다."""
    pw = int(w * (0.50 if (w, h) == (1080, 1080) else 0.42))
    px = w - pw
    b64 = _embed(c["photo"], pw, h)
    ls = c["lines"][:3]
    avail = px - w * 0.074 * 2
    fs = int(min(h * 0.100, avail / max(len(t) for t in ls) * 1.16))
    gap = int(fs * 1.30)
    x = w * 0.074
    top = (h - gap * (len(ls) - 1)) // 2 - int(h * 0.02)
    s = f'  <image href="data:image/jpeg;base64,{b64}" x="{px}" y="0" width="{pw}" height="{h}"/>\n'
    s += ('  <defs><linearGradient id="seam" x1="0" y1="0" x2="1" y2="0">'
          '<stop offset="0" stop-color="#F3EFFC" stop-opacity="1"/>'
          '<stop offset="1" stop-color="#F3EFFC" stop-opacity="0"/></linearGradient></defs>\n'
          f'  <rect x="{px}" y="0" width="{int(w*0.035)}" height="{h}" fill="url(#seam)"/>\n')
    s += (f'  <text x="{x:.0f}" y="{top - gap + int(h*0.012)}" font-size="{int(h*0.027)}" '
          f'font-weight="700" letter-spacing="3" fill="{PURPLE}">{esc(c.get("tag","SNAPVEST"))}</text>\n')
    for i, t in enumerate(ls):
        col = ACCENT if i == len(ls) - 1 and c.get("accent_last", True) else INK
        s += (f'  <text x="{x:.0f}" y="{top + i*gap}" font-size="{fs}" font-weight="700" '
              f'letter-spacing="-3" fill="{col}">{esc(t)}</text>\n')
    s += "  " + bar(x, top + (len(ls)-1)*gap + int(h*0.030), w * 0.16) + "\n"
    if c.get("sub"):
        s += (f'  <text x="{x:.0f}" y="{top + (len(ls)-1)*gap + int(h*0.098)}" '
              f'font-size="{int(h*0.034)}" font-weight="600" letter-spacing="-1" '
              f'fill="{SUB}">{esc(c["sub"])}</text>\n')
    return s

LAYOUTS = {"num": lay_num, "vs": lay_vs, "ask": lay_ask, "list": lay_list,
           "photo": lay_photo, "split": lay_split}


def build(c, w, h):
    body = LAYOUTS[c["layout"]](c, w, h)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">\n<title>{esc(c.get("alt", c.get("name","")))}</title>\n'
            f'{defs(w, h)}\n<g {FONT}>\n{body}{foot(w, h, c.get("note",""), c["layout"] == "photo", (w * (0.50 if (w, h) == (1080, 1080) else 0.42) - w*0.045) if c["layout"] == "split" else None, c.get("cta"))}\n</g>\n</svg>\n')


def shot(svg_path, png_path, w, h):
    html = svg_path.with_suffix(".html")
    html.write_text('<!doctype html><meta charset="utf-8">'
                    '<style>html,body{margin:0;padding:0;background:#fff}'
                    f'svg{{display:block;width:{w}px;height:{h}px}}</style>\n'
                    + svg_path.read_text(encoding="utf-8"), encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={w},{h + 160}",
                    f"--screenshot={png_path}", f"file://{html}"], check=True, capture_output=True)
    html.unlink()
    from PIL import Image
    im = Image.open(png_path)
    if im.size != (w, h):
        im = im.crop((0, 0, w, h))
        im.save(png_path)
    # 네이버 업로드용 JPG 를 같이 뽑는다. 배경이 매끄러운 그라데이션이라
    # PNG 는 압축이 거의 안 먹는다 (1080 기준 PNG 430KB vs JPG 61KB).
    # subsampling=0 (4:4:4) 로 저장해야 글자 가장자리에 색이 안 번진다.
    im.convert("RGB").save(png_path.with_suffix(".jpg"), "JPEG",
                           quality=90, subsampling=0, optimize=True)


def main():
    cfg = json.loads(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "thumbs.json")
                     .read_text(encoding="utf-8"))
    out = HERE / (sys.argv[2] if len(sys.argv) > 2 else "thumbs")
    (out / "svg").mkdir(parents=True, exist_ok=True)
    for c in cfg["thumbs"]:
        for key, (w, h) in SIZES.items():
            stem = f'{c["name"]}-{key}'
            svg = out / "svg" / f"{stem}.svg"
            svg.write_text(build(c, w, h), encoding="utf-8")
            png = out / f"{stem}.png"
            shot(svg, png, w, h)
            kb = png.with_suffix(".jpg").stat().st_size / 1024
            print(f"  ✓ {png.relative_to(HERE)}  {w}x{h}  [{c['layout']}]  · jpg {kb:,.0f}KB")


if __name__ == "__main__":
    main()
