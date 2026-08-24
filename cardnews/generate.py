#!/usr/bin/env python3
"""
Snapvest 카드뉴스 생성기
────────────────────────────────────────────────
config.json 의 값만 바꿔서 실행하면 1080x1080 SVG 5장이 나옵니다.
디자인·레이아웃은 절대 수정하지 마세요. 값만 교체합니다.

  python3 generate.py config.json  [출력폴더]
"""
import base64, json, pathlib, random, sys

# ── 디자인 토큰 (수정 금지) ────────────────────────
INK, SUB, FAINT, DIM = "#2B2B3A", "#8B85A8", "#9691B8", "#B9B3D6"
ACCENT, PURPLE = "#B455C4", "#8B5BD6"
UP, DOWN = "#E0568A", "#5A8FD6"
LINE_SOFT, TRACK, LAV = "#F1EDFA", "#E7E1F7", "#EFEAFC"
FONT = 'font-family="Pretendard, Poppins, Arial, sans-serif"'

DEFS = '''<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1">
    <stop offset="0" stop-color="#FBF9FF"/><stop offset="1" stop-color="#EFEAFC"/>
  </linearGradient>
  <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#4A6CF7"/><stop offset="0.5" stop-color="#B455C4"/><stop offset="1" stop-color="#E0568A"/>
  </linearGradient>
  <linearGradient id="dom" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#4A6CF7"/><stop offset="0.55" stop-color="#B455C4"/><stop offset="1" stop-color="#E0568A"/>
  </linearGradient>
</defs>
<rect width="1080" height="1080" fill="url(#bg)"/>
<circle cx="920" cy="180" r="200" fill="#B455C4" opacity="0.06"/>'''


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def hdr(date):
    return f'''  <text x="80" y="118" font-size="30" fill="{ACCENT}">\u2726</text>
  <text x="126" y="118" font-size="25" font-weight="700" letter-spacing="2.5" fill="{PURPLE}">SNAPVEST AI SIGNAL</text>
  <text x="1000" y="118" text-anchor="end" font-size="25" font-weight="600" fill="{DIM}">{esc(date)}</text>'''


def dom(y):
    return (f'<text x="1000" y="{y}" text-anchor="end" font-size="27" '
            f'font-weight="700" fill="url(#dom)">snapvestai.com</text>')


def wrap(svg, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" '
            f'viewBox="0 0 1080 1080" role="img">\n<title>{esc(title)}</title>\n{svg}\n</svg>\n')


def photo_slot(y, h, note=""):
    """사진 자리 (점선 플레이스홀더)"""
    return f'''<rect x="40" y="{y}" width="1000" height="{h}" rx="52" fill="#F3F0FC"/>
<rect x="40" y="{y}" width="1000" height="{h}" rx="52" fill="none" stroke="#D6CBFA" stroke-width="4" stroke-dasharray="16 13"/>
<g {FONT} text-anchor="middle">
  <text x="540" y="{y + h/2 - 12:.0f}" font-size="32" font-weight="700" fill="{FAINT}">사진 영역</text>
  <text x="540" y="{y + h/2 + 32:.0f}" font-size="24" font-weight="500" fill="{DIM}">1000 × {h}{esc(note)}</text>
</g>'''


def photo_embed(path, y, h, cid):
    """이미지 실제 삽입"""
    b64 = base64.b64encode(pathlib.Path(path).read_bytes()).decode()
    ext = pathlib.Path(path).suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return (f'<defs><clipPath id="{cid}"><rect x="40" y="{y}" width="1000" height="{h}" rx="52"/></clipPath></defs>\n'
            f'<g clip-path="url(#{cid})"><image x="40" y="{y}" width="1000" height="{h}" '
            f'preserveAspectRatio="xMidYMid slice" href="data:image/{mime};base64,{b64}"/></g>')


def img_block(spec, y, h, cid, note=""):
    if spec and pathlib.Path(spec).exists():
        return photo_embed(spec, y, h, cid)
    return photo_slot(y, h, note)


def logo_chip(spec, cx, cy, r):
    """표지 원형 로고 (없으면 빈 원)"""
    if not (spec and pathlib.Path(spec).exists()):
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{LAV}"/>'
    b64 = base64.b64encode(pathlib.Path(spec).read_bytes()).decode()
    ext = pathlib.Path(spec).suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    return (f'<defs><clipPath id="logo"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath></defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{LAV}"/>'
            f'<image clip-path="url(#logo)" x="{cx - r}" y="{cy - r}" width="{r * 2}" '
            f'height="{r * 2}" preserveAspectRatio="xMidYMid slice" '
            f'href="data:image/{mime};base64,{b64}"/>')


