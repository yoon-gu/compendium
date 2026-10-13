---
title: "LLM을 생성형에서 결정형으로 — Unsloth로 나만의 결정 모델 학습하기"
date: 2026-10-13
draft: false
math: true
source_url: "https://unsloth.ai/docs/new/train-your-own-decision-model-with-unsloth"
youtube: "pvrkJ7Ak6AU"
author: "Unsloth"
tags: ["AI", "LLM", "파인튜닝", "LoRA", "분류", "결정 모델", "Unsloth", "문서"]
summary: "Unsloth가 Qwen·Gemma·Llama 같은 LLM을 '결정 모델'로 파인튜닝하는 기능을 냈다. 글을 쓰는 대신 입력과 질문 목록을 한 번 읽고, 작은 헤드가 선택지마다 점수를 매겨 보정된 확률과 함께 답을 고른다. Qwen3.5-0.8B는 4GB VRAM, 42분 학습으로 홀드아웃 정확도 78%를 냈고, 학습한 모델은 Jev 호환 Decision API로 바로 서빙할 수 있다."
---

> **원문:** [Train your own Decision Model](https://unsloth.ai/docs/new/train-your-own-decision-model-with-unsloth) — Unsloth 공식 문서, 2026년 10월
>
> **저자:** Unsloth 팀 — 다니엘 한(Daniel Han)과 마이클 한(Michael Han) 형제가 세운 회사로, LLM 파인튜닝을 더 빠르고 적은 메모리로 돌리는 오픈소스 라이브러리 Unsloth[^unsloth]와 데스크톱 앱 Unsloth Studio를 만든다. 이 글은 그 공식 문서의 '새 기능' 안내 페이지다.
>
> 아래는 원문의 절 순서를 따라 요지를 정리하고 해설을 붙인 노트다. 요지 정리와 해설은 옮긴 이의 것이고 전문은 위 링크에서 읽을 수 있다. 그림은 원문에서 직접 불러온 것이다.

## 한눈에 보기

LLM을 분류기로 쓰는 흔한 방법은 "billing, technical, sales 중 하나로만 답해"라고 시키고 나온 글자를 파싱하는 것이다. 이 글은 그 대신 LLM에 작은 점수 헤드(head)를 달아 *고르는 일만* 하도록 파인튜닝하는 방법을 안내한다.

| 항목 | 내용 |
|---|---|
| 무엇을 만드나 | 입력(state)과 질문 목록을 받아 선택지마다 확률을 내는 결정 모델(decision model) |
| 바탕 모델 | Qwen3.5[^qwen], Gemma 4[^gemma], Llama 3.2[^llama] 등 Unsloth가 파인튜닝할 수 있는 LLM. 기존 결정 모델(Laya, Clef)을 추가로 파인튜닝해도 된다 |
| 구조 | LLM이 입력과 모든 질문·선택지를 한 번 읽고, Clef[^clef]와 같은 설계의 작은 헤드가 선택지마다 점수를 매긴다. 글자는 하나도 생성하지 않는다 |
| 성능 | Qwen3.5-0.8B: 정확도 78%, VRAM 4GB, 학습 42분. 학습 전 30%대에서 70%대로 |
| 학습 방법 | 데스크톱 앱에서 클릭 몇 번 / 무료 Colab·Kaggle 노트북 / 파이썬 코드(`FastDecisionModel`, `DecisionTrainer`) |
| 서빙 | Jev[^jev] 호환 Decision API로 바로 연결. 기존 Jev 코드는 주소만 바꾸면 된다 |

## 먼저, 결정 모델이란 무엇인가

배경 자료: [Run and Serve Decision Models Locally with Unsloth: Laya + Jev API](https://unsloth.ai/docs/models/decision-laya)

결정 모델은 텍스트를 받아 *앱이 바로 행동할 수 있는 구조화된 결정*을 돌려주는 모델이다. 고객 문의를 담당 팀에 배정하거나 이메일을 거르거나 글에 태그를 붙이는 일이 대표적이다. TypeSafe AI의 Jev가 이 형식의 API를 먼저 내놓았고 Cloudflare의 Clef와 Unsloth 문서가 소개하는 Laya[^laya]가 같은 형식을 따르는 공개 대안이다.

요청에는 판단할 텍스트(`state`)와 질문 목록(`questions`)을 넣는다. 질문은 세 종류다.

| 타입 | 쓰임 | 돌려받는 것 |
|---|---|---|
| `noul` | 예/아니요 | '예'일 확률(0-1) |
| `choice` | 여러 선택지 중 하나 | 가장 그럴듯한 선택지와 선택지별 확률 |
| `score` | 순서 있는 척도(예: not urgent < soon < today) | 척도 위의 위치(0부터)와 수준별 확률 |

한 요청에 질문은 최대 64개, `choice`의 선택지는 최대 255개, `score`의 수준은 최대 10단계까지 넣을 수 있다. 문서는 행동을 정할 때 `confidence` 값보다 선택지별 `probabilities`를 보라고 권한다. 예를 들어 `technical` 확률이 0.8을 넘을 때만 버그 리포트를 만드는 식이다.

생성형 LLM에 분류를 시키는 보통 방식과 비교하면 차이가 분명하다. 아래는 두 방식을 파이썬으로 적어 본 것이다(원문의 `predict` 예시를 바탕으로 옮긴 이가 비교용으로 재구성했다).

```python
# 보통 방식: 생성형 LLM에게 글로 답하게 하고 파싱한다
prompt = f"""Customer message: {ticket}
Answer with one of: billing / technical / sales."""
text = llm.generate(prompt, max_new_tokens=5)   # 토큰을 하나씩 생성
team = text.strip().lower()                      # "Billing." "The billing team." 같은 답이 오면 파싱 실패
# 질문이 셋(팀, 환불 여부, 긴급도)이면 호출도 세 번이거나, JSON을 시켜 놓고 형식이 깨질까 걱정해야 한다
# 확률이 없다: 0.51로 고른 건지 0.99로 고른 건지 모른다
```

```python
# 결정 모델: 입력과 질문 전부를 한 번 읽고 선택지마다 확률을 낸다
answers = FastDecisionModel.predict(model, tokenizer, ticket, {
    "team":    {"type": "choice", "instructions": "Which team should handle this?",
                "criteria": {"billing": "invoices, payments, refunds",
                             "technical": "bugs, outages, errors",
                             "sales": "pricing, new plans"}},
    "refund":  {"type": "noul",  "instructions": "Does the customer ask for a refund?"},
    "urgency": {"type": "score", "instructions": "How urgent is this?",
                "criteria": ["not urgent", "soon", "today"]},
})
# 순전파 한 번에 세 질문이 함께 결정된다. 생성 토큰은 0개
# answers["team"]["probabilities"] → {"billing": 0.99, ...}: threshold를 코드에서 정하면 된다
# 답은 언제나 정해진 선택지 키 중 하나라서 파싱할 일이 없다
```

## 학습 결과

Unsloth는 Clef 헤드를 단 LLM을 LoRA로 파인튜닝했다. 학습 전에는 30-37%로 거의 찍는 수준이던 정확도가 최고 78%까지 올랐다. 학습 데이터는 Laya·Clef와 같은 형식을 썼고 테스트 세트는 학습 데이터와 겹치지 않도록 오염 제거(decontamination)를 거쳤다. 홀드아웃(holdout) 정확도는 학습에 쓰지 않고 떼어 둔 행으로 잰 값이다.

| 모델 | typed-decisions | BANKING77 | CLINC150 | 홀드아웃 정확도 |
|---|---|---|---|---|
| Qwen3.5-0.8B | 36% → **73%** | 7% → 74% | 19% → 76% | 78% |
| Qwen3.5-2B | 33% → 78% | 1% → 58% | 1% → 62% | 81% |

다른 모델도 같은 방식으로 학습된다.

| 모델 | 테스트 정확도 | VRAM | 학습 시간 |
|---|---|---|---|
| Qwen3.5-0.8B | 78% | 4GB | 42분 |
| Qwen3.5-2B | 81% | 8GB | 40분 |
| Llama 3.2 3B | 79% | 4.1GB | 30분 |
| Gemma 4 E4B | 77% | 14.4GB | 49분 |
| Laya (추가 파인튜닝) | 77% | 2.5GB | 10분 |

학습 데이터는 typed-decisions[^typed]에 12개 공개 데이터셋을 섞었다. 뉴스 주제 분류(ag_news), 과학 문제(arc), 은행 고객 문의 의도 분류(banking77[^banking]), 예/아니요 질의응답(boolq), 의도 분류(clinc150[^clinc]), 상식 추론(commonsense_qa), 다분야 객관식(mmlu), 자연어 추론(natural language inference, NLI) 세 가지(mnli, snli, wanli), 프롬프트 주입 탐지(prompt_injections), 5단계 감성 분류(sst5)다. 테스트 세트는 3,000행으로 typed-decisions 2,000행, BANKING77 500행, CLINC150 500행이다.

> 해설 — 작은 모델이 눈에 띈다. 0.8B 모델이 4GB VRAM에서 2B 모델과 몇 %p 차이로 따라붙고 Laya를 추가 파인튜닝하면 2.5GB·10분이면 된다. 사내 문의 분류처럼 선택지가 정해진 일이라면 큰 생성형 모델을 API로 부르는 대신 이 정도 크기를 직접 돌리는 쪽이 훨씬 싸다. 다만 2B 모델의 BANKING77·CLINC150 점수(58%, 62%)는 0.8B보다 낮은데 문서는 이유를 설명하지 않는다. 의도가 77개, 150개로 많은 데이터셋에서 학습 전 점수가 1%였다는 점도 함께 볼 만하다.

## 학습하는 세 가지 방법

### 1. Unsloth 앱에서

1. Unsloth 데스크톱 앱을 설치한다(macOS, Windows, Linux). 터미널에서 설치 스크립트를 써도 된다.
2. Train 탭에서 LLM(예: `unsloth/Qwen3.5-4B`)을 고르고 **Train as**를 **Decision model**로 바꾼다. 쓸 만한 설정이 자동으로 채워진다. 문서의 결과를 재현하려면 에폭 2, LoRA rank 16, 학습률 2e-4로 맞춘다.
3. 파일을 올리거나 Hugging Face[^hf]의 데이터셋을 고른다. typed-decisions라면 Subset을 `all`로 둔다.
4. Start Training을 누른다. 학습 전후 홀드아웃 정확도를 보여 주고 모델의 확신도를 보정(calibration)해 준다.
5. Use in Decision API를 누르면 `laya`, `default`, `jev-latest`로 오는 요청이 내 모델로 간다. Decision API의 Try It에서 바로 시험해 볼 수도 있다.

![학습이 끝난 Unsloth 화면](https://3215535692-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FxhOjnexMCB3dmuQFQ2Zq%2Fuploads%2Fcj5kfa0UJdty3SCM27dM%2F2-training-finished.png?alt=media&token=4c1891e0-904a-4ca6-a9b4-7f2f5f059d35)

### 2. 무료 노트북으로

Google Colab과 Kaggle[^colab]의 무료 GPU로 Qwen3.5-4B를 결정 모델로 학습하는 노트북이 있다. 데이터 준비, 학습, 내보내기까지 단계별로 따라가면 된다. UI로 학습하는 Unsloth Studio Colab 노트북도 있다.

- [Google Colab 노트북](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_5_(4B)-Decision.ipynb)
- [Kaggle 노트북](https://www.kaggle.com/notebooks/welcome?src=https://github.com/unslothai/notebooks/blob/main/nb/Kaggle-Qwen3_5_(4B)-Decision.ipynb&accelerator=nvidiaTeslaT4)

### 3. 코드로

`pip install --upgrade unsloth` 후 흐름은 이렇다(원문 코드를 줄여 옮겼다).

```python
from unsloth import FastDecisionModel, DecisionTrainer
from datasets import load_dataset

model, tokenizer = FastDecisionModel.from_pretrained(
    "unsloth/Qwen3.5-4B", max_seq_length=2048, load_in_4bit=True)
model = FastDecisionModel.get_peft_model(model, r=16, lora_alpha=16)   # LoRA 어댑터

dataset = load_dataset("LocalLLaMA/typed-decisions", "all", split="train")
items, report = FastDecisionModel.build_dataset(dataset, tokenizer, model)
train_items, eval_items = FastDecisionModel.split_holdout(items, seed=3407)

trainer = DecisionTrainer(model=model, processing_class=tokenizer,
                          train_dataset=train_items, eval_dataset=eval_items,
                          args=TrainingArguments(...))   # 배치 2, 그래디언트 누적 4, 코사인 스케줄 등
trainer.train()

FastDecisionModel.calibrate(model, tokenizer, eval_items)  # 정확도, ECE, 손실
model.save_pretrained("qwen-decisions")                    # LoRA 어댑터 + 헤드
model.save_pretrained_merged("qwen-decisions-merged")      # 16비트 통합 모델
```

Llama나 Gemma 4를 쓰려면 `model_name`만 `unsloth/Llama-3.2-3B-Instruct`나 `unsloth/gemma-4-E4B-it`로 바꾸면 된다. 자기 데이터를 쓸 때는 한 행에 입력(state), 판단할 질문들, 정답을 넣는 데이터셋 형식을 따른다.

보정은 `split_holdout`이 떼어 둔 행으로 한다. 목적은 모델이 내는 확률이 실제로 맞는 비율과 일치하게 만드는 것이다. 결과에는 기대 보정 오차(expected calibration error, ECE)가 함께 나온다. 예를 들어 모델이 "80% 확신"이라고 한 답들을 모았을 때 실제로 80%쯤 맞아야 보정이 잘 된 것이다. 이게 맞아야 앞에서 말한 "확률 0.8 넘을 때만 처리" 같은 threshold가 의미가 있다. 문서는 어떤 보정 기법을 쓰는지는 밝히지 않는다.

예측은 `predict`에 입력과 질문을 데이터셋과 같은 형식으로 넘긴다(앞 절의 예시). `answer`는 `choice`면 선택지 키, `noul`이면 `True`/`False`, `score`면 수준 번호다. 레이블 붙은 테스트 세트로 정확도를 재려면 `evaluate`를 쓴다.

## Decision API로 서빙하기

앱에서 학습한 모델은 Settings → API에 실행 이름으로 나타난다. 코드로 학습한 모델은 통합 모델 폴더를 지정해 Unsloth를 띄운다.

```bash
UNSLOTH_SYSTEMONE_MODEL=/path/to/qwen-decisions-merged unsloth studio -H 0.0.0.0 -p 8888
```

Settings → API에서 Decision API를 켜면 `laya`, `default`, `jev-latest`로 오는 요청이 내 모델로 가고 답의 형식도 Laya와 같다. 모델은 GPU가 필요하고 첫 요청 때 올라오는데 몇 분 걸릴 수 있다. 학습이 GPU를 쓰는 동안 Decision API는 기다렸다가 학습이 끝나면 다시 답한다.

Jev를 쓰던 코드는 TypeSafe SDK의 주소와 키 환경 변수만 로컬 Unsloth로 바꾸면 그대로 돈다. 다만 `confidence` 계산식이 Jev와 달라서 Jev에서 맞춘 `confidence` threshold는 옮겨 쓸 수 없다. threshold는 `probabilities`에 걸어야 한다.

## 어떻게 동작하나

Unsloth는 입력을 프롬프트 하나에 넣고 그 뒤에 모든 질문과 선택지를 붙인다. LLM은 이것을 딱 한 번 읽는다. 그다음 Cloudflare Clef와 같은 설계의 작은 헤드가 질문과 선택지 위치에서 LLM이 낸 출력(은닉 상태)을 보고 선택지마다 점수를 매긴다. 모든 질문을 함께 결정한다.

글을 쓰지 않으므로 LLM의 단어 예측에 메모리를 쓰지 않는다. 생성형 LLM은 위치마다 어휘 전체(수십만 개)에 대한 점수를 계산하는데 결정 모델은 그 대신 선택지 개수만큼의 점수만 내면 된다.

> 해설 — 구조로 보면 오래된 방식인 "인코더 + 분류 헤드"(BERT 파인튜닝)에 가깝다. 다른 점은 두 가지다. 첫째, 선택지를 고정된 출력 층이 아니라 *프롬프트 속 글*로 준다. 그래서 학습 때 못 본 선택지도 설명만 바꿔 넣으면 고를 수 있다. 둘째, 바탕이 지시를 따르도록 학습된 LLM이라 질문 문장(`instructions`)과 선택지 설명(`criteria`)을 읽고 이해한다. 정해진 레이블만 배우는 분류기와 아무 말이나 하는 생성기 사이의 자리다.

## 권장 설정

- 4비트 LoRA, rank 16, 학습률 2e-4에서 시작한다. 새로 붙는 헤드는 기본 1e-4로 학습되며 `DecisionTrainer`의 `head_learning_rate`로 바꿀 수 있다.
- typed-decisions에서는 2에폭을 썼다. 데이터가 적으면 3-4에폭을 써 본다.
- 빨리 시험해 보려면 `max_steps = 60`. Qwen3.5-4B가 L4 GPU에서 10분 만에 76%에 이르렀다.
- 메모리가 모자라면 배치 크기를 반으로 줄이고 그래디언트 누적(gradient accumulation)을 두 배로 늘린다.
- `max_seq_length`는 학습 때 가장 긴 입력이다. 입력이 길면 질문과 선택지는 남기고 입력의 끝을 잘라 맞춘다. 예측 때는 16,384 토큰까지 읽는다.

> 해설 — 문서 안에서 숫자가 조금씩 어긋난다. 성능표 옆 설명은 "LoRA r=64로 1에폭"이라 하고 앱 안내와 권장 설정은 "rank 16, 2에폭, 학습률 2e-4"라 한다. 코드 예시는 학습률이 2e-5이고 에폭 대신 `max_steps = 240`을 쓴다. 재현하려면 어느 설정으로 표의 숫자가 나왔는지 원문에서 다시 확인하는 것이 좋다.

## 정리

생성형 LLM을 분류에 쓸 때 늘 걸리던 세 가지가 있다. 답 형식이 깨지고 질문마다 호출해야 하며 얼마나 확신하는지 모른다. 결정 모델은 이 셋을 한꺼번에 푼다. 질문을 한 번에 넣고 선택지 중 하나만 고르며 보정된 확률을 준다. Unsloth는 이것을 자기 데이터로 4GB GPU에서 한 시간 안에 학습하고 로컬 API로 띄우는 데까지 이어 놓았다. 선택지가 정해진 판단을 대량으로 돌려야 하는 팀이라면 생성형 API를 부르기 전에 시험해 볼 만한 길이다.

[^unsloth]: Unsloth — LLM 파인튜닝을 빠르고 메모리 적게 하도록 최적화한 오픈소스 라이브러리이자 데스크톱 앱. 이 글에서 결정 모델 학습 기능(`FastDecisionModel`, `DecisionTrainer`)과 Decision API 서버를 제공한다.
[^qwen]: Qwen — 알리바바의 오픈 웨이트 LLM 계열. 이 글의 주된 바탕 모델(0.8B, 2B, 4B).
[^gemma]: Gemma — 구글의 오픈 웨이트 LLM 계열. 이 글에서는 Gemma 4 E4B를 결정 모델로 학습한 결과를 싣는다.
[^llama]: Llama — 메타의 오픈 웨이트 LLM 계열. 이 글에서는 Llama 3.2 3B 결과를 싣는다.
[^clef]: Clef — Cloudflare가 공개한 오픈 웨이트 결정 모델. Qwen 백본(backbone) 위에 모든 질문의 모든 선택지를 한 번에 점수 매기는 작은 헤드를 단 구조로, Unsloth가 이 헤드 설계를 그대로 쓴다.
[^jev]: Jev — TypeSafe AI의 결정 모델 API. `noul`·`choice`·`score` 질문 형식을 정했고, Laya·Clef와 Unsloth의 Decision API가 이 형식과 호환된다.
[^laya]: Laya — Unsloth 문서가 Jev의 공개 대안으로 소개하는 작은 결정 모델. 다국어판은 678MB, 4GB RAM이면 CPU에서도 돈다.
[^typed]: typed-decisions — Hugging Face의 `LocalLLaMA/typed-decisions` 데이터셋. 청구서, 보안 사고, 고객 응대, 에이전트 기록 같은 입력에 타입 있는 질문과 정답이 달려 있다. 이 글의 주 학습·평가 데이터.
[^banking]: BANKING77 — 은행 고객 문의 문장을 77개 의도로 분류하는 공개 데이터셋. 이 글의 평가 세트 중 하나.
[^clinc]: CLINC150 — 150개 의도와 범위 밖 문의를 담은 의도 분류 데이터셋. 이 글의 평가 세트 중 하나.
[^hf]: Hugging Face — 모델과 데이터셋을 공유하는 플랫폼. 학습 데이터를 여기서 바로 불러온다.
[^colab]: Google Colab·Kaggle — 무료 GPU가 붙은 브라우저 노트북 환경. Unsloth가 결정 모델 학습 노트북을 여기에 올려 두었다.
