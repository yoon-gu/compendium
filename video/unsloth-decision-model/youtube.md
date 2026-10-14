Unsloth로 LLM을 생성형에서 결정형으로, 나만의 결정 모델 학습하기
태그: Unsloth, 언슬로스, Unsloth 파인튜닝, LLM 분류, LLM 파인튜닝, 결정 모델, 텍스트 분류, 의도 분류, 고객 문의 분류, 문의 라우팅, LoRA 파인튜닝, 로라, Qwen 파인튜닝, 로컬 LLM, 소형 언어 모델, 확률 보정, 기대 보정 오차, LLM threshold, 구조화 출력, 고객 지원 자동화, 큐웬, 젬마, decision model, Laya, Clef, Jev, Qwen, Gemma, Llama, LoRA, fine-tuning, text classification, intent classification, calibration, BANKING77, CLINC150, Decision API, local LLM, 듣는편람

LLM으로 고객 문의를 분류하는데 답 형식이 자꾸 깨지나요? 모델이 얼마나 확신하는지도 알 수 없어서 곤란하셨나요? 글을 쓰는 대신 선택지마다 확률을 매기는 '결정 모델'로 바꾸면 이 문제들이 한꺼번에 풀립니다.

Unsloth 공식 문서 "Train your own Decision Model"을 12장면으로 풀어 읽습니다. 생성형 LLM에 분류를 시키면 무엇이 걸리는지, 헤드와 LoRA가 무엇인지부터 짚습니다. 이어서 noul·choice·score 세 가지 질문 타입, Qwen3.5 0.8B를 4GB GPU에서 42분 학습해 정확도를 30%대에서 78%까지 올린 결과, 확률 보정과 기대 보정 오차(ECE) 계산(예시 값으로), Jev 호환 Decision API로 서빙하는 법, 입력을 한 번 읽고 헤드가 선택지마다 점수를 매기는 원리를 다룹니다. 문서 안에서 학습 설정이 서로 어긋나는 부분도 짚었습니다. 애니메이션 네 편으로 생성형과 결정형의 차이, 파싱이 깨지는 순간, 한 번 읽기, threshold를 보여 드립니다.

이런 분께 맞습니다
- 문의 분류·태깅·라우팅에 LLM API를 쓰고 있는데 비용과 형식 오류가 신경 쓰이는 개발자
- 작은 모델을 직접 파인튜닝해 로컬에서 돌려 보고 싶은 ML 엔지니어
- 모델 확률을 믿고 자동화 threshold를 정하고 싶은 데이터 사이언티스트

{챕터}

원문(영어): https://unsloth.ai/docs/new/train-your-own-decision-model-with-unsloth
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/unsloth-decision-model/
함께 보기, Codemode란 무엇인가: https://youtu.be/lzKaQiJ6_dU

화면의 그림과 애니메이션은 원문 스크린샷을 쓰지 않고 새로 그렸습니다. 성능 수치는 Unsloth가 직접 잰 값입니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#LLM #파인튜닝 #생성AI
