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

문구는 공식대로 넣는다 (blog/BLOG-TEMPLATE.md 「썸네일 문구 공식」).

  숫자형  실적리뷰 #N   +32%          -> num    메인은 숫자 하나
  질문형  종목분석      지금 비쌀까?  -> ask    보조에 무엇으로 따졌는지
  비교형  (라벨 없음)   A사 vs B사    -> vs     보조에 누가 더 쌀까
  이유형  이슈정리      급락한 이유   -> list   badge 로 "N가지"

큰 글씨 하나 · 10자 안팎 · 좌상단 시리즈 라벨 · 하단 블로그명. 넷 다 코드가 지킨다.
10자를 넘기면 만들 때 경고가 뜬다 — 잘라서 다시 넣으라는 뜻이다.

판은 두 벌. 같은 뼈대라도 밝은 판과 어두운 판을 번갈아 쓰면 목록에서 덜 지친다.

  theme 없음      밝은 라벤더
  theme "dark"    어두운 남보라

크기는 두 벌이 같이 나온다.
  1080x1080  정사각 — 네이버 대표이미지 · 인스타
  1200x630   가로  — 오픈그래프 · 카카오/페북 공유 카드
가로판도 글자는 가운데 정사각 안에 둔다. 어디서 잘려도 살아남게.

    python3 thumb.py thumbs.json [출력폴더]
