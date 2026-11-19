가장 싼 LLM 호출은 부르지 않은 호출이다, 규칙은 코드로 판단은 모델로 나누는 법 (AWS)
태그: LLM 비용 절감, 생성형 AI 비용, AI 비용 최적화, LLM 호출 줄이기, 모델 라우팅, 결정 호출, 구조화 출력, 의도 분류, 고객 문의 분류, 정규식, 빠른 길, 골든 평가 세트, 모델 크기 선택, 그림자 모드, 환각, 확률 보정, AI 에이전트 설계, 아마존 베드락, LLM threshold, Cut generative AI costs, Code for rules models for judgment, AWS, Amazon Bedrock, structured outputs, Strands Decider, SageMaker, Step Functions, AWS Lambda, fast path, right-sizing, golden evaluation set, LLM cost, AI 아키텍처, 결정적 코드, 키워드 매칭, 임베딩 유사도, ReDoS, model distillation, LLMOps, 프롬프트 라우팅, 듣는편람

LLM 비용, 어느 모델로 바꿔야 줄어들까요? 그 전에 이 단계에 모델이 필요하기는 한지부터 물어보셨나요?
AWS 블로그 글 "Cut generative AI costs: Code for rules, models for judgment"를 10장면으로 풀어 읽습니다. 비용을 가장 크게 좌우하는 건 모델 선택이 아니라 모델을 부르느냐 마느냐라는 주장입니다.

시제품에서 시작해 입력 검사·형식 바꾸기·라우팅까지 모두 LLM에 맡기게 되는 버릇이 돈·시간·들쭉날쭉함이라는 세 가지 값을 어떻게 치르게 하는지 짚습니다. 이어서 단계마다 던지는 세 가지 질문(규칙으로 판정되나, 모델이 규칙을 한 번만 써 줄 수 있나, 정해진 보기에서 고르나)과, 고객지원 도우미 다섯 단계 중 모델이 꼭 필요한 건 하나뿐이었다는 예를 봅니다. 보기에서 고르게 하는 결정 호출과 '모르겠음'으로 위로 넘기기, 보정된 확신도와 threshold, 키워드 규칙을 먼저 돌려 하루 100만 건 중 5만 건만 모델로 보내는 빠른 길(원문이 밝힌 셈 예시), 골든 평가 세트로 모델 크기 맞추기, 규칙이 낡는 걸 잡는 그림자 모드까지 다룹니다. 애니메이션 네 편으로 결정 호출, 세 질문, 다섯 단계, 빠른 길을 보여 드립니다.

이런 분께 맞습니다
- LLM API 비용 청구서가 생각보다 커서 어디부터 줄일지 고민인 개발자
- 문의 분류·라우팅·형식 검사에 모델을 쓰고 있는 AI 서비스 팀
- 새 모델이 나올 때마다 바꿀지 말지 회의하는 팀장과 아키텍트

{챕터}

원문(영어): https://aws.amazon.com/ko/blogs/machine-learning/cut-generative-ai-costs-code-for-rules-models-for-judgment/
한국어 번역·정리 노트: https://yoon-gu.github.io/compendium/notes/code-for-rules-models-for-judgment/
함께 보기, LLM을 생성형에서 결정형으로: https://youtu.be/pvrkJ7Ak6AU

화면의 그림과 애니메이션은 원문 그림을 쓰지 않고 새로 그렸습니다. 모델 점수·비용 배수 그림과 문의 예시는 설명을 위한 가상의 값입니다.

AI 사용 안내: 원문 정리와 대본 작성에 AI(Claude)를 썼고, 나레이션은 AI 음성(Typecast)입니다.

듣는편람은 읽을 만한 글을 골라 한국어로 풀어 읽어 주는 채널입니다. 구독하시면 매주 한 편씩 받아 보실 수 있어요.

#LLM #AI비용 #AWS
