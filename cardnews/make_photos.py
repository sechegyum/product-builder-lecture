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


if __name__ == "__main__":
    main()