"""
import json, pathlib, subprocess, sys

from generate import (INK, SUB, FAINT, DIM, ACCENT, PURPLE, UP, DOWN,
                      LINE_SOFT, LAV, FONT, esc)

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
HERE = pathlib.Path(__file__).parent
SIZES = {"sq": (1080, 1080), "wide": (1200, 630)}
BRAND = "스냅베스트"

# 색은 두 벌뿐이다. 공식의 "컬러 2~3개 고정" 을 코드로 묶어 둔 것 —
# 레이아웃마다 색을 새로 고르기 시작하면 블로그가 흩어진다.
PAL = {
    "light": dict(ink=INK, sub=SUB, faint=FAINT, dim=DIM, lav=LAV, soft=LINE_SOFT,
                  accent=ACCENT, purple=PURPLE, up=UP, down=DOWN,
                  pill_bg="#FFFFFF", pill_op="0.82", pill_fg=PURPLE,
                  band="#FFFFFF", band_op="0.62", foot="#8B85A8", dom="url(#line)"),
    "dark":  dict(ink="#F6F3FF", sub="#ADA2D2", faint="#8A7FB4", dim="#8E84B2",
                  lav="#241D40", soft="#342C58",
                  accent="#D07BE4", purple="#CDBDF7", up="#F2719C", down="#7FADEA",
                  pill_bg="#2E2552", pill_op="1", pill_fg="#CDBDF7",
                  band="#FFFFFF", band_op="0.05", foot="#A79BCB", dom="#FFFFFF"),
}
P = PAL["light"]


def defs(w, h, dark=False):
    """generate.py 의 DEFS 는 1080 고정이라 크기를 받게 다시 쓴다. 색은 그대로.

    어두운 판은 배경 두 색과 번짐 세기만 바꾼다. 그래야 밝은 판과 형제로 보인다.
    """
    c0, c1, glow = ("#171130", "#0B0918", "0.30") if dark else ("#FBF9FF", "#EFEAFC", "0.13")
    return f'''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1">
    <stop offset="0" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/>
  </linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#4A6CF7"/><stop offset="0.5" stop-color="#B455C4"/><stop offset="1" stop-color="#E0568A"/>
  </linearGradient>
  <radialGradient id="m1" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#4A6CF7" stop-opacity="{glow}"/><stop offset="1" stop-color="#4A6CF7" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="m2" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#E0568A" stop-opacity="{glow}"/><stop offset="1" stop-color="#E0568A" stop-opacity="0"/>
  </radialGradient>
</defs>
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<rect x="{-w*0.19:.0f}" y="{-h*0.15:.0f}" width="{w*0.84:.0f}" height="{w*0.84:.0f}" fill="url(#m1)"/>
<rect x="{w*0.41:.0f}" y="{h*0.46:.0f}" width="{w*0.87:.0f}" height="{w*0.87:.0f}" fill="url(#m2)"/>'''


def foot(w, h, note, dark=False, dom_x=None, cta=None):
    """좌하단 블로그명 + 우하단 한마디.

    공식의 '하단 블로그명' 자리다. note 를 비워 두면 블로그명이 들어간다 —
    포맷이 달라도 아래쪽에 같은 이름이 박혀 있어야 한 블로그로 읽힌다.
    카드뉴스의 '밀어서 보기' 같은 인스타 장치는 여기 넣지 않는다.
    """
    y = h - 52
    s = ""
    left = BRAND if note is None else note
    if left:
        s += (f'  <text x="{w*0.074:.0f}" y="{y}" font-size="{int(h*0.030)}" font-weight="700" '
              f'letter-spacing="-0.3" fill="{"#CFC6E8" if dark else P["foot"]}">{esc(left)}</text>\n')
    label = "snapvestai.com" if cta is None else cta
    if label:
        s += (f'  <text x="{(dom_x if dom_x else w - w*0.074):.0f}" y="{y}" text-anchor="end" font-size="{int(h*0.030)}" '
              f'font-weight="700" letter-spacing="-0.5" fill="{"#FFFFFF" if dark else P["dom"]}">{esc(label)}</text>')
    return s.rstrip("\n")


def bar(x, y, w, h=13):
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h}" rx="{h//2}" fill="url(#line)"/>'


def _tw(text, size, ls):
    """글자 폭 어림. 한글은 한 칸, 로마자·숫자는 0.58 칸으로 센다."""
    return sum(1.0 if ord(c) > 0x2000 else 0.58 for c in text) * size + ls * max(len(text) - 1, 0)


def pill_w(text, size):
    return _tw(text, size, size * 0.16) + int(size * 0.72) * 2


def pill(x, y, text, size, bg=None, fg=None):
    """좌상단 시리즈 라벨. 글자만 두면 꼬리표로 안 읽혀서 알약을 깐다.

    '실적리뷰 #3' 처럼 시리즈 이름을 넣는 자리다. 같은 라벨이 반복되면
    독자가 글 하나가 아니라 연재로 받아들인다 — 공식이 이걸 노린다.
    """
    if not text:
        return ""
    size = max(size, 28)
    ls = size * 0.16
    px, ph = int(size * 0.72), int(size * 1.85)
    return (f'  <rect x="{x:.0f}" y="{y - ph*0.70:.0f}" width="{_tw(text, size, ls) + px*2:.0f}" '
            f'height="{ph}" rx="{ph//2}" fill="{bg or P["pill_bg"]}" opacity="{P["pill_op"]}"/>\n'
            f'  <text x="{x + px:.0f}" y="{y:.0f}" font-size="{size}" font-weight="700" '
            f'letter-spacing="{ls:.1f}" fill="{fg or P["pill_fg"]}">{esc(text)}</text>')


def tag(x, y, text, size):
    return pill(x, y, text, size)


def badge(x, y, text, size):
    """숫자 배지 — "3가지". 라벨 옆에 붙여 몇 개를 다루는 글인지 먼저 알린다."""
    ls = size * 0.1
    px, ph = int(size * 0.72), int(size * 1.85)
    return (f'  <rect x="{x:.0f}" y="{y - ph*0.70:.0f}" width="{_tw(text, size, ls) + px*2:.0f}" '
            f'height="{ph}" rx="{ph//2}" fill="url(#line)"/>\n'
            f'  <text x="{x + px:.0f}" y="{y:.0f}" font-size="{size}" font-weight="700" '
            f'letter-spacing="{ls:.1f}" fill="#FFFFFF">{esc(text)}</text>')


# ── num — 숫자 하나 ─────────────────────────────────
def lay_num(c, w, h):
    big = c["big"]
    col = {"up": P["up"], "down": P["down"], "accent": P["accent"]}.get(c.get("tone", "accent"), ACCENT)
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
              f'font-weight="700" letter-spacing="-2" fill="{P["ink"]}">{esc(t)}</text>\n')
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
          f'letter-spacing="-5" fill="{P["up"]}">{esc(a)}</text>\n')
    s += (f'  <text x="{x:.0f}" y="{lny}" font-size="{int(h*0.038)}" font-weight="600" '
          f'letter-spacing="-1" fill="{P["sub"]}">{esc(c.get("left_note",""))}</text>\n')
    s += (f'  <text x="{x:.0f}" y="{arw}" font-size="{int(h*0.055)}" font-weight="700" '
          f'fill="{P["faint"]}">\u2193</text>\n')
    s += (f'  <text x="{x:.0f}" y="{by}" font-size="{fs}" font-weight="700" '
          f'letter-spacing="-5" fill="{P["down"]}">{esc(b)}</text>\n')
    s += (f'  <text x="{x:.0f}" y="{rny}" font-size="{int(h*0.038)}" font-weight="600" '
          f'letter-spacing="-1" fill="{P["sub"]}">{esc(c.get("right_note",""))}</text>\n')
    if bry:
        s += "  " + bar(x, bry, w * 0.22) + "\n"
    if c.get("caption"):
        s += (f'  <text x="{x:.0f}" y="{capy}" font-size="{int(h*0.05)}" font-weight="700" '
              f'letter-spacing="-1.5" fill="{P["ink"]}">{esc(c["caption"])}</text>\n')
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
        col = P["accent"] if i == len(ls) - 1 else P["ink"]
        s += (f'  <text x="{x:.0f}" y="{top + i*gap}" font-size="{fs}" font-weight="700" '
              f'letter-spacing="-4" fill="{col}">{esc(t)}</text>\n')
    s += "  " + bar(x, top + (len(ls) - 1) * gap + int(h * 0.035), w * 0.22) + "\n"
    if c.get("sub"):
        # 보조 한 줄 — 무엇으로 따졌는지. 질문만 던지고 끝내면 낚시처럼 읽힌다.
        s += (f'  <text x="{x:.0f}" y="{top + (len(ls)-1)*gap + int(h*0.115)}" '
              f'font-size="{int(h*0.042)}" font-weight="600" letter-spacing="-1" '
              f'fill="{P["sub"]}">{esc(c["sub"])}</text>\n')
    return s


# ── list — 제목 + 항목 셋 ───────────────────────────
def lay_list(c, w, h):
    x = w * 0.074
    if (w, h) == (1080, 1080):
        ty, iy, step = 330, 520, 118
    else:
        ty, iy, step = 210, 330, 82
    lab, lsz = c.get("tag", "SNAPVEST"), int(h * 0.026)
    s = tag(x, ty - 130, lab, lsz) + "\n"
    if c.get("badge"):
        s += badge(x + pill_w(lab, max(lsz, 28)) + 14, ty - 130, c["badge"], max(lsz, 28)) + "\n"
    s += (f'  <text x="{x:.0f}" y="{ty}" font-size="{int(h*0.093)}" font-weight="700" '
          f'letter-spacing="-3.5" fill="{P["ink"]}">{esc(c["title"])}</text>\n')
    s += "  " + bar(x, ty + int(h * 0.028), w * 0.22) + "\n"
    for i, t in enumerate(c["items"][:3]):
        s += (f'  <circle cx="{x + 14:.0f}" cy="{iy + i*step - 12}" r="9" fill="{P["accent"]}"/>\n'
              f'  <text x="{x + 48:.0f}" y="{iy + i*step}" font-size="{int(h*0.048)}" '
              f'font-weight="700" letter-spacing="-1.5" fill="{P["ink"]}">{esc(t)}</text>\n')
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
    # 여백을 줄이고 자간을 더 좁혀 같은 캔버스에서 글자를 키운다.
    # 사진 포스터는 검색 결과에서 작게 보이므로 글자가 클수록 유리하다.
    x = w * 0.058
    n = max(len(t) for t in ls)
    LS = 5.0                      # letter-spacing. 음수만큼 폭을 되돌려 받는다
    fs = int(min(h * 0.118, ((w - 2 * x) + LS * n) / n))
    gap = int(fs * 1.22)
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
    s += (f'  <text x="{x:.0f}" y="{top - int(h*0.092)}" font-size="{int(h*0.036)}" font-weight="700" '
          f'letter-spacing="2.5" fill="#CDBDF7">{esc(c.get("tag","SNAPVEST"))}</text>\n')
    for i, t in enumerate(ls):
        s += (f'  <text x="{x:.0f}" y="{top + i*gap}" font-size="{fs}" font-weight="700" '
              f'letter-spacing="-5" fill="#FFFFFF">{esc(t)}</text>\n')
    s += "  " + bar(x, top + (len(ls)-1)*gap + int(h*0.036), w * 0.22, int(h*0.015)) + "\n"
    if c.get("sub"):
        s += (f'  <text x="{x:.0f}" y="{top + (len(ls)-1)*gap + int(h*0.125)}" '
              f'font-size="{int(h*0.046)}" font-weight="600" letter-spacing="-1" '
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
          f'font-weight="700" letter-spacing="3" fill="{P["purple"]}">{esc(c.get("tag","SNAPVEST"))}</text>\n')
    for i, t in enumerate(ls):
        col = P["accent"] if i == len(ls) - 1 and c.get("accent_last", True) else P["ink"]
        s += (f'  <text x="{x:.0f}" y="{top + i*gap}" font-size="{fs}" font-weight="700" '
              f'letter-spacing="-3" fill="{col}">{esc(t)}</text>\n')
    s += "  " + bar(x, top + (len(ls)-1)*gap + int(h*0.030), w * 0.16) + "\n"
    if c.get("sub"):
        s += (f'  <text x="{x:.0f}" y="{top + (len(ls)-1)*gap + int(h*0.098)}" '
              f'font-size="{int(h*0.034)}" font-weight="600" letter-spacing="-1" '
              f'fill="{P["sub"]}">{esc(c["sub"])}</text>\n')
    return s

# ── table — 비교표 ──────────────────────────────────
# 표는 캔버스가 고정이 아니다. 줄 수에 맞춰 높이를 계산해 세로로 늘린다.
# 블로그 본문에 넣는 그림이라 가로 1080 에 세로는 내용만큼이면 된다.
TB = dict(pad=64, title=72, sub=34, head=104, gap_t=36, note=32)


def _row_h(n):
    return 76 if n <= 12 else 68 if n <= 20 else 62


def table_size(c):
    rows = c["rows"]
    rh = _row_h(len(rows))
    body = sum(int(rh * 0.88) if _is_div(r) else rh for r in rows)
    h = (TB["pad"] + TB["title"] + (TB["sub"] + 14 if c.get("sub") else 0) + TB["gap_t"]
         + TB["head"] + body + (TB["note"] + 30 if c.get("note") else -18) + TB["pad"])
    return 1080, int(h)


def _is_div(r):
    return len(r) == 1


def lay_table(c, w, h):
    rows, cols = c["rows"], c["cols"]
    pad = TB["pad"]
    rh = _row_h(len(rows))
    # 라벨 칸은 넓게, 값 칸 셋은 똑같이 나눈다
    lab_w = int((w - pad * 2) * 0.355)
    cw = (w - pad * 2 - lab_w) / 3
    cx = [pad + lab_w + cw * (i + 0.5) for i in range(3)]

    s = f'  <text x="{pad}" y="{pad + 54}" font-size="{TB["title"]}" font-weight="700" ' \
        f'letter-spacing="-2.5" fill="{P["ink"]}">{esc(c["title"])}</text>\n'
    y = pad + 54
    if c.get("sub"):
        y += TB["sub"] + 14
        s += (f'  <text x="{pad}" y="{y}" font-size="{TB["sub"]}" font-weight="600" '
              f'letter-spacing="-1" fill="{P["sub"]}">{esc(c["sub"])}</text>\n')
    y += TB["gap_t"]

    # 머리줄 — 상품 이름 두 줄 (티커행 / 설명행)
    s += (f'  <rect x="{pad}" y="{y}" width="{w - pad*2}" height="{TB["head"]}" rx="20" '
          f'fill="{P["lav"]}"/>\n')
    for i, col in enumerate(cols):
        a, _, b = col.partition("|")
        s += (f'  <text x="{cx[i]:.0f}" y="{y + 42}" text-anchor="middle" font-size="44" '
              f'font-weight="700" letter-spacing="-1" fill="{P["ink"]}">{esc(a)}</text>\n')
        if b:
            s += (f'  <text x="{cx[i]:.0f}" y="{y + 80}" text-anchor="middle" font-size="27" '
                  f'font-weight="600" letter-spacing="-0.5" fill="{P["faint"]}">{esc(b)}</text>\n')
    y += TB["head"]

    band = 0
    for r in rows:
        if _is_div(r):                      # 구분 머리 — 묶음 이름
            dh = int(rh * 0.88)
            s += (f'  <text x="{pad}" y="{y + dh*0.78:.0f}" font-size="30" font-weight="700" '
                  f'letter-spacing="1.5" fill="{P["purple"]}">{esc(r[0])}</text>\n')
            y += dh
            band = 0
            continue
        if band % 2 == 1:
            s += (f'  <rect x="{pad}" y="{y}" width="{w - pad*2}" height="{rh}" '
                  f'fill="{P["band"]}" opacity="{P["band_op"]}"/>\n')
        s += (f'  <text x="{pad + 16}" y="{y + rh*0.66:.0f}" font-size="36" font-weight="600" '
              f'letter-spacing="-0.8" fill="{P["sub"]}">{esc(r[0])}</text>\n')
        for i, v in enumerate(r[1:4]):
            v = str(v)
            hl = v.startswith("*")
            if hl:
                v = v[1:]
            col = P["accent"] if hl else (P["dim"] if v in ("-", "—", "") else P["ink"])
            # 칸을 넘치면 그 칸만 글자를 줄인다. 이웃 칸과 붙는 것보다 낫다.
            fs = 40 if hl else 38
            wide = sum(1.0 if ord(ch) > 0x2000 else 0.56 for ch in v)   # 한글은 한 칸
            if wide * fs > cw - 16:
                fs = max(26, int((cw - 16) / wide))
            s += (f'  <text x="{cx[i]:.0f}" y="{y + rh*0.66:.0f}" text-anchor="middle" '
                  f'font-size="{fs}" font-weight="700" letter-spacing="-0.8" '
                  f'fill="{col}">{esc(v)}</text>\n')
        y += rh
        band += 1

    if c.get("note"):
        s += (f'  <line x1="{pad}" y1="{y + 6}" x2="{w - pad}" y2="{y + 6}" '
              f'stroke="{P["soft"]}" stroke-width="3"/>\n')
        s += (f'  <text x="{pad}" y="{y + 54}" font-size="{TB["note"]}" font-weight="600" '
              f'letter-spacing="-0.6" fill="{P["dim"]}">{esc(c["note"])}</text>\n')
    return s

# ── band — 글 맨 끝에 붙이는 띠 ──────────────────────
# 블로그 모든 글의 마지막에 같은 모양으로 들어간다. 매번 새로 만들지 않는다.
#   shot 없음 — 1080x440, 그라데이션 버튼
#   shot 있음 — 1080x700, 앱스토어 검색 화면을 그대로 보여준다
def band_size(c):
    return (1080, 700) if c.get("shot") else (1080, 440)


def lay_band(c, w, h):
    x, pad = 64, 64
    shot = c.get("shot")
    s = (f'  <text x="{x}" y="{88 if shot else 96}" font-size="27" font-weight="700" '
         f'letter-spacing="3" fill="{P["purple"]}">{esc(c.get("tag", "SNAPVEST"))}</text>\n')
    top = 158 if shot else 172
    for i, t in enumerate(c["lines"][:2]):
        col = P["accent"] if i == 1 and c.get("accent_last") else P["ink"]
        s += (f'  <text x="{x}" y="{top + i*62}" font-size="{50 if shot else 52}" '
              f'font-weight="700" letter-spacing="-2.5" fill="{col}">{esc(t)}</text>\n')
    if c.get("sub"):
        s += (f'  <text x="{x}" y="{268 if shot else 292}" font-size="38" font-weight="600" '
              f'letter-spacing="-1" fill="{P["sub"]}">{esc(c["sub"])}</text>\n')

    if shot:
        # 앱스토어 화면을 그대로 띄운다. 말보다 이게 빠르다.
        iw = w - pad * 2
        from PIL import Image as _I
        src = _I.open(HERE / "photos" / shot)
        ih = round(iw * src.height / src.width)
        iy = 300
        b64 = _embed(shot, iw, ih, sharpen=False)
        s += ('  <defs>\n'
              f'    <clipPath id="shotclip"><rect x="{pad}" y="{iy}" width="{iw}" '
              f'height="{ih}" rx="28"/></clipPath>\n'
              '    <filter id="shotsh" x="-20%" y="-20%" width="140%" height="140%">\n'
              '      <feDropShadow dx="0" dy="10" stdDeviation="18" flood-color="#5B4B8A" flood-opacity="0.16"/>\n'
              '    </filter>\n  </defs>\n')
        s += (f'  <rect x="{pad}" y="{iy}" width="{iw}" height="{ih}" rx="28" '
              f'fill="#FFFFFF" filter="url(#shotsh)"/>\n')
        s += (f'  <image href="data:image/jpeg;base64,{b64}" x="{pad}" y="{iy}" '
              f'width="{iw}" height="{ih}" clip-path="url(#shotclip)"/>\n')
        return s

    bw, by, bh = w - pad * 2, 334, 82
    s += f'  <rect x="{pad}" y="{by}" width="{bw}" height="{bh}" rx="{bh//2}" fill="url(#line)"/>\n'
    s += (f'  <text x="{w//2}" y="{by + 54}" text-anchor="middle" font-size="36" '
          f'font-weight="700" letter-spacing="-0.8" fill="#FFFFFF">{esc(c["button"])}</text>\n')
    return s


LAYOUTS = {"num": lay_num, "vs": lay_vs, "ask": lay_ask, "list": lay_list,
           "photo": lay_photo, "split": lay_split,
           "table": lay_table, "band": lay_band}


def build(c, w, h):
    global P
    dark = c.get("theme") == "dark"
    P = PAL["dark" if dark else "light"]
    body = LAYOUTS[c["layout"]](c, w, h)
    tail = "" if c["layout"] in ("table", "band") else foot(
        w, h, c.get("note"), dark or c["layout"] == "photo",
        (w * (0.50 if (w, h) == (1080, 1080) else 0.42) - w*0.045) if c["layout"] == "split" else None,
        c.get("cta"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img">\n<title>{esc(c.get("alt", c.get("name","")))}</title>\n'
            f'{defs(w, h, dark)}\n<g {FONT}>\n{body}{tail}\n</g>\n</svg>\n')


def shot(svg_path, png_path, w, h, photo=False):
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
    # 저장 규칙 — 글자·그래프는 PNG, 사진은 JPG.
    # JPG 는 글자 테두리를 뭉갠다. 그런데 우리 배경이 매끄러운 그라데이션이라
    # 그냥 PNG 로 두면 용량이 안 줄어든다 (1080 정사각 기준 455KB).
    # 색수를 128 로 줄이고 디더링을 걸면 131KB 로 내려가면서 글자는 그대로다.
    im = im.convert("RGB")
    if photo:
        im.save(png_path.with_suffix(".jpg"), "JPEG", quality=90,
                subsampling=0, optimize=True)
        png_path.unlink(missing_ok=True)
    else:
        im.quantize(colors=128, method=Image.MEDIANCUT,
                    dither=Image.FLOYDSTEINBERG).save(png_path, "PNG", optimize=True)


def over10(c):
    """공식의 '전체 10자 안팎'. 넘기면 알려 준다 — 썸네일은 글이 아니라 간판이다."""
    big = {"num": [c.get("big", "")], "vs": [c.get("left", ""), c.get("right", "")],
           "ask": c.get("lines", []), "list": [c.get("title", "")],
           "photo": c.get("lines", []), "split": c.get("lines", [])}.get(c["layout"], [])
    return [t for t in big if len(t) > 11]


def main():
    cfg = json.loads(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "thumbs.json")
                     .read_text(encoding="utf-8"))
    out = HERE / (sys.argv[2] if len(sys.argv) > 2 else "thumbs")
    (out / "svg").mkdir(parents=True, exist_ok=True)
    for c in cfg["thumbs"]:
        sizes = ({"": table_size(c)} if c["layout"] == "table"
                 else {"": band_size(c)} if c["layout"] == "band"
                 else SIZES)
        for key, (w, h) in sizes.items():
            stem = f'{c["name"]}-{key}' if key else c["name"]
            svg = out / "svg" / f"{stem}.svg"
            svg.write_text(build(c, w, h), encoding="utf-8")
            png = out / f"{stem}.png"
            shot(svg, png, w, h, c["layout"] in ("photo", "split"))
            final = png.with_suffix(".jpg") if c["layout"] in ("photo", "split") else png
            print(f"  ✓ {final.relative_to(HERE)}  {w}x{h}  [{c['layout']}"
                  f"{'·dark' if c.get('theme') == 'dark' else ''}]"
                  f"  {final.stat().st_size/1024:,.0f}KB")
        for t in over10(c):
            print(f"    ⚠ 10자 넘음 ({len(t)}자) — \"{t}\"")


if __name__ == "__main__":
    main()
