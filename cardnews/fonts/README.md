# Pretendard

카드뉴스 렌더와 Canva 업로드에 쓰는 폰트. SIL Open Font License 1.1.
원본: https://github.com/orioncactus/pretendard

카드에서 실제로 쓰는 굵기 4개만 담았다.

| 파일 | weight | 쓰이는 곳 |
|---|---|---|
| `Pretendard-Black.otf` | 900 | 표지 종목명 |
| `Pretendard-Bold.otf` | 700 | 헤드라인 대부분 |
| `Pretendard-SemiBold.otf` | 600 | 지표 라벨 · 상태 문구 |
| `Pretendard-Medium.otf` | 500 | 본문 설명 |

## 로컬 렌더용 설치

`render.py` 는 시스템에 Pretendard 가 있어야 글자가 제대로 나온다.
컨테이너는 세션마다 초기화되므로 매번 다시 깔아야 한다.

```
mkdir -p ~/.fonts && cp cardnews/fonts/*.otf ~/.fonts/ && fc-cache -f
fc-list | grep -i pretendard      # 확인
```

## Canva 업로드용

Canva 에 Pretendard 가 없어서 `out/*.svg` 를 그대로 올리면 폰트가 치환되고
글자 폭이 달라져 줄이 밀린다. 이 4개를 먼저 등록하면 해결된다.

```
Canva → 브랜드 → 브랜드 키트 → 글꼴 → 글꼴 업로드
```

글꼴 업로드는 Canva Pro 기능이다. 무료 플랜이면
`svg_outline.py` 로 만든 패스 변환본(`svg-canva/`)을 쓰는 편이 낫다.
