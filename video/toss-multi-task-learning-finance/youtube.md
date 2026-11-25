질문마다 모델을 늘리던 방식을 멈췄다, 수백 개 트리 모델을 멀티태스크 모델 하나로 (토스)
태그: 토스 테크 블로그, 토스 머신러닝, 멀티태스크 학습, 멀티태스크 러닝, 금융 머신러닝, 핀테크 데이터 사이언스, 마케팅 타기팅, 트리 모델, 모델 통합, MLOps, 재학습 자동화, 추천 시스템, PLE 구조, 공유 인코더, 부정적 전이, 손실 마스킹, 평균 정밀도, 딥러닝 모델 설계, ML 엔지니어, 데이터 과학자, Toss, multi-task learning, MTL, PLE, Progressive Layered Extraction, negative transfer, shared encoder, Meta Lattice, model consolidation, financial ML, marketing targeting, GBDT, machine learning platform, Average Precision, 토스 ML 챕터, 개인화 마케팅, 이커머스 머신러닝, Tencent PLE, 듣는편람

트리 모델이 수백 개라 재학습도 못 돌리고 있나요? 질문 하나에 모델 하나씩 붙이는 방식은 언제 한계에 닿을까요?
토스 ML 챕터의 글 "목적마다, 상품마다 늘던 모델을 하나로: 금융 도메인에 멀티태스크 학습 적용하기"를 12장면으로 풀어 읽습니다. 과제 수 × 상품 수만큼 불어나던 트리 모델을 멀티태스크 모델 하나로 묶은 두 사례입니다.

마케팅용 금융 행동 수십 개를 한 번에 예측하는 모델은 목적별 트리 모델보다 AP가 약 54% 올랐고, 실제 발송에서 불필요한 발송을 약 35% 줄였습니다. 상품마다 분류 하나와 회귀 둘을 함께 푸는 모델은 MAE가 66-79% 줄고 AUC가 약 10% 올랐으며, 새 상품도 모델을 새로 만들지 않고 예측합니다. 공유 인코더와 PLE(공유 전문가·과제별 전문가·게이트), 정답 없는 과제의 손실만 가리는 법, 중요한 신호에 출력층 가까이 전용 길을 내는 설계, 그리고 부정적 전이·배포가 묶이는 문제까지 짚습니다. 모션 그래픽 네 편(Remotion)으로 모델 폭증, PLE 구조, 손실 마스킹, 신호 전용 길을 보여 드립니다.

이런 분께 맞습니다
- 과제마다 상품마다 모델이 늘어 운영이 버거운 ML 엔지니어
- 멀티태스크 학습을 실무에 써 볼지 고민하는 데이터 과학자
- AUC는 그대로인데 캠페인 성과가 달라지는 이유가 궁금한 마케팅 분석가

{챕터}

원문: https://toss.tech/article/multi-task-learning-in-finance
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/toss-multi-task-learning-finance/
함께 보기, 무신사가 예측을 넘어 결정과 발견으로 간 두 ML 플랫폼: https://youtu.be/lLAnXRaXj2c

화면의 그림과 애니메이션은 원문 그림을 쓰지 않고 새로 그렸습니다. 성과 수치는 모두 원문에서 옮겼습니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#토스 #멀티태스크학습 #머신러닝
