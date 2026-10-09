#!/usr/bin/env python3
"""
이번 회차를 티커 이름의 폴더 하나로 묶는다. 받아서 풀면 끝이다.

    python3 pack.py            # dist/SNOW-2026-09-03.zip

압축을 풀면 이렇게 나온다.

    SNOW/
    ├── png/      카드 5장 (1080x1080). 인스타에 올릴 것
    ├── out/      같은 카드의 SVG. 캔바에 올리거나 글자 고칠 때
    ├── photos/   받은 원본 사진
    ├── assets/   규격에 맞춘 사진 (카드에 실제로 박힌 것)
    ├── blog.txt  블로그 본문 (그대로 복사)
    ├── sns.md    인스타 · 쓰레드 · 토스 글귀
    ├── SOURCES.md  수치 출처와 검산
    └── config.json 이 회차의 값

**왜 zip 하나로 묶나.** 파일을 낱개로 보내면 스무 개가 넘고, 받는 쪽에서
폴더를 손으로 만들어 나눠 담아야 한다. 한 번 받아 풀면 폴더째 자리를
잡는 편이 손이 덜 간다.

폴더 이름을 티커로 두는 이유도 같다. 날짜가 앞에 오면 같은 종목을 다시
다룰 때 두 회차가 목록에서 떨어져 앉는다.
"""
import json
import pathlib
import shutil
import sys
import zipfile

HERE = pathlib.Path(__file__).parent
DIST = HERE / "dist"

# 넣을 것. 없으면 조용히 건너뛴다 — 회차마다 사진 수가 다르다.
DIRS = ["png", "out", "photos", "assets"]
FILES = ["blog.txt", "blog.md", "sns.md", "SOURCES.md", "config.json"]


def main() -> None:
    cfg_path = HERE / "config.json"
    if not cfg_path.exists():
        sys.exit("config.json 이 없습니다. 묶을 회차가 없어요.")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    ticker = str(cfg["ticker"]).strip()
    month, day = str(cfg["date"]).split(".")      # date 는 "09.03" 형식
    stamp = f"{cfg.get('year', 2026)}-{month}-{day}"

    DIST.mkdir(exist_ok=True)
    out = DIST / f"{ticker}-{stamp}.zip"

    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for d in DIRS:
            src = HERE / d
            if not src.is_dir():
                continue
            for f in sorted(src.rglob("*")):
                if f.is_file() and not f.name.startswith("."):
                    z.write(f, f"{ticker}/{d}/{f.relative_to(src)}")
                    n += 1
        for name in FILES:
            f = HERE / name
            if f.is_file():
                z.write(f, f"{ticker}/{name}")
                n += 1

    size = out.stat().st_size / 1e6
    print(f"  {out.relative_to(HERE)}  ({n}개 파일 · {size:.1f}MB)")
    print(f"  풀면 {ticker}/ 폴더 하나가 나옵니다.")


if __name__ == "__main__":
    main()
