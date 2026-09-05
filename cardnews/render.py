#!/usr/bin/env python3
"""
out/*.svg -> png/*.png (1080x1080)

Pretendard 가 설치된 환경에서 실행할 것. (SVG 를 그대로 올리면 폰트가 깨집니다)
    python3 render.py

    python3 render.py [입력폴더] [출력폴더]
"""
import pathlib, shutil, subprocess, sys
from PIL import Image

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
SIZE = 1080
PAD = 160                       # 헤드리스 크롬이 뷰포트에서 깎아먹는 높이 여유분
HERE = pathlib.Path(__file__).parent
SRC = HERE / (sys.argv[1] if len(sys.argv) > 1 else "out")
DST = HERE / (sys.argv[2] if len(sys.argv) > 2 else "png")
TMP = HERE / ".render"

SHELL = ('<!doctype html><meta charset="utf-8">'
         '<style>html,body{{margin:0;padding:0;background:#fff}}'
         'svg{{display:block;width:{s}px;height:{s}px}}</style>\n{svg}')


def main():
    if not pathlib.Path(CHROME).exists():
        sys.exit(f"크롬을 찾을 수 없습니다: {CHROME}")
    DST.mkdir(exist_ok=True); TMP.mkdir(exist_ok=True)
    for svg in sorted(SRC.glob("*.svg")):
        html = TMP / f"{svg.stem}.html"
        html.write_text(SHELL.format(s=SIZE, svg=svg.read_text(encoding="utf-8")),
                        encoding="utf-8")
        shot = TMP / f"{svg.stem}.png"
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                        "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={SIZE},{SIZE + PAD}",
                        f"--screenshot={shot}", f"file://{html}"],
                       check=True, capture_output=True)
        out = DST / f"{svg.stem}.png"
        Image.open(shot).convert("RGB").crop((0, 0, SIZE, SIZE)).save(out)
        print(f"  ✓ {out}")
    shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