def strong_name(c, line):
    """표지 첫 줄에서 종목명만 더 굵게. 종목명으로 시작하지 않으면 그대로 둔다"""
    name = str(c.get("company_ko", ""))
    if name and line.startswith(name):
        return (f'<tspan font-weight="900">{esc(name)}</tspan>'
                f'<tspan font-weight="700">{esc(line[len(name):])}</tspan>')
    return f'<tspan font-weight="700">{esc(line)}</tspan>'


# ── 1. 표지 ────────────────────────────────────────
def card1(c, align="end"):
    """align="end" 우측 정렬(기본) · align="middle" 중간 정렬"""
    tx = 1000 if align == "end" else 540
    bx = 760 if align == "end" else 420
    return wrap(f'''{DEFS}
<g {FONT}>
{hdr(c["date"])}
  <text x="{tx}" y="338" text-anchor="{align}" font-size="88" letter-spacing="-3" fill="{INK}">{strong_name(c, c["cover_line1"])}</text>
  <text x="{tx}" y="442" text-anchor="{align}" font-size="88" font-weight="700" letter-spacing="-3" fill="{INK}">{esc(c["cover_line2"])}</text>
  <text x="{tx}" y="546" text-anchor="{align}" font-size="88" font-weight="700" letter-spacing="-3" fill="{ACCENT}">{esc(c["cover_line3"])}</text>
  <rect x="{bx}" y="600" width="240" height="14" rx="7" fill="url(#line)"/>

  <rect x="80" y="664" width="920" height="336" rx="52" fill="#FFFFFF"/>
  {logo_chip(c.get("logo"), 176, 760, 40)}
  <text x="244" y="752" font-size="32" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(c["company_en"])}</text>
  <text x="244" y="794" font-size="23" font-weight="600" letter-spacing="0.5" fill="{FAINT}">{esc(c["ticker"])} · {esc(c["exchange"])}</text>
  <text x="944" y="752" text-anchor="end" font-size="40" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(c["price"])}</text>
  <text x="944" y="794" text-anchor="end" font-size="26" font-weight="700" fill="{UP if not str(c["change"]).startswith("-") else DOWN}">{esc(c["change"])}</text>
  <line x1="136" y1="832" x2="944" y2="832" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="136" y="890" font-size="27" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(c["cover_fact1"])}</text>
  <text x="136" y="932" font-size="27" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(c["cover_fact2"])}</text>

  <text x="80" y="1046" font-size="27" font-weight="700" letter-spacing="-0.5" fill="{DIM}">밀어서 보기 →</text>
  {dom(1046)}
</g>''', f'{c["company_ko"]} · 표지')


# ── 2. 기업 설명 ───────────────────────────────────
def card2(c):
    """사진 · 설명 2줄 · 보조 2줄 · 사업 부문 칩 3개 · 하단 지표 3열
    desc_sub2 와 segments 는 없으면 그 줄이 통째로 빠진다."""
    sub2 = c.get("desc_sub2")
    sub2_svg = (f'  <text x="80" y="768" font-size="27" font-weight="500" '
                f'letter-spacing="-0.5" fill="{SUB}">{esc(sub2)}</text>\n') if sub2 else ""

    segs, seg_svg = c.get("segments") or [], ""
    for i, s in enumerate(segs[:3]):
        x = 80 + i * 312
        seg_svg += (f'  <rect x="{x}" y="800" width="296" height="54" rx="27" fill="#FFFFFF"/>\n'
                    f'  <text x="{x + 148}" y="834" text-anchor="middle" font-size="24" '
                    f'font-weight="700" letter-spacing="-0.5" fill="{PURPLE}">{esc(s)}</text>\n')

    return wrap(f'''{DEFS}
{img_block(c.get("photo_company"), 280, 290, "pc")}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="222" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">{esc(c["company_ko"])}는 <tspan fill="{ACCENT}">어떤 회사</tspan>일까?</text>
  <rect x="80" y="248" width="220" height="12" rx="6" fill="url(#line)"/>

  <text x="80" y="634" font-size="38" font-weight="700" letter-spacing="-1.5" fill="{INK}">{esc(c["desc_lead1"])}</text>
  <text x="80" y="684" font-size="38" font-weight="700" letter-spacing="-1.5" fill="{INK}">{esc(c["desc_lead2"])}</text>
  <text x="80" y="730" font-size="27" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(c["desc_sub"])}</text>
{sub2_svg}{seg_svg}
  <rect x="80" y="880" width="920" height="172" rx="52" fill="#FFFFFF"/>
  <text x="233" y="942" text-anchor="middle" font-size="24" font-weight="600" fill="{FAINT}">시가총액</text>
  <text x="233" y="998" text-anchor="middle" font-size="42" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(c["market_cap"])}</text>
  <line x1="387" y1="922" x2="387" y2="1010" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="540" y="942" text-anchor="middle" font-size="24" font-weight="600" fill="{FAINT}">거래량</text>
  <text x="540" y="998" text-anchor="middle" font-size="42" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(c["volume"])}</text>
  <line x1="693" y1="922" x2="693" y2="1010" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="847" y="942" text-anchor="middle" font-size="24" font-weight="600" fill="{FAINT}">52주 위치</text>
  <text x="847" y="998" text-anchor="middle" font-size="42" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(c["week52"])}</text>
</g>''', f'{c["company_ko"]} · 어떤 회사일까')


