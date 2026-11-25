# 듣는편람 모션 그래픽 (Remotion)

회차별 핵심 대목 애니메이션을 Remotion 컴포지션으로 만든다. 컴포지션은 `src/<회차>/`, 공용 부품(숲 톤 팔레트·나눔고딕·언급 시각 등장)은 `src/lib/ui.tsx`.

- 클립은 1776x1000, 25fps. 길이와 등장 시각은 `<회차>/figures/<이름>-timing.json`(`timing.py`가 whisper로 씀)을 `--props`로 받는다.
- 굽기: `sh ../<회차>/figures/render.sh` → `../<회차>/figures/<이름>.mp4` → `python3 ../build.py <회차>`.
- 미리 보기: `npx remotion studio`
- 폰트: 루트 `.gitignore`가 `public/`을 막으므로 새로 받은 뒤 `cp ~/Library/Fonts/NanumGothic-{Regular,Bold,ExtraBold}.ttf public/fonts/`.
