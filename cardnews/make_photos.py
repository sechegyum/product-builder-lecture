#!/usr/bin/env python3
"""
photos/ 원본 사진 -> assets/ 카드 슬롯 규격 이미지

카드 슬롯이 1000px 로 넓어서 작은 원본을 그대로 늘리면 뭉개진다.
그래서 같은 사진을 두 번 쓴다.
  · 배경 = 꽉 채워 자른 뒤 강하게 블러 + 라벤더 블렌드
  · 전경 = 세로에만 맞춰 확대(배율 최소) + 언샵 + 둥근 모서리 + 그림자

    python3 make_photos.py
"""
import pathlib
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).parent
SRC, OUT = HERE / "photos", HERE / "assets"
LAV = (239, 234, 252)          # #EFEAFC

# (원본, 폭, 높이, 결과, 크롭)  — 높이는 generate.py 슬롯 규격
# 크롭은 원본 픽셀 기준 (left, top, right, bottom). 안 쓰면 None.
# 스톡 이미지에 오탈자·워터마크·엉뚱한 축 라벨이 박혀 있으면 여기서 잘라낸다.
JOBS = [
    ("bdrx-news.jpg", 1000, 290, "photo-company.jpg", (0,  0, 1206, 330)),  # 2번 · MTX110 기사 헤드라인
    ("bdrx-ced.webp", 1000, 372, "photo-reason.jpg",  (0, 40,  850, 430)),  # 3번 · CED 카테터 전달
    # 기사 사진을 3번(급등 이유)에서 2번(회사 소개)으로 옮겼다. 기사 날짜가
    # 2024년 10월이고 내용도 MTX110(뇌종양)이라, 2026년 9월 FAP 3상을 설명하는
    # 3번에 두면 그게 이번 뉴스로 읽힌다. 파이프라인 소개인 2번이 제자리다.
    # 기사는 헤드라인만 남겨 비를 3.65 로 올렸다 (슬롯 3.45).
    # 4번 · 일봉 캡처 자리. 봉 데이터가 있으면 안 쓴다.
]

# 1번 카드 표지 원형 로고 (config 의 logo). 셋 중 하나로 쓴다.
#   {"src": 파일명}                  로고 원본을 그대로
#   {"src": 파일명, "crop": (l,t,r,b)}  로고에서 심볼만 잘라서
#   {"text": "R"}                    로고가 없는 티커용 레터마크
#   {"src": 파일명, "bleed": True}     로고가 제 배경을 갖고 있을 때 (아래)
# SPAC 처럼 쓸 로고가 아예 없으면 None 으로 두면 빈 원이 나온다.
#
# bleed 를 언제 쓰나 — 로고가 흰 바탕에 마크만 있는 형태면 기본값이 맞다.
# 여백을 잘라내고 흰색을 라벤더로 갈아 카드 배경에 녹인다. 그런데 OLB 처럼
# **색 배경이 통째로 로고인 경우**(빨간 사각형에 흰 글자) 그 처리를 하면
# 흰 글자가 라벤더로 바뀌어 브랜드가 망가진다. bleed 는 자르지도 물들이지도
# 않고 정사각형으로만 맞춰, generate.py 의 원형 클립이 그대로 원을 채운다.
CHIP = {"src": "logo.png", "out": "logo-chip.png", "fill": 0.85}
#   이 로고는 흰 바탕에 마크만 있는 형태라 bleed 를 쓰지 않는다.
#   점선 원이 마크 자체라 원형 클립과 겹쳐도 모서리가 비어 안 잘린다.
#   fill — 마크가 원 안에서 차지할 가로 비율. 가로로 넓은 마크는 키워야 읽힌다
CHIP_PX, CHIP_FILL = 240, 0.60                 # 캔버스 크기 · 마크가 차지할 가로 비율
PURPLE = (139, 91, 214)                        # #8B5BD6
FONT_BOLD = "/root/.fonts/Pretendard-Bold.otf"


def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def rounded(im, rad):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], rad, fill=255)
    im = im.convert("RGBA")
    im.putalpha(mask)
    return im


def trim(im, thr=238):
    """흰 여백 잘라내기 — 파일마다 다른 로고 여백을 없애고 광학 크기를 맞춘다"""
    px, (w, h) = im.load(), im.size
    box = [w, h, 0, 0]
    for y in range(h):
        for x in range(w):
            if min(px[x, y]) < thr:
                box = [min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)]
    return im.crop((box[0], box[1], box[2] + 1, box[3] + 1))


