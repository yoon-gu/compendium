Jane Street 자기회귀 확산 글 대화편, 시장 데이터는 연속이면서 이산이다
태그: Jane Street, 제인 스트리트, 제인스트리트, 자기회귀 확산, 확산 모델, 디퓨전 모델, 플로우 매칭, 시장 데이터 생성, 호가창, 오더북, 주식 데이터, 금융 데이터, 퀀트, 퀀트 트레이딩, 시계열 생성, 합성 데이터, 영과잉 모형, AI 팟캐스트, 팟캐스트, 대화형 해설, AI 논문, James Somers, Kavish, autoregressive diffusion, diffusion model, flow matching, rectified flow, DDPM, atom smoothing, market data, order book, synthetic data, quant, podcast, 듣는편람

AUC가 0.992에서 0.758로 떨어졌는데 왜 좋아진 걸까요? 확산 모델로 주식 호가창을 통째로 지어내려 한 Jane Street 인턴의 실험을 두 진행자가 묻고 답하며 풀어 봅니다.

Jane Street 블로그 글 "Can you use autoregressive diffusion to generate market data?"를 대화로 읽는 편입니다. 시장 미시구조는 처음인 진행자가 묻고, 글을 읽고 온 진행자가 답합니다. 호가창과 BBO, 시장 데이터가 영상처럼 연속인지 텍스트처럼 이산인지, 이벤트를 하나씩 이어 붙이는 자기회귀 확산 구조, DDPM의 노이즈 예측이 왜 폭발했고 flow matching은 왜 50단계로 충분했는지, 0초 간격처럼 한 점에 몰린 확률을 20개 범주로 떼어 낸 방법과 atom smoothing, 그리고 판별기 AUC를 읽는 방향과 롤아웃의 한계까지 다룹니다. 원문이 밝히지 않은 부분은 대화 안에서 그렇다고 짚습니다. 화면에는 대화 흐름에 맞춰 그림 스무 장과 애니메이션 네 편이 지나갑니다.

이런 분께 맞습니다
- 확산 모델이나 flow matching을 표 형식·시계열 데이터에 써 보려는 ML 엔지니어·데이터 사이언티스트
- 호가창이나 결제 데이터처럼 0과 정액에 확률이 몰린 금융 데이터를 다루는 분
- 그림만 보는 설명보다 묻고 답하는 대화로 이해하고 싶은 분

{챕터}

원문(영어): https://blog.janestreet.com/can-you-use-autoregressive-diffusion-to-generate-market-data/
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/autoregressive-diffusion-market-data/
함께 보기, 같은 글을 한 사람이 들려주는 나레이션 편: https://youtu.be/SPLx5_vGdl8

화면의 그림과 애니메이션은 원문 그림을 쓰지 않고 새로 그렸습니다. 원문 수치를 옮긴 그림에는 "원문 그림을 바탕으로 다시 그림"이라고 적었습니다.

AI 사용 안내: 원문 정리와 대화 대본 작성에 AI(Claude)를 썼고, 두 진행자의 목소리는 AI 음성(Typecast)입니다. 진행자 이름은 가명입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#확산모델 #퀀트 #팟캐스트
