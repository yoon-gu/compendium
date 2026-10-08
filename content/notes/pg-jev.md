---
title: "pg-jev: Postgres 테이블에 자연어로 조건을 거는 확장"
date: 2026-10-08
draft: false
source_url: "https://github.com/realZachi/pg-jev"
author: "Zachi (realZachi)"
tags: ["AI", "PostgreSQL", "SQL", "분류", "System One", "도구 사용", "오픈소스"]
summary: "WHERE 절에 '고객이 화가 나 있다' 같은 자연어 조건을 쓰면 행마다 TypeSafe의 Jev(확률을 돌려주는 System One 모델)에 물어 참/거짓·확률·선택·점수를 돌려주는 PostgreSQL 확장. 인덱스도 임베딩도 없는 전체 스캔이 설계이고, 20행 묶음·스트리밍 읽기·세션 캐시로 2,000행을 3.5초, 약 0.012달러에 판정한다. 행 전체가 외부 API로 나가고 superuser와 plpython3u가 필요하다는 제약이 붙는다."
---

> **원문:** [realZachi/pg-jev](https://github.com/realZachi/pg-jev) — Zachi, PostgreSQL License, 2026-09-17 첫 공개, 현재 0.2.1(2026-10-03). 문서 사이트 [pgjev.com](https://pgjev.com), [PGXN](https://pgxn.org/dist/jev/)
>
> 아래는 저장소의 README, 에이전트용 참고 문서(`.agents/skills/pgjev/references/`), CHANGELOG, SQL 소스를 읽고 한국어로 정리한 노트다. 수치는 모두 저자의 자체 측정값이다.

## 한 줄 요약

`SELECT * FROM people WHERE jev(people, 'the name is European');` — 조건을 말하듯 쓰면 Postgres가 행마다 모델에 물어 걸러 준다. 모델은 앞서 두 번 정리한 적 있는 [TypeSafe의 Jev](/compendium/notes/typed-decisions-from-glm-flash/), 텍스트를 생성하지 않고 타입이 정해진 질문에 **보정된 확률(calibrated probability)**을 돌려주는 System One 모델이다. 인덱스, 임베딩, 벡터 컬럼이 없고, `jev()`는 평범한 boolean 함수라 `AND age > 40`, 조인, `GROUP BY`, `ORDER BY jev_prob(...)`와 그대로 섞인다.

```sql
CREATE EXTENSION jev CASCADE;

-- 거르기: 확률 0.5 이상이면 참
SELECT * FROM tickets WHERE status = 'open' AND jev(tickets, 'the customer threatens to cancel');

-- 순위: 확률로 정렬
SELECT subject, jev_prob(tickets, 'the customer is angry') AS p FROM tickets ORDER BY p DESC LIMIT 20;

-- 분류: 닫힌 선택지 중 하나
SELECT jev_choice(tickets, 'which team should handle this?', ARRAY['billing','technical','security','sales']), count(*)
FROM tickets GROUP BY 1;

-- 점수: 순서 있는 등급에 대한 확률 가중 위치 (0..n-1)
SELECT name, jev_score(products, 'how luxurious is this product?', ARRAY['budget','mid-range','premium','luxury'])
FROM products ORDER BY 2 DESC;
```

## 어떻게 동작하나

확장(extension)의 본체는 SQL 파일 안의 PL/Python 함수 하나(`_jev_eval`)다. 버전 0.2.0 기준 흐름은 이렇다.

1. 행이 복합 값(composite)으로 들어오면 `to_json`으로 직렬화해 해시한다. 같은 (테이블, 질문, 행 내용)에 대한 답이 세션 캐시에 있으면 SPI도 API도 건드리지 않고 바로 돌려준다.
2. 테이블과 질문 조합에 대한 첫 캐시 미스가 **읽기 선행(read-ahead)** 작업을 띄운다. 테이블과 materialized view는 TID 범위 스캔으로, 일반 view·파티션·외부 테이블은 `OFFSET`/`LIMIT` 페이지로, 물리적 순서대로 1,000행씩 읽는다.
3. 행을 `jev.batch_size`(기본 20)개씩 한 요청에 담는다. 요청 하나는 `{"condition": …, "rows": [...]}`라는 상태 하나와, 행마다 "rows[i]가 조건을 만족하는가"를 묻는 yes/no 질문(TypeSafe 용어로 noul) 20개로 구성된다. 요청당 고정 오버헤드가 약 270토큰이라, 행 하나만 보내면 약 435토큰, 20개 묶음이면 행당 약 175토큰이 든다.
4. `jev.concurrency`(기본 16)의 두 배까지 요청을 동시에 띄우고, 영속 HTTPS 연결을 재사용한다. 묶음이 돌아오는 즉시 그 행들의 답이 나가므로 executor가 테이블 전체를 기다리지 않는다. 그래서 `LIMIT`은 진행 중인 창(window)만 끝내고 멈추고, 같은 `WHERE`의 더 싼 술어가 먼저 걸러 낸 행은 판정하지 않는다.
5. 인덱스 스캔·조인·역방향 스캔처럼 물리적 순서 밖의 행을 요청받으면 하나씩 보내지 않고 건너뛴 이웃 행과 묶는다. `jev.max_prefetch_rows`(기본 5,000)는 읽기 선행이 얼마나 멀리 찾아보고 건너뛴 행을 얼마나 기억하는지의 한도이지, 캐시나 세션 메모리의 한도가 아니다.
6. 답은 행 내용과 질문을 키로 백엔드 세션(PL/Python `GD`)에 캐시된다. 다시 실행, 임계값 변경, 확률로 정렬, 집계는 전부 공짜다. 조건을 한 단어라도 바꾸면 새 스캔이다. `UPDATE`로 행이 바뀌면 해시가 달라져 자동으로 다시 판정된다.
7. 서브쿼리나 CTE의 익명 `record`는 읽기 선행을 못 해 **행당 한 요청**이 된다. 저자가 "느린 pgjev 쿼리의 가장 흔한 단일 원인"으로 꼽는 대목이고, 처방은 베이스 테이블이나 view에 `jev()`를 거는 것이다.

재시도는 429·529·5xx에서 `Retry-After`를 따르고, 풀에 든 연결은 재사용 전에 상태를 확인한다. 대기는 250ms 단위로 잘라서 `statement_timeout`과 취소 요청이 먹힌다.

### 왜 한 요청에 20행인가

모델은 배열 안에서 `rows[i]`를 **위치로** 찾는데, 배열이 길어지면 이게 흔들린다. 구조화 컬럼에서 만든 정답(직함, EU 회원국 여부, 자유 텍스트 안의 특정 문구; 각 400행)으로 재 보니 묶음 1-20행은 100%, 40행은 92-98%, 80행은 77-94%였다. 행 폭을 1,000자까지 늘려도 20행에서는 차이가 없었고, 행에 이름을 붙이는 방식은 도움이 안 됐다. 20행 묶음은 40행보다 토큰을 4% 더 쓰지만 요청 지연은 크기에 거의 무관해서 속도는 같다. 그래서 기본값이 20이고 "그대로 두라"고 한다.

### 측정치

유럽에서 API까지 왕복 약 190ms인 환경, 2,000행 테이블 기준.

| 상황 | 결과 |
|---|---|
| 새 조건, 전체 | ≈ 3.5초, 요청 100개, 입력 토큰 ≈ 296k, ≈ $0.012 |
| 같은 세션에서 같은 쿼리 재실행 | ≈ 50ms (캐시) |
| 새 조건에 `LIMIT 3` | ≈ 0.6초 |
| 연결이 따뜻한 상태에서 새 조건 | ≈ 2.3초 (새 연결의 첫 요청이 TLS + 서버 준비로 0.9-1.9초, 이후 요청당 ≈ 0.3초) |
| 0.1.0 (비교) | 8.5초, 338k 토큰 |

비용은 `입력 토큰 × $0.042 / 1M`(jev-1.13 정가, 출력 토큰은 무료). 경험칙으로 **행당 약 175토큰 ≈ $0.0000074**, 1천 행 ≈ $0.007, 10만 행 ≈ $0.7. `jev_stats()`가 세션 누계를, `jev.notices`가 켜져 있으면 문장마다 `NOTICE`로 요청 수·토큰·예상 비용·시간을 보여 준다.

## 함수

| 함수 | 반환 | 용도 |
|---|---|---|
| `jev(row, condition [, threshold])` | boolean | `WHERE` 술어. 임계값 우선순위: 인자 → `jev.threshold` → 0.5 |
| `jev_prob(row, condition)` | float8 | 조건을 만족할 확률 0..1 |
| `jev_score(row, question, levels[])` | float8 | 순서 있는 등급에 대한 확률 가중 위치 (0..n-1) |
| `jev_score_norm(…)` | float8 | 같은 것을 0..1로 정규화 |
| `jev_choice(row, question, options[])` | text | 가장 그럴듯한 선택지 하나 |
| `jev_confidence(row, question, kind, options[])` | float8 | `choice`/`score` 답의 확신도 |
| `jev_eval(row, question, kind, options[])` | jsonb | 원시 답 전체 (확률 벡터, 범례, 확신도) |
| `jev_stats()` / `jev_cache_clear()` / `jev_version()` | | 세션 통계 / 캐시 비우기 / 버전 |

`row` 자리에는 테이블 별칭 자체를 넣는다(`jev(people, …)`). 행 전체가 `to_json`으로 가므로 **컬럼 이름도 모델이 본다** — 이름이 설명적일수록 좋다. 모든 함수는 `STABLE`이라 `WHERE`, `SELECT`, `ORDER BY`, `CASE`, 조인, view에는 쓸 수 있지만 인덱스 정의나 generated column에는 못 쓴다. `jev_choice`와 `jev_confidence`를 같은 (질문, 종류, 선택지)로 부르면 캐시를 공유해 API 호출은 한 번이다.

## 설정

전부 `jev.` 접두어의 GUC라 `SET`, `SET LOCAL`, `ALTER ROLE … SET`, `ALTER DATABASE … SET`, `postgresql.conf` 어디서든 정한다. 기억할 것만 추리면:

- `jev.api_key` — 서버 프로세스의 `TYPESAFE_API_KEY` 환경변수가 기본. 클라이언트 셸의 환경변수는 소용없다.
- `jev.model` — 기본 `jev-latest`. 결과가 보고서에 들어가면 `jev-1.13.0`처럼 고정하라고 한다. 모델 릴리스 사이에 답이 바뀔 수 있다.
- `jev.batch_size` 20, `jev.concurrency` 16, `jev.timeout` 30초, `jev.keepalive` 600초.
- `jev.api_url` — 기본은 TypeSafe API. `POST /v1/systemone` 계약만 같으면 어느 서버든 가리킬 수 있고, **`*.typesafe.ai` 호스트가 아니면 API 키 없이 요청이 나간다**(0.2.1). 예로 든 로컬 서버가 둘인데, [stuntd](https://github.com/bladedevoff/stuntd)는 Jev API 뒤에 [Laya](/compendium/notes/laya-system1-decision-engine/)를 두고 답을 기록해 질문마다 헤드를 학습시키므로 한 테이블의 판정이 시간이 지나며 로컬로 옮겨 갈 수 있다고 소개한다. 다른 하나는 laya-server.
- 지출 가드 `jev.max_rows_per_statement`, `jev.max_chars_per_statement` — 한 문장이 API로 보낼 행 수·글자 수 상한. 공유 서버에서는 켜 두라는 권고(`ALTER DATABASE app SET jev.max_rows_per_statement = 5000` 식).

## 조건을 잘 쓰는 법

저장소가 에이전트용으로 정리해 둔 체크리스트가 사람에게도 그대로 유용하다.

- 라벨이 아니라 관찰 가능한 행동을 쓴다. `'churn risk'`보다 `'the customer threatens to leave, dispute a charge, or take legal action'`.
- 산술, 날짜, 정확 일치, 조인은 SQL에 둔다. 모델은 의미 판단만.
- 임계값을 고르기 전에 `jev_prob()`로 분포를 본다. `width_bucket`으로 히스토그램을 그리고, 0.4-0.6 구간을 뽑아 보면 모델이 모호하게 느끼는 행이 보이고, 대개 조건 문구를 조이라는 신호다.
- 모델이 볼 컬럼만 담은 view를 만들어 `jev(view, …)`로 부른다. 개인정보와 토큰을 함께 줄인다. view는 테이블처럼 읽기 선행과 묶음 처리가 된다.
- 한 번에 한 조건. "A 또는 B"는 괜찮지만 다섯 가지 나열은 `jev_choice`가 낫다. 서로 배타적인 두 조건으로 `CASE`를 짜면 스캔이 두 번이니 `jev_choice` 하나로.
- 조건은 사용자의 언어로 써도 되고 데이터는 다른 언어여도 된다. 텍스트 컬럼의 언어가 중요하면 조건에 밝힌다.

## 주의할 점 — 저자가 먼저 적어 둔 것

- 전체 스캔이 설계다. 자연어 조건을 답해 줄 인덱스는 없다. `jev()`에 닿는 모든 행이 세션당 한 번 판정된다. SQL로 먼저 자르라.
- 데이터가 Postgres 밖으로 나간다. 행 내용이 HTTPS로 TypeSafe API에 간다. 공유하면 안 되는 데이터에는 쓰지 말고, 필요한 것만 담은 view를 쓰라.
- 신뢰받지 않는 언어이고 superuser 설치다. `plpython3u`는 서버 프로세스의 OS 권한으로 돈다. superuser만 확장을 만들 수 있고, Supabase·Neon·RDS 같은 관리형 호스트에서는 돌릴 수 없다.
- 캐시는 백엔드마다 따로다. 연결 풀의 백엔드가 각자 캐시를 데운다. `jev_cache_clear()`는 현재 세션만 비운다. 캐시는 고유한 (행, 질문) 쌍만큼 자랄 수 있고 `jev.max_prefetch_rows`로 제한되지 않는다.
- SQL의 대체물이 아니다. 산술, 날짜, 동등 비교, 조인은 SQL에 두고 모델은 의미 판단에만 쓴다.

## 설치

PostgreSQL 14-17, `plpython3u`(Debian/Ubuntu는 `postgresql-plpython3-NN` 패키지), superuser, 그리고 [console.typesafe.ai](https://console.typesafe.ai)의 API 키. `pgxn install jev` 뒤 `CREATE EXTENSION jev CASCADE`, 또는 소스에서 `make install`, 또는 동봉된 Dockerfile. 회귀 테스트는 결정론적 mock API(`test/mock_api.py`)로 돌고 실제 API를 부르지 않는다.

눈에 띄는 것은 설치 경로 첫머리에 **에이전트 스킬**이 있다는 점이다. `npx skills add realZachi/pg-jev`로 스킬을 넣고 Claude Code·Codex·Cursor에 "이 서버에 pgjev 설치하고 설정해"라고 하면, 에이전트가 사전 점검(PG 버전, `plpython3u`, superuser) → 설치 → 확장 생성 → 키 배치 → 스모크 테스트까지 하고, 이후 비용을 의식한 `jev()` 쿼리 작성법까지 안다. 문서 사이트도 URL 끝에 `.md`를 붙이면 에이전트가 읽을 수 있게 해 두었다. 이 노트가 참고한 `references/` 문서들이 바로 그 스킬의 부속물이다.

## 버전 이력

- 0.1.0 (2026-09-17) — 함수 7종, 테이블 전체 선읽기(최대 `max_prefetch_rows`), 묶음 40, 동시성 6, 타임아웃 90초, mock API 회귀 테스트와 PG 14-17 CI.
- 0.2.0 (2026-09-18, 하루 뒤) — 스트리밍 읽기 선행, 영속 연결, 묶음 20·동시성 16·타임아웃 30으로 기본값 변경, `jev.keepalive`, 진행 `NOTICE`, 인터럽트 가능한 대기. 같은 쿼리가 8.5초 → 3.5초, `LIMIT 3`이 8.4초 → 0.6초, 입력 토큰 12% 절감. 묶음을 줄인 이유가 위의 위치 찾기 실험이다. "레코드가 조건을 만족한다"는 범용 `criteria`를 noul 질문에서 뺐더니 입력 토큰의 16%였는데 답은 하나도 안 바뀌었다는 대목도 있다.
- 0.2.1 (2026-10-03) — `*.typesafe.ai`가 아닌 엔드포인트는 키 없이 호출(이슈 #3). 외부 호출도 행당 과금도 없는 로컬 구성이 가능해졌다.

## 읽으며 짚어 둘 점

- 속도·비용 수치는 저자가 유럽에서 한 테이블(2,000행)로 잰 것이고, 정확도 실험은 **구조화 컬럼에서 정답을 만든** 쉬운 과제(직함, EU 회원국 여부, 문구 포함 여부)다. 이 실험이 보여 주는 것은 "묶음 크기에 따른 위치 찾기 오류"이지, 자유 텍스트에 대한 Jev의 판단 정확도가 아니다. 그쪽은 TypeSafe 문서와 제3자 비교(앞서 정리한 [29개 데이터셋 비교](/compendium/notes/typed-decisions-from-glm-flash/))를 봐야 한다.
- 비용 추정치는 엔드포인트가 무엇이든 TypeSafe 정가로 계산된다. 로컬 서버를 쓰면 `jev_stats()`의 달러 숫자는 의미가 없다.
- 저장소는 TypeSafe와 무관한 개인 프로젝트다(README 명시). 2026-09-17에 만들어져 이 노트를 쓰는 2026-10-08 기준 GitHub 별 1,063개, 포크 77개. GitHub이 언어를 Shell로 표시하지만 본체는 SQL 파일 안의 PL/Python이다.
- "질문 하나에 답 하나"가 아니라 "상태 하나에 질문 20개"로 묶는 설계, 그리고 그 묶음이 커질수록 위치 참조가 흔들린다는 관찰은 Jev에만 해당하는 이야기가 아니다. LLM에 레코드 배열을 넘겨 항목별 판단을 받는 어떤 파이프라인에도 같은 함정이 있고, 이 저장소는 그 한계를 실측으로 정했다는 점에서 참고할 만하다.

## 남는 생각

성향 모델을 운영하는 입장에서 흥미로운 건 쿼리 패턴 쪽이다. `jev_prob()`로 분포를 먼저 보고 임계값을 고르고, 0.5 근처를 뽑아 모호한 사례를 들여다보고, 확신도가 낮은 행은 사람에게 넘기라는 흐름은 모델 점수를 캠페인에 쓸 때 하는 일과 똑같다. 다른 점은 피처 엔지니어링과 학습이 없고 조건 문구가 그 자리를 대신한다는 것, 그리고 행 전체가 외부로 나간다는 것이다. 금융 데이터에 그대로 쓸 수 있는 물건은 아니지만, 로컬 Jev 호환 서버 옵션이 생긴 0.2.1부터는 "SQL 안에서 확률형 판단을 받는다"는 인터페이스 자체를 사내에서 실험해 볼 길은 열린 셈이다. 앞서 정리한 [기성 LLM의 logprob 한 자리를 읽는 기법](/compendium/notes/typed-decisions-from-glm-flash/)을 `/v1/systemone` 계약 뒤에 두면 같은 자리에 꽂힐 수 있겠다는 생각도 든다 — 이건 저장소가 아니라 내 추측이다.

## 함께 읽기

- [GLM-5.3-Flash를 Jev 같은 System One 모델로 바꾸기](/compendium/notes/typed-decisions-from-glm-flash/) — Jev가 무엇인지, 그리고 전용 모델 없이 같은 성질을 얻는 법
- [Laya — 33ms 비자기회귀 System 1 결정 엔진](/compendium/notes/laya-system1-decision-engine/) — pg-jev가 로컬 백엔드로 언급하는 stuntd 뒤의 모델