# ── 3. 급등 이유 ───────────────────────────────────
def card3(c):
    body = "".join(
        f'  <text x="80" y="{856 + i*42}" font-size="28" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(t)}</text>\n'
        for i, t in enumerate(c["reason_body"][:3]))
    return wrap(f'''{DEFS}
{img_block(c.get("photo_reason"), 288, 372, "pr", " · 가로 꽉 채워 배치")}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="222" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">그래서 <tspan fill="{ACCENT}">왜 {esc(c["reason_verb"])}</tspan>?</text>
  <rect x="80" y="248" width="220" height="12" rx="6" fill="url(#line)"/>

  <text x="80" y="740" font-size="38" font-weight="700" letter-spacing="-1.5" fill="{INK}">{esc(c["reason_lead1"])}</text>
  <text x="80" y="790" font-size="38" font-weight="700" letter-spacing="-1.5" fill="{INK}">{esc(c["reason_lead2"])}</text>

{body}
  <text x="80" y="1046" font-size="25" font-weight="600" fill="{DIM}">{esc(c["reason_source"])}</text>
  {dom(1046)}
</g>''', f'{c["company_ko"]} · 급등 이유')


# ── 4. 차트 + 지표 ─────────────────────────────────
def make_candles(cfg):
    """실제 OHLCV 가 있으면 그대로, 없으면 시드 기반 생성"""
    if cfg.get("candles"):
        return cfg["candles"]
    n = cfg.get("candle_count", 46)
    random.seed(cfg.get("seed", 11))
    out, p = [], cfg.get("candle_start", 60.0)
    end = cfg.get("candle_end", p * 2.7)
    for _ in range(n - 1):
        o = p
        cl = o * (1 + random.uniform(-0.042, 0.042))
        out.append([o, max(o, cl) * (1 + random.uniform(.002, .020)),
                    min(o, cl) * (1 - random.uniform(.002, .020)), cl,
                    random.uniform(.22, .60)])
        p = cl
    out.append([p, end * 1.024, p * 0.985, end, 1.0])
    return out


def gauge(y, name, name_w, val, val_color, status, ratio):
    fill_w = max(28, min(920, 920 * ratio))
    cx = 80 + fill_w
    return f'''  <text x="80" y="{y}" font-size="30" font-weight="700" letter-spacing="-0.5" fill="{INK}">{esc(name)}</text>
  <text x="{80 + name_w}" y="{y}" font-size="27" font-weight="700" fill="{val_color}">{esc(val)}</text>
  <text x="1000" y="{y}" text-anchor="end" font-size="25" font-weight="600" fill="{SUB}">{esc(status)}</text>
  <rect x="80" y="{y+18}" width="920" height="28" rx="14" fill="{TRACK}"/>
  <rect x="80" y="{y+18}" width="{fill_w:.0f}" height="28" rx="14" fill="url(#line)"/>
  <circle cx="{cx:.0f}" cy="{y+32}" r="21" fill="#FFFFFF" stroke="{val_color}" stroke-width="6"/>'''


