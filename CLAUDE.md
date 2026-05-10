# Compendium — Claude 작업 가이드

이 저장소는 관심 있는 글을 한국어로 번역해 모아 두는 Hugo 블로그입니다.

## 콘텐츠 구조

```
content/
├── notes/      # 짧게 요약·정리한 번역 글
└── papers/     # 논문 등 라인바이라인 한국어 번역 (긴 글)
```

- `notes/`: 블로그/위키/문서 같은 짧은 글의 한국어 요약 (마크다운만)
- `papers/`: 논문 레벨의 긴 번역. arxiv 논문은 아래 워크플로우로 LaTeX→PDF 빌드까지 함께 발행

**요약-논문 양방향 연결 규칙**: `papers/<slug>.md`를 작성하면 `notes/<slug>.md`에도 같은 슬러그로 짧은 요약본(1-2 화면 분량의 핵심 정리)을 함께 만들고, 두 글을 양방향 링크로 잇는다.

- `notes/<slug>.md`: 본문 끝 또는 상단에 "전문은 [한국어 번역본](/compendium/papers/<slug>/)에서" 식의 링크. arxiv 논문이면 한국어/원문 PDF 링크도 함께 노출
- `papers/<slug>.md`: 상단에 "짧은 요약은 [/notes/<slug>/](/compendium/notes/<slug>/)" 링크 한 줄
- 두 파일이 같은 슬러그를 공유해도 Hugo 섹션이 다르므로 URL은 각각 `/notes/<slug>/`와 `/papers/<slug>/`로 구분됨

빌드 산출물:
- `static/papers/<slug>.pdf` — 한국어 번역본 PDF
- `static/papers/<slug>-original.pdf` — arxiv 원문 PDF (arxiv 출처일 때만)

LaTeX 소스:
- `papers-tex/<slug>/` — 한국어 번역된 tex 소스 (chapters/, images/, sty/, bib, Makefile)

## arxiv 논문 번역 워크플로우

사용자가 arxiv 링크(예: `https://arxiv.org/abs/<id>`, `https://arxiv.org/pdf/<id>.pdf`)를 주면 다음 순서로 작업합니다.

### 1. 소스 받기

```bash
# e-print(.tex) 소스 다운로드 후 papers-tex/<slug>/에 추출
mkdir -p /tmp/<slug>-src && cd /tmp/<slug>-src
curl -sL "https://arxiv.org/e-print/<id>v<v>" -o src.tar.gz
tar xzf src.tar.gz
mkdir -p /Users/yoon-gu/repos/compendium/papers-tex/<slug>
cp -R . /Users/yoon-gu/repos/compendium/papers-tex/<slug>/

# 원문 PDF 다운로드
curl -sL "https://arxiv.org/pdf/<id>v<v>.pdf" \
  -o /Users/yoon-gu/repos/compendium/static/papers/<slug>-original.pdf
```

`<slug>`는 kebab-case로 짧게 (예: `pragma-revolut-foundation-model`).

### 2. main.tex에 한글 preamble 주입

`papers-tex/<slug>/main.tex` 적당한 위치(보통 documentclass 직후)에 다음 블록을 추가합니다.

```latex
% --- Korean translation support (xelatex + kotex) ---
\usepackage{kotex}
\usepackage{fontspec}
\setmainfont{NanumMyeongjo}[AutoFakeSlant=0.167]
\setsansfont{NanumGothic}[AutoFakeSlant=0.167]
\setmainhangulfont{NanumMyeongjo}[AutoFakeSlant=0.167]
\setsanshangulfont{NanumGothic}[AutoFakeSlant=0.167]
\setmonohangulfont{NanumGothicCoding}[AutoFakeSlant=0.167]
\setmonofont{NanumGothicCoding}[AutoFakeSlant=0.167]
\linespread{1.4}\selectfont
\renewcommand{\figurename}{그림}
\renewcommand{\tablename}{표}
\setlength{\parindent}{1.2em}
% --- end Korean support ---
```

그리고 `\title{}`, `\author{}` 푸터 등 표지 정보도 한국어로 다듬어 넣습니다 (원어 병기 가능).

폰트 의존성: macOS `~/Library/Fonts/`에 NanumMyeongjo, NanumGothic, NanumGothicCoding 설치 필요. 빌드는 항상 `xelatex`(kotex가 요구).

### 3. 챕터별 번역

`chapters/` 또는 `\input` 으로 들어오는 모든 본문 .tex를 라인바이라인으로 번역. **LaTeX 명령은 그대로 유지** — `\cite`, `\ref`, `\label`, math, environments(`figure`, `table`, `itemize` 등), `\textbf`, `\emph`, 커스텀 매크로(`\inR` 등) 모두 보존. 번역하는 것은 자연어 본문과 캡션/제목 텍스트만.

표·그림 캡션도 한국어로. 표 헤더 셀(예: `Task`, `Metric`)도 한국어로 다듬되, 약어/지표명(ROC-AUC, $F_1$, mAP, LoRA 등)은 영문 유지.

**전문용어 원문 병기 규칙**: 도메인 전문용어를 한국어로 옮길 때, **한 논문 안에서 첫 등장 1회**에 한해 괄호로 원문을 함께 표기한다. (LaTeX 다중 파일 논문이라면 전체 문서를 단위로, 마크다운은 한 파일이 단위.) 독자의 이해도와 영어 자료로의 연결성을 높이기 위함.

**범위(range) 표기**: 마크다운에서 `~`는 취소선(strikethrough) 마커로 해석될 수 있으므로 `1~2`처럼 한국어 범위 표기에 쓰지 않는다. 대신 `1-2`처럼 하이픈을 쓴다. LaTeX에서도 `~`는 비단절 공백이므로 범위에는 `--` (en dash) 또는 `-`를 쓴다.

