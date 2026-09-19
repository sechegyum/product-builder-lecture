# product-builder-lecture

## cardnews/ — 스냅베스트 카드뉴스

인스타그램 캐러셀 5장 세트를 만드는 생성기. **디자인 고정, 값만 교체.**

사용자가 **종목과 뉴스만** 주면 나머지 수치는 조사해서 채운다.
→ `.claude/skills/snapvest-cardnews/SKILL.md` 를 따를 것. (`/snapvest-cardnews`)

```
cardnews/
├── generate.py        디자인 코드. 수정 금지
├── make_photos.py     photos/ -> assets/ 규격 맞춤 + 표지 원형 로고
├── render.py          out/*.svg -> png/*.png (1080x1080, 헤드리스 크롬)
├── svg_outline.py     글자를 패스로 변환 (Canva 업로드용)
├── make_chart.py      candles -> 사진 슬롯용 일봉 차트
├── make_graphic.py    쓸 사진이 없을 때 브랜드 톤 추상 그래픽
├── fonts/             Pretendard 4종 (렌더 · Canva 업로드)
├── archive.py         회차 보관. 새 회차 시작 전에 먼저 실행
├── pack.py            회차를 dist/TICKER-날짜.zip 으로 묶음 (대표님 PC 로 보낼 것)
├── README.md          디자인 규칙 · config 필드 표 · 문구 원칙
├── PROMPT.md          요청 양식
├── SNS-TEMPLATE.md    인스타 캡션 · 쓰레드 체인 뼈대
│
├── config.json        이번 회차 값
├── SOURCES.md         이번 회차 수치 출처 + 미검증 항목
├── sns.md             이번 회차 글귀
├── photos/ assets/ out/ png/
└── archive/YYYY-MM-DD-TICKER/   지난 회차
```

### 손대면 안 되는 것

- `generate.py` 의 색상 상수 · 좌표 · 폰트 크기
- 5장 헤드라인 문형 (질문 → 배경 → 답 → 검증 → 답 안 준 질문)
- 결론·매수 권유 금지, 확인 안 된 값은 `자료 없음` 으로 노출

### 실행

```
cd cardnews
python3 archive.py                      # 이전 회차 보관
python3 make_photos.py                  # 사진 전처리
python3 generate.py config.json out     # SVG 5장
python3 render.py                       # PNG 5장
python3 pack.py                         # dist/TICKER-날짜.zip 으로 묶기
```

### 회차를 끝내면 zip 을 보낸다

카드가 다 나오면 `pack.py` 로 묶어 **파일로 보낸다.** 컨테이너는 대표님
컴퓨터가 아니라서 직접 저장해 드릴 수 없다 — 받아서 푸는 것이 유일한 길이다.
풀면 `SNOW/` 처럼 **티커 이름의 폴더 하나**가 나온다 (png · out · photos ·
assets · 글귀 전부 들어 있음).

낱개로 보내면 스무 개가 넘고 받는 쪽에서 폴더를 손으로 나눠 담아야 한다.

렌더에는 Pretendard 가 시스템 폰트로 필요하다. 컨테이너는 세션마다 초기화되므로
**`cardnews/fonts/` 의 OTF 4개를 먼저 설치**하고 시작한다.

```
mkdir -p ~/.fonts && cp cardnews/fonts/*.otf ~/.fonts/ && fc-cache -f
```

### 커밋

컨테이너는 세션이 끝나면 회수된다. **매 회차 커밋·푸시할 것.**
