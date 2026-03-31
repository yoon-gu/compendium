# Compendium

관심 있는 글을 스크래핑하고 한국어로 번역하여 기록하는 블로그입니다.

## 사용법

Claude Code에게 URL을 주면:
1. 원문을 스크래핑
2. 한국어로 번역
3. Hugo 포스트로 작성 후 커밋 & 푸시

GitHub Actions가 자동으로 Hugo 빌드 → GitHub Pages 배포합니다.

## 기술 스택

- **정적 사이트**: [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **배포**: GitHub Pages (GitHub Actions)
- **스크래핑 & 번역**: Claude Code