**리스트 항목에 bold 남용 금지**: 번호/글머리 리스트의 모든 항목 머리에 `**...**:` 형태로 bold를 다는 것은 강조의 의미를 흐린다. 리스트 구조 자체가 시각적 위계를 주므로 항목 머리는 평문(plain text)으로 두고, bold는 *문장 안에서 진짜 강조하고 싶은* 특정 값/용어에만 쓴다. (예: 항목 머리는 평문, 항목 안의 수치 한두 개는 bold 가능 — 단 모두 bold면 의미 없음.)

- 적용 대상: 분야 특화 용어, 모델/방법 이름, 학습 패러다임 (예: `트랜스포머(Transformer)`, `사전학습(pre-training)`, `파인튜닝(fine-tuning)`, `자기지도(self-supervised)`, `다운스트림 과제(downstream task)`, `질의응답(question answering, QA)`)
- 예외: 이미 영문 그대로 쓰는 약어/모델명/지표 (BERT, GPT, LoRA, ROC-AUC 등), 일반어휘에 가까운 단어 (모델, 데이터, 학습 등)
- 같은 파일에서 두 번째부터는 괄호 없이 한국어만
- 약어가 있는 용어는 약어까지 함께 표기 (예: `자연어 추론(natural language inference, NLI)`)
- 한국어 표기가 정착되지 않은 용어는 원문 그대로 두는 것도 OK

이미 `content/papers/<slug>.md`에 손번역된 마크다운이 있다면 용어 일관성을 위해 참고.

### 4. 빌드 + 발행

```bash
cd papers-tex/<slug>
latexmk -xelatex -interaction=nonstopmode -outdir=build main.tex
cp build/main.pdf ../../static/papers/<slug>.pdf
```

또는 PRAGMA 디렉토리에 있는 Makefile을 복사해 사용 (`make publish`).

검증: `qlmanage -t -s 1400 -o /tmp /path/to/pdf` 로 첫 페이지 썸네일 추출 후 Read 도구로 확인.

### 5. 마크다운 포스트 작성

`content/papers/<slug>.md` 생성 (이미 요약본이 있으면 PDF 링크만 추가).

frontmatter 예시:

```yaml
---
title: "한국어 제목"
date: YYYY-MM-DD
draft: false
math: true
source_url: "https://arxiv.org/html/<id>v<v>"
author: "저자 명단 (소속)"
tags: ["AI", "...", "..."]
summary: "1-3문장 요약"
---
```

본문 상단에 출처 인용과 PDF 링크 블록을 둡니다.

```markdown
> **원문:** [영문 제목](arxiv URL) — 저자, 소속, arXiv <id>v<v>
>
> 아래 글은 원문 논문의 순서와 서술을 최대한 따라가며 한국어로 옮긴 것이다.

**PDF 다운로드**

- [한국어 번역본 PDF](/compendium/papers/<slug>.pdf) — 원문 레이아웃을 보존한 한국어판
- [arxiv 원문 PDF](/compendium/papers/<slug>-original.pdf)
```

이어서 본문 라인바이라인 한국어 번역 (마크다운; LaTeX 수식은 `$...$` / `$$...$$`로).

## 비-arxiv 출처

arxiv가 아닌 출처(블로그, transformer-circuits.pub 등)는 보통 LaTeX 소스가 없으므로 **마크다운 번역만** 합니다. PDF 빌드 단계 없음.

## Hugo 빌드/배포

- 로컬: `hugo server` (시스템에 hugo가 없으면 GitHub Actions가 push 시 자동 빌드)
- 배포: master 브랜치 push 시 `.github/workflows/deploy.yml`이 GitHub Pages에 게시
- 사이트 베이스 URL: `https://yoon-gu.github.io/compendium/` — 마크다운에서 PDF 링크는 `/compendium/papers/...` 로 시작

## 메뉴/섹션 설정

`hugo.toml`:
- `mainSections = ["notes", "papers"]` — 홈에서 두 섹션 모두 노출
- 메뉴: 요약(notes), 논문(papers), 아카이브, 태그, 검색

## 빌드 산출물 .gitignore

`papers-tex/**/*.aux,fls,log,xdv,...` 와 `build/` 는 `.gitignore`에 등록되어 있음. **단, `.bbl`은 제외하지 않는다** — arxiv 소스는 `.bib` 없이 사전 생성된 `.bbl`만 동봉하는 경우가 많아 빌드에 필요. PDF는 `static/papers/`에 커밋.

## 커밋 정책

- **작업 단위가 일단락되면 기본적으로 커밋 + `git push origin master` 까지 진행한다.** 사용자가 별도로 "커밋하지 말고 보여만 달라"고 하지 않는 한 푸시까지 한다 (사용자 사전 승인됨).
- 푸시 전 점검: `git status`로 의도치 않은 파일(`.DS_Store` 등)이 포함되지 않았는지 확인. 민감 정보 가능성 있는 파일은 스테이징 제외.
- 커밋 메시지 스타일: 짧은 한국어 동사구 (예: `수식 렌더링 수정: 인라인 KaTeX span 렌더링 추가`)
- `master`에 직접 푸시. 강제 푸시(`--force`), `git reset --hard`, 훅 우회(`--no-verify`)는 사용자 명시 요청 시에만.

## 환경 메모

- macOS, MacTeX 2021 (`/Library/TeX/texbin/`)
- xelatex + kotex(`/usr/local/texlive/2021/.../cjk-ko/kotex.sty`)
- Nanum 폰트 — `~/Library/Fonts/`
- PDF 썸네일은 poppler(pdftotext) 없이 `qlmanage -t`로 생성 가능