def card4(c):
    candles = make_candles(c)
    N = len(candles)
    X0, X1, YT, YB, VT, VB = 92, 988, 346, 568, 592, 648
    lo = min(x[2] for x in candles) * 0.97
    hi = max(x[1] for x in candles) * 1.03
    py = lambda v: YB - (v - lo) / (hi - lo) * (YB - YT)
    step = (X1 - X0) / N
    bw = step * 0.56
    p = [f'<line x1="{X0}" y1="{py(lo+(hi-lo)*f):.1f}" x2="{X1}" y2="{py(lo+(hi-lo)*f):.1f}" stroke="{LINE_SOFT}" stroke-width="2"/>'
         for f in (0, .33, .66, 1)]
    for i, (o, h, l, cl, v) in enumerate(candles):
        cx = X0 + step * (i + .5)
        col = UP if cl >= o else DOWN
        p.append(f'<line x1="{cx:.1f}" y1="{py(h):.1f}" x2="{cx:.1f}" y2="{py(l):.1f}" stroke="{col}" stroke-width="2"/>')
        t, b = py(max(o, cl)), py(min(o, cl))
        p.append(f'<rect x="{cx-bw/2:.1f}" y="{t:.1f}" width="{bw:.1f}" height="{max(b-t,2):.1f}" rx="1.4" fill="{col}"/>')
        vh = v * (VB - VT)
        p.append(f'<rect x="{cx-bw/2:.1f}" y="{VB-vh:.1f}" width="{bw:.1f}" height="{vh:.1f}" rx="1.4" fill="{col}" opacity="0.3"/>')

    g = c["gauges"]
    return wrap(f'''{DEFS}
<rect x="52" y="288" width="976" height="400" rx="52" fill="#FFFFFF"/>
<g {FONT}>
  <text x="92" y="326" font-size="24" font-weight="700" letter-spacing="-0.5" fill="{INK}">{esc(c["ticker"])} 일봉</text>
  <text x="988" y="326" text-anchor="end" font-size="22" font-weight="600" fill="{DIM}">최근 {N}일</text>
</g>
{"".join(p)}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="222" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">지표는 <tspan fill="{ACCENT}">지금 어디쯤</tspan>일까?</text>
  <rect x="80" y="248" width="220" height="12" rx="6" fill="url(#line)"/>

{gauge(754, "MFI", 86, g["mfi"], UP, g["mfi_status"], g["mfi"]/100)}
{gauge(856, "RSI", 80, g["rsi"], ACCENT, g["rsi_status"], g["rsi"]/100)}
{gauge(958, "볼린저밴드", 184, g["bb"], UP, g["bb_status"], min(float(g["bb"]), 1.0))}

  <text x="80" y="1046" font-size="25" font-weight="600" fill="{DIM}">{esc(c["gauge_note"])}</text>
  {dom(1046)}
</g>''', f'{c["company_ko"]} · 지표')


# ── 5. 마무리 ──────────────────────────────────────
def card5(c):
    items = "".join(
        f'  <text x="146" y="{508 + i*62}" font-size="30" font-weight="700" letter-spacing="-0.8" fill="{INK}">{esc(t)}</text>\n'
        for i, t in enumerate(c["cta_items"][:3]))
    return wrap(f'''{DEFS}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="252" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">그럼 <tspan fill="{ACCENT}">내부자</tspan>는</text>
  <text x="80" y="330" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">지금 사고 있을까?</text>
  <rect x="80" y="356" width="220" height="12" rx="6" fill="url(#line)"/>

  <rect x="80" y="428" width="920" height="330" rx="52" fill="#FFFFFF"/>
{items}  <line x1="146" y1="670" x2="934" y2="670" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="146" y="722" font-size="28" font-weight="500" letter-spacing="-0.5" fill="{SUB}">티커 하나로 한 번에 확인해요</text>

  <rect x="80" y="812" width="920" height="116" rx="58" fill="url(#line)"/>
  <text x="540" y="884" text-anchor="middle" font-size="40" font-weight="700" letter-spacing="-0.5" fill="#FFFFFF">snapvestai.com</text>
  <text x="540" y="972" text-anchor="middle" font-size="27" font-weight="600" letter-spacing="-0.5" fill="{PURPLE}">로그인 없이 하루 5회 무료</text>

  <text x="80" y="1046" font-size="25" font-weight="600" fill="{DIM}">숫자는 코드가, 해석은 AI가.</text>
  <text x="1000" y="1046" text-anchor="end" font-size="27" font-weight="700" fill="url(#dom)">Snapvest</text>
</g>''', '마무리')


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    outdir = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "out")
    outdir.mkdir(parents=True, exist_ok=True)
    c = json.loads(pathlib.Path(cfg_path).read_text(encoding="utf-8"))

    files = {
        "1-cover.svg":        card1(c, "end"),      # 우측 정렬
        "1-cover-center.svg": card1(c, "middle"),   # 중간 정렬
        "2-company.svg": card2(c),
        "3-reason.svg":  card3(c),
        "4-chart.svg":   card4(c),
        "5-cta.svg":     card5(c),
    }
    for name, svg in files.items():
        (outdir / name).write_text(svg, encoding="utf-8")
        print(f"  ✓ {outdir/name}")


if __name__ == "__main__":
    main()