def lettermark(text, dst, size=CHIP_PX):
    """로고가 없는 티커용. 토스처럼 첫 글자만 원 안에 박는다"""
    chip = Image.new("RGB", (size, size), LAV)
    d = ImageDraw.Draw(chip)
    f = ImageFont.truetype(FONT_BOLD, round(size * 0.52))
    l, t_, r, b = d.textbbox((0, 0), text, font=f)
    d.text(((size - (r - l)) / 2 - l, (size - (b - t_)) / 2 - t_), text, font=f, fill=PURPLE)
    chip.save(dst, "PNG")
    print(f"  ✓ {dst}  레터마크 '{text}'")


def logo_bleed(src, dst, size=CHIP_PX, crop=None):
    """제 배경을 갖고 있는 로고. 정사각형으로만 맞추고 색은 손대지 않는다"""
    im = Image.open(src).convert("RGB")
    if crop:
        im = im.crop(crop)
    side = min(im.size)
    x, y = (im.width - side) // 2, (im.height - side) // 2
    im = im.crop((x, y, x + side, y + side)).resize((size, size), Image.LANCZOS)
    im.save(dst, "PNG")
    print(f"  ✓ {dst}  {size}×{size}  (풀블리드 · 색 보정 없음)")


def logo_chip(src, dst, size=CHIP_PX, fill=CHIP_FILL, crop=None):
    """표지 원형 로고. 흰 배경을 라벤더로 치환해 카드 배경과 이어지게 만든다"""
    if not pathlib.Path(src).exists():
        print(f"  · {pathlib.Path(src).name} 없음 → 표지 로고는 빈 원으로 둡니다")
        return
    mark = Image.open(src).convert("RGB")
    if crop:
        mark = mark.crop(crop)
    mark = trim(mark)

    # 흰색일수록 라벤더로 — 로고 색은 그대로 두고 여백만 갈아끼운다
    shift = [l - 255 for l in LAV]
    px = mark.load()
    for y in range(mark.height):
        for x in range(mark.width):
            r, g, b = px[x, y]
            k = min(r, g, b) / 255
            px[x, y] = tuple(max(0, min(255, round(v + s * k)))
                             for v, s in zip((r, g, b), shift))

    mw = round(size * fill)
    mh = round(mark.height * mw / mark.width)
    mark = mark.resize((mw, mh), Image.LANCZOS)

    chip = Image.new("RGB", (size, size), LAV)
    chip.paste(mark, ((size - mw) // 2, (size - mh) // 2))
    chip.save(dst, "PNG")
    print(f"  ✓ {dst}  {size}×{size}  (마크 {mw}×{mh})")


def build(src, w, h, dst, crop=None, margin=22, rad=26):
    im = Image.open(src).convert("RGB")
    if crop:
        im = im.crop(crop)

    bg = cover(im, w, h).filter(ImageFilter.GaussianBlur(30))
    bg = Image.blend(bg, Image.new("RGB", (w, h), LAV), 0.52)
    bg = ImageEnhance.Brightness(bg).enhance(1.04)

    fh = h - margin * 2
    fw = round(im.width * fh / im.height)
    fg = rounded(im.resize((fw, fh), Image.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=2.2, percent=115, threshold=3)), rad)
    x, y = (w - fw) // 2, margin

    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [x, y + 6, x + fw, y + fh + 6], rad, fill=(120, 100, 165, 62))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))

    canvas = bg.convert("RGBA")
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(fg, (x, y))
    canvas.convert("RGB").save(dst, "JPEG", quality=94, subsampling=0)
    print(f"  ✓ {dst}  {w}×{h}  (원본 {im.width}×{im.height} → 전경 {fw}×{fh})")


def main():
    OUT.mkdir(exist_ok=True)
    for name, w, h, out, crop in JOBS:
        build(SRC / name, w, h, OUT / out, crop)
    if CHIP is None:
        print("  · 표지 로고 설정 없음 → 빈 원")
    elif "text" in CHIP:
        lettermark(CHIP["text"], OUT / CHIP["out"])
    elif CHIP.get("bleed"):
        logo_bleed(SRC / CHIP["src"], OUT / CHIP["out"], crop=CHIP.get("crop"))
    else:
        logo_chip(SRC / CHIP["src"], OUT / CHIP["out"],
                  fill=CHIP.get("fill", CHIP_FILL), crop=CHIP.get("crop"))


if __name__ == "__main__":
    main()
