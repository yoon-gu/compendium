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

`papers-tex/**/*.aux,bbl,fls,log,xdv,...` 와 `build/` 는 `.gitignore`에 등록되어 있음. PDF는 `static/papers/`에 커밋.

## 커밋 정책

- **커밋은 사용자가 명시 요청할 때만**. 그 외에는 변경 사항만 보고하고 대기.
- 커밋 메시지 스타일: 짧은 한국어 동사구 (예: `수식 렌더링 수정: 인라인 KaTeX span 렌더링 추가`)

## 환경 메모

- macOS, MacTeX 2021 (`/Library/TeX/texbin/`)
- xelatex + kotex(`/usr/local/texlive/2021/.../cjk-ko/kotex.sty`)
- Nanum 폰트 — `~/Library/Fonts/`
- PDF 썸네일은 poppler(pdftotext) 없이 `qlmanage -t`로 생성 가능
