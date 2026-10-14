시장 데이터는 연속이면서 이산이다, 자기회귀 확산으로 호가창 생성하기 (Jane Street)
태그: Jane Street, 제인 스트리트, 제인스트리트, 자기회귀 확산, 확산 모델, 디퓨전 모델, 플로우 매칭, 자기회귀 모델, 시장 데이터 생성, 호가창, 오더북, 주식 데이터, 금융 데이터, 퀀트, 퀀트 트레이딩, 알고리즘 트레이딩, 시계열 생성, 합성 데이터, 분위수 변환, 영과잉 모형, 판별기, AI 논문, James Somers, Kavish, autoregressive diffusion, diffusion model, flow matching, rectified flow, DDPM, DDIM, atom smoothing, market data, order book, limit order book, synthetic data, quant, 듣는편람

확산 모델로 주식 호가창을 통째로 지어낼 수 있을까요? 퀀트 트레이딩 회사 Jane Street의 여름 인턴이 미국 주식 4년치로 도전했고, 진짜 난관은 "시장 데이터는 연속이면서 이산이다"라는 점이었습니다.

Jane Street 블로그 글 "Can you use autoregressive diffusion to generate market data?"를 14장면으로 풀어 읽습니다. 호가창과 BBO, 확산 모델이 무엇인지부터 짚고, 이벤트를 하나씩 만들어 이어 붙이는 자기회귀 확산 구조, DDPM의 노이즈 예측이 왜 초반에 폭발했는지(예시 값으로 계산), 곧은 길로 가는 flow matching, 0초 간격과 정확히 0인 호가 변화처럼 한 점에 몰린 확률을 20개 범주로 떼어 낸 방법과 atom smoothing으로 폈다가 다시 접는 방법, 그리고 total variation과 판별기 AUC로 본 결과와 롤아웃의 한계까지 다룹니다. 애니메이션 세 편으로 궤적·자기회귀 생성·atom smoothing을 보여 드립니다.

이런 분께 맞습니다
- 확산 모델이나 flow matching을 표 형식·시계열 데이터에 써 보려는 ML 엔지니어·데이터 사이언티스트
- 호가창이나 결제 데이터처럼 0과 정액에 확률이 몰린 금융 데이터를 다루는 분
- 퀀트 회사가 생성 모델을 어떻게 연구하는지 궁금한 분

{챕터}

원문(영어): https://blog.janestreet.com/can-you-use-autoregressive-diffusion-to-generate-market-data/
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/autoregressive-diffusion-market-data/
함께 보기, 수학 공식을 버린 넷플릭스의 LLM 추천(GenRec): https://youtu.be/9DMu9XuaiZ0

화면의 그림과 애니메이션은 원문 그림을 쓰지 않고 새로 그렸습니다. 원문 수치를 옮긴 그림에는 "원문 그림을 바탕으로 다시 그림"이라고 적었습니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#확산모델 #퀀트 #생성AI
