# Compendium

관심 있는 글을 한국어로 번역해 모아 두는 Hugo 블로그입니다.

👉 https://yoon-gu.github.io/compendium/

## 구조

| 디렉토리 | 내용 |
|---|---|
| `content/notes/` | 블로그·문서 등 짧은 글의 한국어 요약 |
| `content/papers/` | 논문 등 긴 글의 라인바이라인 한국어 번역 |
| `papers-tex/<slug>/` | 한국어로 번역한 arxiv LaTeX 소스 |
| `static/papers/` | 빌드된 한국어 PDF와 arxiv 원문 PDF |

논문 번역은 `papers/<slug>.md`와 `notes/<slug>.md`를 같은 슬러그로 짝지어 만들고 서로 링크합니다.

## 사용법

Claude Code에게 URL을 주면:

1. 원문을 가져와 한국어로 번역
2. arxiv 논문이면 e-print 소스를 받아 LaTeX까지 번역 → xelatex + kotex로 PDF 빌드
3. Hugo 포스트로 작성 후 커밋 & 푸시

자세한 작업 규칙은 [CLAUDE.md](CLAUDE.md) 참고.

## 기술 스택

- **정적 사이트**: [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) (서브모듈)
- **배포**: master 푸시 시 GitHub Actions → GitHub Pages
- **PDF 빌드**: MacTeX(xelatex) + kotex + Nanum 폰트
- **번역**: Claude Code
