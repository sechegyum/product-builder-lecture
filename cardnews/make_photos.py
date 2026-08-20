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
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = pathlib.Path(__file__).parent
SRC, OUT = HERE / "photos", HERE / "assets"
LAV = (239, 234, 252)          # #EFEAFC

JOBS = [                       # (원본, 폭, 높이, 결과)  — 높이는 generate.py 슬롯 규격
    ("moderna-logo.jpg", 1000, 340, "photo-company.jpg"),   # 2번 카드
    ("lab.jpg",          1000, 372, "photo-reason.jpg"),    # 3번 카드
]

CHIP = ("moderna-mark.jpg", "logo-chip.png")   # 1번 카드 표지 원형 로고 (config 의 logo)
CHIP_PX, CHIP_FILL = 240, 0.60                 # 캔버스 크기 · 마크가 차지할 가로 비율


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


def logo_chip(src, dst, size=CHIP_PX, fill=CHIP_FILL):
    """표지 원형 로고. 흰 배경을 라벤더로 치환해 카드 배경과 이어지게 만든다"""
    mark = trim(Image.open(src).convert("RGB"))

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


def build(src, w, h, dst, margin=22, rad=26):
    im = Image.open(src).convert("RGB")

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
    for name, w, h, out in JOBS:
        build(SRC / name, w, h, OUT / out)
    logo_chip(SRC / CHIP[0], OUT / CHIP[1])


if __name__ == "__main__":
    main()
