# NotebookLM 오디오 오버뷰 만들기 — 시장 데이터 회차

## 1. 소스 (노트북에 넣을 것)

- 원문 웹사이트: https://blog.janestreet.com/can-you-use-autoregressive-diffusion-to-generate-market-data/
- 한국어 정리 노트: https://yoon-gu.github.io/compendium/notes/autoregressive-diffusion-market-data/
  (또는 `content/notes/autoregressive-diffusion-market-data.md` 파일을 그대로 올린다)

## 2. 설정

- 형식: 심층 분석(Deep Dive) · 길이: 기본 · 언어: 한국어

## 3. 맞춤 지시문 (붙여 넣기)

```
한국어로, 데이터 과학을 아는 직장인 청취자를 대상으로 대화해 주세요.
흐름: ① 시장 데이터는 영상처럼 연속인가 텍스트처럼 이산인가라는 질문 ② 호가창·BBO 같은 용어를 쉽게 풀기
③ DDPM식 노이즈 예측이 발산한 이유(1/√ᾱ로 나누면 오차가 부풀려짐)와 flow matching으로 바꾼 결과
④ 한 점에 몰린 확률(0초 간격, 호가 변화 0)을 20개 범주로 떼어 낸 방법과 그 한계
⑤ atom smoothing ⑥ 판별기 AUC 0.992→0.758의 의미(낮을수록 생성기에 좋음) ⑦ 아직 실전 생성기는 아니라는 한계.
원문에 없는 수치나 주장은 만들지 마세요. 판별기 범례(smoothed, newrep)의 정확한 설정은 원문에 없다고 말해 주세요.
카드 결제 금액이 정액에 몰리는 것 같은 금융 데이터 예시를 하나 곁들여도 좋습니다.
```

## 4. 받은 다음

- 오디오를 내려받아 `video/autoregressive-diffusion-market-data/work/overview.m4a` 로 둔다(파일 이름만 알려 줘도 된다).
- 그다음은 Claude가 한다: 받아쓰기로 대화 시각을 잡고 → 화면마다 `@분:초` 를 단 대본(`script-overview.md`)을 쓰고 →
  기존 그림·애니메이션을 대화에 맞춰 다시 배치하고 → `build.py --audio=work/overview.m4a` 로 굽는다(크레딧 0).
