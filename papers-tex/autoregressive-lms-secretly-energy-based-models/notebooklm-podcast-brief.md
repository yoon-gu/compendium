# NotebookLM Podcast Brief — Autoregressive LMs are Secretly Energy-Based Models

## Paper identity

- Title: Autoregressive Language Models are Secretly Energy-Based Models: Insights into the Lookahead Capabilities of Next-Token Prediction
- Authors: Mathieu Blondel, Michael E. Sander, Germain Vivier-Ardisson, Tianlin Liu, Vincent Roulet
- arXiv: https://arxiv.org/abs/2512.15605
- Compendium: https://yoon-gu.github.io/compendium/papers/autoregressive-lms-secretly-energy-based-models/

## One-paragraph thesis

이 논문의 thesis는 Autoregressive LM이 단순히 “다음 token만 맞히는” local predictor가 아니라, 함수공간 관점에서는 Energy-Based Model의 sequence-level energy를 암묵적으로 표현할 수 있다는 것이다. 저자들은 probability chain rule에서 ARM-EBM bijection을 만들고, 이를 MaxEnt RL의 soft Bellman equation과 연결한다. 이 관점은 next-token prediction이 왜 lookahead/planning처럼 보이는 behavior를 낳을 수 있는지 설명한다.

## Suggested episode structure

1. **Hook** — “Next-token prediction만 하는 model이 어떻게 planning처럼 행동할까?”
2. **ARM vs EBM** — ARM은 conditional next-token distribution, EBM은 complete response의 energy/score로 시작한다.
3. **Chain rule as bridge** — probability chain rule이 EBM의 sequence-level score와 ARM의 token-level conditional을 연결한다.
4. **Soft Bellman connection** — 이 bijection이 MaxEnt RL의 soft Bellman equation과 같은 구조임을 설명한다.
5. **Supervised learning equivalence** — ARM과 EBM의 supervised objective가 같은 optimum을 가질 수 있음을 설명한다.
6. **Distillation and error bound** — EBM을 ARM으로 distill할 때 어떤 KL bound가 나오는지 다룬다.
7. **Practitioner takeaway** — next-token prediction의 한계와 가능성을 균형 있게 정리한다.

## Key technical concepts

- Autoregressive Model (ARM): token-by-token conditional probability를 factorize하는 language model.
- Energy-Based Model (EBM): complete sequence에 score/energy를 부여하고 softargmax로 distribution을 정의하는 model.
- Probability chain rule: joint probability를 conditional probability들의 product로 분해하는 기본 원리.
- Bijection: ARM parameter/function과 EBM score function 사이의 one-to-one mapping.
- Soft Bellman equation: MaxEnt RL에서 value와 reward가 log-sum-exp backup으로 연결되는 equation.
- Distillation: EBM의 sequence-level distribution을 ARM의 autoregressive factorization으로 옮기는 과정.

## Pronunciation / terms to keep in English

ARM, EBM, Energy-Based Model, Autoregressive Model, next-token prediction, lookahead, MaxEnt RL, soft Bellman equation, chain rule, bijection, KL bound, distillation, supervised learning, function space.

## Caveats and limitations

- 결과는 주로 function space의 이론적 equivalence다. 실제 finite Transformer의 optimization dynamics나 data efficiency를 곧바로 보장하지 않는다.
- EBM sampling은 일반적으로 어렵고, ARM은 sampling이 쉽다. 이 차이는 practical deployment에서 중요하다.
- “ARM이 EBM이다”라는 표현은 정확히는 적절한 mapping 아래에서 같은 distribution/function을 표현할 수 있다는 의미로 설명해야 한다.

## Closing takeaway

이 논문은 next-token prediction을 과소평가하지 말라는 메시지를 준다. ARM은 token-level predictor처럼 보이지만, chain rule과 soft Bellman 관점에서는 sequence-level energy를 담아낼 수 있고, 이것이 LLM의 lookahead-like behavior를 이해하는 강력한 이론적 lens가 된다.
