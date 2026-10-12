#!/usr/bin/env python3
"""
현재 회차를 archive/ 로 옮겨 보관한다. **새 회차를 시작하기 전에 먼저 실행할 것.**

    python3 archive.py

config.json 의 date · ticker 로 폴더 이름을 만든다 → archive/2026-08-20-MRNA/
템플릿 파일(generate.py, render.py, make_photos.py, README.md ...)은 건드리지 않는다.
"""
import json, pathlib, shutil, sys

HERE = pathlib.Path(__file__).parent
MOVE = ["config.json", "SOURCES.md", "sns.md", "blog.md", "blog.txt",
        "photos", "assets", "out", "png"]


def main():
    cfg_path = HERE / "config.json"
    if not cfg_path.exists():
        sys.exit("config.json 이 없습니다. 보관할 회차가 없어요.")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    month, day = cfg["date"].split(".")          # date 는 "08.20" 형식
    dest = HERE / "archive" / f"{cfg.get('year', 2026)}-{month}-{day}-{cfg['ticker']}"
    if dest.exists():
        sys.exit(f"이미 보관된 회차입니다: {dest}")
    dest.mkdir(parents=True)

    for name in MOVE:
        src = HERE / name
        if not src.exists():
            continue
        shutil.move(str(src), str(dest / name))
        print(f"  → {dest.name}/{name}")

    print(f"\n보관 완료: {dest}")
    print("이제 새 회차의 config.json 과 photos/ 를 만들면 됩니다.")


if __name__ == "__main__":
    main()
