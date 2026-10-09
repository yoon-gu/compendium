2026-W41-3 | 수학 공식을 버린 넷플릭스의 LLM 추천, GenRec 논문 해설 (Netflix)
태그: 넷플릭스 추천 알고리즘, 넷플릭스 알고리즘, 추천 시스템, 추천시스템, LLM 추천, LLM 추천 시스템, 생성형 추천, 거대언어모델, LLM, 컨텍스트 엔지니어링, 피처 엔지니어링, 랭킹 모델, 추천 랭커, 사후 학습, 파인튜닝, 보상 모델, 환각, 할루시네이션, 스케일링 법칙, A/B 테스트, vLLM, 프리필, 머신러닝, 딥러닝, 데이터 사이언스, 데이터 사이언티스트, ML 엔지니어, 추천 엔진, 개인화, 논문 리뷰, 논문 해설, AI 논문, 인공지능, ai, netflix recommendation, netflix algorithm, recommender system, llm recommendation, genrec, context engineering, ranking model, post-training, reward model, scaling laws, paper review, 듣는편람

넷플릭스 추천이 더 이상 수학 공식이 아니라면? 넷플릭스가 2026년 8월에 낸 논문 GenRec은 수천 개의 손설계 피처로 돌던 추천 랭커를, 시청 기록을 문장으로 풀어 읽는 LLM 랭커로 바꾼 과정을 담고 있습니다.

두 진행자가 대화로 논문을 풀어 읽습니다. 왜 기존 시스템이 병목이 됐는지, 기반 모델과 랭커를 두 단계로 나눠 학습한 이유, 시청 기록을 자연어로 바꾸는 언어화와 토큰을 3분의 1로 줄인 컨텍스트 엔지니어링, 없는 영화를 지어내지 못하게 막는 카탈로그 인식 랭킹 헤드, 클릭 대신 장기 만족에 보상을 주는 손실 함수, 한 번의 순전파로 카탈로그 전체 점수를 내는 프리필 전용 서빙, 그리고 트래픽 10%로 4주간 돌린 A/B 테스트에서 40배 적은 데이터로 기존 랭커를 이긴 결과까지 짚습니다. 화면에는 대화에 맞춰 논문의 수치와 구조를 정리해 두었습니다.

이런 분께 맞습니다
- 추천 시스템을 만들거나 운영하는 ML 엔지니어·데이터 사이언티스트
- LLM을 검색·추천 같은 기존 시스템에 어떻게 붙일지 고민하는 분
- 넷플릭스가 내 시청 기록을 어떻게 읽는지 궁금한 분

{챕터}

원문(영어): https://arxiv.org/abs/2608.10257
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/genrec-netflix/
함께 보기, AI Workers' Inquiry 2026: https://youtu.be/zzAYe3pQIng
함께 보기, AI 시대의 매니저의 길: https://youtu.be/BYF4YI8QPDM
함께 보기, AI를 예의 있게 쓰는 법: https://youtu.be/yBLFGCFUgeE

화면에 쓴 자료
- 루브 골드버그 장치 영상: Purdue Engineering, "2019 Purdue National Chain Reaction Competition Winner", CC BY 3.0, via Wikimedia Commons (https://commons.wikimedia.org/wiki/File:2019_Purdue_National_Chain_Reaction_Competition_Winner.webm)
- 루브 골드버그 장치 사진: Mbrickn, Imagination Station, CC0, via Wikimedia Commons (https://commons.wikimedia.org/wiki/File:Rube_Goldberg_Machine_at_Imagination_Station.jpg)
- 루브 골드버그 장치 사진: jclarson, CC BY 2.0, via Wikimedia Commons (https://commons.wikimedia.org/wiki/File:Rube_goldberg_machine.jpg)
- 루브 골드버그 만화 "Self-Operating Napkin"(1931): 퍼블릭 도메인, via Wikimedia Commons

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#넷플릭스 #추천시스템 #LLM
