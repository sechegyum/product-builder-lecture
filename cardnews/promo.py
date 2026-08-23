#!/usr/bin/env python3
"""
스냅베스트 서비스 소개 카드 5장 (1080x1080)

종목 카드뉴스(generate.py)와 같은 디자인 토큰을 쓰되 레이아웃만 다르다.
generate.py 는 건드리지 않는다.

    python3 promo.py promo.json promo-out
"""
import json, pathlib, sys

from generate import (INK, SUB, FAINT, DIM, ACCENT, PURPLE, UP, LINE_SOFT,
                      LAV, FONT, DEFS, esc, hdr, dom, wrap)


def bar(x, y, w=220, h=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h//2}" fill="url(#line)"/>'


# ── 1. 훅 ──────────────────────────────────────────
def card1(c):
    a = c["hook"]
    return wrap(f'''{DEFS}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="342" font-size="82" font-weight="700" letter-spacing="-3" fill="{INK}">{esc(a["line1"])}</text>
  <text x="80" y="442" font-size="82" font-weight="700" letter-spacing="-3" fill="{INK}">{esc(a["line2"])}</text>
  <text x="80" y="542" font-size="82" font-weight="700" letter-spacing="-3" fill="{ACCENT}">{esc(a["line3"])}</text>
  {bar(80, 596, 240, 14)}

  <rect x="80" y="664" width="920" height="336" rx="52" fill="#FFFFFF"/>
  <circle cx="176" cy="760" r="40" fill="url(#line)"/>
  <text x="176" y="774" text-anchor="middle" font-size="38" fill="#FFFFFF">✦</text>
  <text x="244" y="752" font-size="32" font-weight="700" letter-spacing="-1" fill="{INK}">Snapvest</text>
  <text x="244" y="794" font-size="23" font-weight="600" letter-spacing="0.5" fill="{FAINT}">snapvestai.com</text>
  <text x="944" y="752" text-anchor="end" font-size="40" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(a["badge"])}</text>
  <text x="944" y="794" text-anchor="end" font-size="26" font-weight="700" fill="{UP}">{esc(a["badge_sub"])}</text>
  <line x1="136" y1="832" x2="944" y2="832" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="136" y="890" font-size="27" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(a["fact1"])}</text>
  <text x="136" y="932" font-size="27" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(a["fact2"])}</text>

  <text x="80" y="1046" font-size="27" font-weight="700" letter-spacing="-0.5" fill="{DIM}">밀어서 보기 →</text>
  {dom(1046)}
</g>''', '스냅베스트 · 표지')


# ── 2. 어떤 서비스 ─────────────────────────────────
def card2(c):
    a = c["what"]
    rows = "".join(
        f'  <rect x="140" y="{452 + i*72}" width="800" height="56" rx="18" fill="{LAV}"/>\n'
        f'  <circle cx="176" cy="{480 + i*72}" r="7" fill="url(#line)"/>\n'
        f'  <text x="204" y="{490 + i*72}" font-size="25" font-weight="600" fill="{SUB}">{esc(t)}</text>\n'
        for i, t in enumerate(a["rows"][:3]))
    return wrap(f'''{DEFS}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="222" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">스냅베스트는 <tspan fill="{ACCENT}">뭘 하는 곳</tspan>일까?</text>
  {bar(80, 248)}

  <rect x="80" y="300" width="920" height="400" rx="52" fill="#FFFFFF"/>
  <rect x="140" y="356" width="800" height="72" rx="24" fill="{LAV}"/>
  <text x="176" y="402" font-size="28" fill="{DIM}">⌕</text>
  <text x="222" y="402" font-size="30" font-weight="700" letter-spacing="1" fill="{INK}">{esc(a["query"])}</text>
  <text x="904" y="402" text-anchor="end" font-size="25" font-weight="700" fill="{ACCENT}">{esc(a["query_hint"])}</text>
{rows}
  <text x="80" y="790" font-size="38" font-weight="700" letter-spacing="-1.5" fill="{INK}">{esc(a["lead1"])}</text>
  <text x="80" y="840" font-size="38" font-weight="700" letter-spacing="-1.5" fill="{INK}">{esc(a["lead2"])}</text>
  <text x="80" y="894" font-size="27" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(a["sub"])}</text>

  <rect x="80" y="936" width="920" height="112" rx="46" fill="#FFFFFF"/>
  <text x="233" y="982" text-anchor="middle" font-size="22" font-weight="600" fill="{FAINT}">지원 시장</text>
  <text x="233" y="1022" text-anchor="middle" font-size="32" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(a["m1"])}</text>
  <line x1="387" y1="962" x2="387" y2="1022" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="540" y="982" text-anchor="middle" font-size="22" font-weight="600" fill="{FAINT}">무료 조회</text>
  <text x="540" y="1022" text-anchor="middle" font-size="32" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(a["m2"])}</text>
  <line x1="693" y1="962" x2="693" y2="1022" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="847" y="982" text-anchor="middle" font-size="22" font-weight="600" fill="{FAINT}">가입</text>
  <text x="847" y="1022" text-anchor="middle" font-size="32" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(a["m3"])}</text>
</g>''', '스냅베스트 · 어떤 서비스')


# ── 3. 무엇이 나오나 ───────────────────────────────
def card3(c):
    a = c["shows"]
    items = ""
    for i, (t, s) in enumerate(a["items"][:6]):
        col, row = i % 2, i // 2
        x, y = 80 + col * 470, 330 + row * 210
        items += (f'  <rect x="{x}" y="{y}" width="450" height="182" rx="40" fill="#FFFFFF"/>\n'
                  f'  <circle cx="{x+58}" cy="{y+58}" r="16" fill="url(#line)"/>\n'
                  f'  <text x="{x+38}" y="{y+118}" font-size="29" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(t)}</text>\n'
                  f'  <text x="{x+38}" y="{y+156}" font-size="22" font-weight="500" fill="{FAINT}">{esc(s)}</text>\n')
    return wrap(f'''{DEFS}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="222" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">티커 하나에 <tspan fill="{ACCENT}">이게 다</tspan> 나와요</text>
  {bar(80, 248)}
{items}
  <text x="80" y="1046" font-size="25" font-weight="600" fill="{DIM}">{esc(a["note"])}</text>
  {dom(1046)}
</g>''', '스냅베스트 · 무엇이 나오나')


# ── 4. 어떻게 쓰나 ─────────────────────────────────
def card4(c):
    a = c["how"]
    steps = ""
    for i, (t, s) in enumerate(a["steps"][:3]):
        y = 310 + i * 210
        steps += (f'  <rect x="80" y="{y}" width="920" height="182" rx="44" fill="#FFFFFF"/>\n'
                  f'  <circle cx="{170}" cy="{y+91}" r="44" fill="url(#line)"/>\n'
                  f'  <text x="170" y="{y+106}" text-anchor="middle" font-size="42" font-weight="700" fill="#FFFFFF">{i+1}</text>\n'
                  f'  <text x="248" y="{y+80}" font-size="34" font-weight="700" letter-spacing="-1.2" fill="{INK}">{esc(t)}</text>\n'
                  f'  <text x="248" y="{y+126}" font-size="25" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(s)}</text>\n')
    return wrap(f'''{DEFS}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="222" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}"><tspan fill="{ACCENT}">어떻게</tspan> 쓰면 될까?</text>
  {bar(80, 248)}
{steps}
  <text x="80" y="1000" font-size="27" font-weight="700" letter-spacing="-0.5" fill="{PURPLE}">{esc(a["tip"])}</text>
  <text x="80" y="1046" font-size="25" font-weight="600" fill="{DIM}">{esc(a["note"])}</text>
  {dom(1046)}
</g>''', '스냅베스트 · 어떻게 쓰나')


# ── 5. 마무리 ──────────────────────────────────────
def card5(c):
    a = c["cta"]
    items = "".join(
        f'  <text x="146" y="{508 + i*62}" font-size="30" font-weight="700" letter-spacing="-0.8" fill="{INK}">{esc(t)}</text>\n'
        for i, t in enumerate(a["items"][:3]))
    return wrap(f'''{DEFS}
<g {FONT}>
{hdr(c["date"])}
  <text x="80" y="252" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}">{esc(a["line1"])}</text>
  <text x="80" y="330" font-size="60" font-weight="700" letter-spacing="-2.5" fill="{INK}"><tspan fill="{ACCENT}">{esc(a["line2_hi"])}</tspan>{esc(a["line2"])}</text>
  {bar(80, 356)}

  <rect x="80" y="428" width="920" height="330" rx="52" fill="#FFFFFF"/>
{items}  <line x1="146" y1="670" x2="934" y2="670" stroke="{LINE_SOFT}" stroke-width="3"/>
  <text x="146" y="722" font-size="28" font-weight="500" letter-spacing="-0.5" fill="{SUB}">{esc(a["sub"])}</text>

  <rect x="80" y="812" width="920" height="116" rx="58" fill="url(#line)"/>
  <text x="540" y="884" text-anchor="middle" font-size="40" font-weight="700" letter-spacing="-0.5" fill="#FFFFFF">snapvestai.com</text>
  <text x="540" y="972" text-anchor="middle" font-size="27" font-weight="600" letter-spacing="-0.5" fill="{PURPLE}">{esc(a["free"])}</text>

  <text x="80" y="1046" font-size="25" font-weight="600" fill="{DIM}">숫자는 코드가, 해석은 AI가.</text>
  <text x="1000" y="1046" text-anchor="end" font-size="27" font-weight="700" fill="url(#dom)">Snapvest</text>
</g>''', '스냅베스트 · 마무리')


def main():
    cfg = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "promo.json")
    outdir = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "promo-out")
    outdir.mkdir(parents=True, exist_ok=True)
    c = json.loads(cfg.read_text(encoding="utf-8"))
    for name, svg in {"1-hook.svg": card1(c), "2-what.svg": card2(c),
                      "3-shows.svg": card3(c), "4-how.svg": card4(c),
                      "5-cta.svg": card5(c)}.items():
        (outdir / name).write_text(svg, encoding="utf-8")
        print(f"  ✓ {outdir/name}")


if __name__ == "__main__":
    main()
