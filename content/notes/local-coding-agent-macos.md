---
title: "macOS에서 로컬 코딩 에이전트 설정하기"
date: 2026-06-12
draft: false
source_url: "https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos"
author: "Kyle Howells"
tags: ["AI", "Coding Agent", "macOS", "llama.cpp", "Gemma", "Qwen", "Local LLM"]
summary: "Kyle Howells가 macOS에서 llama.cpp, Metal, Gemma 4 26B-A4B, MTP speculative decoding, multimodal projector, Pi 코딩 에이전트를 조합해 로컬 OpenAI 호환 코딩 에이전트를 구성한 과정을 정리한다. M1 Max에서 Gemma 4 + Q8 MTP draft model은 생성 속도를 58.2 tok/s에서 72.2 tok/s로 높였고, Qwen3.6은 더 강한 코딩 모델이지만 더 느린 대안으로 소개된다."
---

> **원문:** [How to Setup a Local Coding Agent on macOS](https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos) — Kyle Howells, 2026년 6월 12일
>
> 아래 글은 원문 글의 구조와 서술을 따라가며 한국어로 옮긴 것이다.

## macOS에서 로컬 코딩 에이전트 설정하기

*Gemma 4 26B-A4B와 Qwen3.6 35B-A3B를 llama.cpp, MTP speculative decoding, multimodal support, 그리고 Pi 코딩 에이전트와 함께 로컬에서 실행하기.*

최근 인터넷이 몇 번 끊기면서 코딩 에이전트 없이 stranded되는 일이 있었다. 그래서 Gemma 4용 [“Gemma 4 now runs 2x faster with MTP”](https://x.com/UnslothAI/status/2065107734916432189) Multi-Token Prediction 업데이트를 보고, 이를 로컬에서 돌려보기로 했다.

내가 원한 로컬 코딩 에이전트 설정은 다음과 같았다.

- Mac에서 실제로 쓸 수 있을 만큼 빨라야 한다.
- OpenAI 호환 API를 통해 동작해야 한다. 그래야 다른 도구에서도 사용할 수 있다.
- 가능하면 필요할 때 스크린샷/이미지도 처리할 수 있어야 한다. 그래야 에이전트가 만든 결과의 스크린샷을 다시 입력으로 줄 수 있다.

그리고 성공했다. 아래 영상은 실시간이다. 에이전트가 충분히 사용할 만한 속도로 응답하는 모습을 보여준다.

<video controls autoplay loop muted playsinline preload="metadata" title="Gemma 4 local coding agent short demo" style="display:block; width:100%; max-width:100%; max-height:70vh; height:auto; object-fit:contain; margin:1rem auto;">
  <source src="https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos/Gemma_4_-_Short.mp4" type="video/mp4">
  Gemma 4 local coding agent short demo: https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos/Gemma_4_-_Short.mp4
</video>

약간의 테스트 뒤 최종적으로 사용한 설정은 다음과 같다.

- macOS에서 Metal로 빌드한 [llama.cpp](https://github.com/ggml-org/llama.cpp)
- GGUF 형식의 Gemma 4 26B-A4B
- speculative decoding을 위한 Q8 MTP draft model
- Gemma 4 multimodal projector
- 터미널 코딩 에이전트로 [Pi](https://github.com/earendil-works/pi)

이 설정은 Apple M1 Max, 64GB unified memory, macOS 15.7.7에서 테스트했다.

# 모델

메인 모델은 `gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf`다.

Hugging Face 링크: [models/unsloth-gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/blob/main/gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf)

이 파일은 약 16GB다. MTP draft head와 multimodal projector를 포함하면 모델 폴더는 약 17GB가 된다.

벤치마크 프롬프트는 다음과 같았다.

```text
Write a compact Python function that parses a unified diff and returns the changed file paths. Then explain two edge cases.
```

각 벤치마크는 약 128토큰을 생성했다.

# 기준선: llama.cpp + Metal

먼저 Metal acceleration을 사용해 llama.cpp에서 메인 모델을 직접 실행했다.

```bash
repos/llama.cpp/build/bin/llama-cli \
  -m models/unsloth-gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf \
  -ngl 999 \
  -fa on \
  -c 4096 \
  -n 128
```

결과:

| Setup                               | Prompt tok/s | Generation tok/s |
|:------------------------------------|-------------:|-----------------:|
| Gemma 4 26B-A4B Q4, llama.cpp Metal |        298.0 |             58.2 |

초당 58토큰은 빠르지는 않지만 사용할 수는 있다. 하지만 코딩 에이전트 작업에서는 가능한 한 빠른 편이 좋다. 특히 에이전트가 많은 tool call을 수행할 때 그렇다.

# MTP Draft Model 추가하기

Gemma 4에는 이제 [MTP draft model](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/blob/main/MTP/gemma-4-26B-A4B-it-Q8_0-MTP.gguf)이 제공된다.

```text
MTP/gemma-4-26B-A4B-it-Q8_0-MTP.gguf
```

이 모델은 llama.cpp에서 speculative draft model로 로드할 수 있다.

```bash
repos/llama.cpp/build/bin/llama-cli \
  -m models/unsloth-gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf \
  --model-draft models/unsloth-gemma-4-26B-A4B-it-GGUF/MTP/gemma-4-26B-A4B-it-Q8_0-MTP.gguf \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  -ngl 999 \
  -fa on \
  -c 4096 \
  -n 128
```

MTP를 사용한 첫 실행은 4개의 draft token을 사용해 초당 69.2토큰이었다. 하지만 Unsloth의 [How to Run MTP Models](https://unsloth.ai/docs/models/mtp) 가이드에는 다음과 같은 메모가 있다.

> “우리는 `--spec-draft-n-max 2`가 가장 좋은 시작점이라는 점을 발견했다. 하지만 2가 최적이라고 가정하지 말라. 성능은 하드웨어에 따라 달라진다. 1부터 6까지 아무 값이나 시도하고, 시스템에서 가장 빠른 값을 사용하라.”

`--spec-draft-n-max`를 sweep한 뒤 가장 좋은 결과는 draft token 3개에서 초당 72.2토큰이었다.

| Setup                     | Prompt tok/s | Generation tok/s | Speedup |
|:--------------------------|-------------:|-----------------:|--------:|
| Main model only           |        298.0 |             58.2 |   1.00x |
| Main model + Q8 MTP draft |        295.6 |             72.2 |   1.24x |

유용한 점은 prompt processing은 사실상 동일하게 유지되었고, generation은 약 24% 개선되었다는 것이다.

# MTP 튜닝

`--spec-draft-n-max` 값을 1부터 6까지 테스트했다.

| `--spec-draft-n-max` | Prompt tok/s | Generation tok/s |
|---------------------:|-------------:|-----------------:|
|                    1 |        295.5 |             68.4 |
|                    2 |        299.1 |             72.0 |
|                    3 |        295.6 |             72.2 |
|                    4 |        297.3 |             70.7 |
|                    5 |        297.9 |             63.7 |
|                    6 |        296.3 |             61.2 |

내 M1 Max 머신에서는 `3`이 가장 빨랐고, `2`도 충분히 가까워서 둘 중 어느 쪽도 괜찮았다. 그보다 큰 값은 더 느려졌다.

# MLX 비교

Mac에서 모델을 실행할 때 llama.cpp와 MLX 중 어느 쪽이 더 빠른지 알아보기 위해 `mlx-lm`을 통해 MLX 모델도 테스트했다.

| Runtime               | Model                     | Generation tok/s |
|:----------------------|:--------------------------|-----------------:|
| llama.cpp Metal + MTP | Unsloth GGUF Q4 + Q8 MTP  |             72.2 |
| llama.cpp Metal       | Unsloth GGUF Q4           |             58.2 |
| MLX-LM                | Unsloth UD MLX 4-bit      |             45.8 |
| MLX-LM                | mlx-community 4-bit       |             43.9 |
| MLX-LM                | mlx-community OptiQ 4-bit |             38.1 |

나는 Mac에 최적화된 MLX가 가장 빠를 것이라고 생각했다.  
하지만 이 특정 설정에서는 llama.cpp가 MLX보다 빨랐고, MTP를 사용한 llama.cpp가 명확히 가장 좋은 선택이었다.

아마도 llama.cpp에 오랫동안 들어간 노력과 튜닝 덕분에, cross-platform임에도 macOS에 꽤 잘 최적화되어 있는 것 같다.

[gemma-4-swift-mlx](https://github.com/VincentGourbin/gemma-4-swift-mlx)를 통해 Gemma 4 MTP도 시도해 보았지만, 테스트한 26B 4-bit MLX checkpoint가 loader가 기대하는 weight key와 맞지 않았다. 이미 앞선 MLX 테스트가 있었기 때문에, 새 모델을 다시 다운로드하고 맞춰보는 대신 넘어갔다.

# 이미지 지원 추가하기

Pi에서는 스크린샷도 첨부할 수 있기를 원했다. 처음에 Pi용 local model entry는 모델을 text-only로 선언했다.

```json
"input": ["text"]
```

그 결과 Pi는 image tool output을 모델에 제대로 전달하지 않았다.

llama.cpp server도 multimodal 부분이 동작하려면 Gemma 4 multimodal projector가 필요하다. 단, [12B만 native multimodal](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemma-4-12b/)이다.

```text
mmproj-BF16.gguf
```

`--mmproj`와 함께 로드하면 llama.cpp는 multimodal support를 advertise하고, Pi는 이미지를 보낼 수 있다.

projector를 로드한 상태에서 text benchmark를 다시 실행해 속도가 바뀌지 않는지 확인했다.

| Setup                 | Projector          | Prompt tok/s | Generation tok/s |
|:----------------------|:-------------------|-------------:|-----------------:|
| llama.cpp Metal + MTP | none               |        120.3 |             71.4 |
| llama.cpp Metal + MTP | `mmproj-BF16.gguf` |        297.4 |             72.2 |

projector를 포함한 최종 실행에서는 text generation slowdown이 나타나지 않았다.

---

이제 설정 방법이다.

# llama.cpp 설치

의존성을 설치한다.

```bash
brew install cmake git tmux python@3.11
```

llama.cpp를 clone하고 build한다.

```bash
mkdir -p ~/Developer/ML-Models/Gemma4/repos
cd ~/Developer/ML-Models/Gemma4

git clone https://github.com/ggml-org/llama.cpp repos/llama.cpp

cd repos/llama.cpp
cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_METAL=ON \
  -DGGML_ACCELERATE=ON

cmake --build build --config Release -j
```

테스트한 build에는 다음이 포함되어 있었다.

```text
GGML_METAL=ON
GGML_ACCELERATE=ON
GGML_BLAS=ON
GGML_BLAS_VENDOR=Apple
```

# 모델 파일 다운로드

Python 환경을 만든다.

```bash
cd ~/Developer/ML-Models/Gemma4
python3.11 -m venv .venv
source .venv/bin/activate
pip install -U huggingface_hub hf_xet
```

파일을 다운로드한다.

```bash
mkdir -p models/unsloth-gemma-4-26B-A4B-it-GGUF

huggingface-cli download unsloth/gemma-4-26B-A4B-it-GGUF \
  gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf \
  mmproj-BF16.gguf \
  MTP/gemma-4-26B-A4B-it-Q8_0-MTP.gguf \
  --local-dir models/unsloth-gemma-4-26B-A4B-it-GGUF
```

최종적으로 다음 파일들이 있어야 한다.

```text
models/unsloth-gemma-4-26B-A4B-it-GGUF/
  gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf
  mmproj-BF16.gguf
  MTP/gemma-4-26B-A4B-it-Q8_0-MTP.gguf
```

# 로컬 서버 시작하기

최종 server command는 다음과 같다.

```bash
repos/llama.cpp/build/bin/llama-server \
  -m models/unsloth-gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf \
  --model-draft models/unsloth-gemma-4-26B-A4B-it-GGUF/MTP/gemma-4-26B-A4B-it-Q8_0-MTP.gguf \
  --mmproj models/unsloth-gemma-4-26B-A4B-it-GGUF/mmproj-BF16.gguf \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  -ngl 999 \
  -fa on \
  -c 65536 \
  --parallel 1 \
  --host 127.0.0.1 \
  --port 8080
```

OpenAI-compatible endpoint는 다음과 같다.

```text
http://127.0.0.1:8080/v1
```

나는 `tmux` 안에서 실행되도록 작은 `start_server.sh` wrapper를 사용했다.

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_NAME="${SESSION_NAME:-gemma4-server}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8080}"
CTX_SIZE="${CTX_SIZE:-65536}"
PARALLEL="${PARALLEL:-1}"

LLAMA_SERVER="$ROOT_DIR/repos/llama.cpp/build/bin/llama-server"
MODEL="$ROOT_DIR/models/unsloth-gemma-4-26B-A4B-it-GGUF/gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf"
DRAFT_MODEL="$ROOT_DIR/models/unsloth-gemma-4-26B-A4B-it-GGUF/MTP/gemma-4-26B-A4B-it-Q8_0-MTP.gguf"
MMPROJ="$ROOT_DIR/models/unsloth-gemma-4-26B-A4B-it-GGUF/mmproj-BF16.gguf"
LOG_FILE="$ROOT_DIR/logs/llama-server-mtp.log"

mkdir -p "$ROOT_DIR/logs"

tmux new-session -d -s "$SESSION_NAME" -c "$ROOT_DIR" \
  "$LLAMA_SERVER \
    -m '$MODEL' \
    --model-draft '$DRAFT_MODEL' \
    --mmproj '$MMPROJ' \
    --spec-type draft-mtp \
    --spec-draft-n-max 3 \
    -ngl 999 \
    -fa on \
    -c '$CTX_SIZE' \
    --parallel '$PARALLEL' \
    --host '$HOST' \
    --port '$PORT' \
    2>&1 | tee -a '$LOG_FILE'"
```

시작한다.

```bash
chmod +x start_server.sh
./start_server.sh
```

서버가 실행 중인지 확인한다.

```bash
curl http://127.0.0.1:8080/v1/models
```

# Pi 설정

Pi는 model provider를 다음 위치에서 읽는다.

```text
~/.pi/agent/models.json
```

local provider를 추가한다.

```json
{
  "providers": {
    "gemma4-local": {
      "name": "Gemma 4 Local",
      "baseUrl": "http://127.0.0.1:8080/v1",
      "api": "openai-completions",
      "apiKey": "local",
      "authHeader": false,
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        {
          "id": "gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf",
          "name": "Gemma 4 26B-A4B Q4 + MTP",
          "reasoning": false,
          "input": ["text", "image"],
          "contextWindow": 65536,
          "maxTokens": 8192,
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          }
        }
      ]
    }
  }
}
```

중요한 부분은 다음과 같다.

- `baseUrl`은 llama.cpp OpenAI-compatible server를 가리킨다.
- `api`는 `openai-completions`다.
- `authHeader`는 `false`다. 로컬 서버이기 때문이다.
- `input`에는 `text`와 `image`가 모두 포함되어야 한다. 그렇지 않으면 Pi가 모델을 text-only로 취급한다.

선택적으로 다음 파일에서 기본값으로 설정할 수 있다.

```text
~/.pi/agent/settings.json
```

```json
{
  "defaultProvider": "gemma4-local",
  "defaultModel": "gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf",
  "defaultThinkingLevel": "minimal"
}
```

그런 다음 Pi가 모델을 볼 수 있는지 확인한다.

```bash
pi --offline --list-models gemma
```

예상 출력:

```text
provider      model                               context  max-out  thinking  images
gemma4-local  gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf  65.5K    8.2K     no        yes
```

local model을 사용해 Pi를 실행한다.

```bash
pi --provider gemma4-local --model gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf
```

또는 non-interactive mode를 사용한다.

```bash
pi -p --provider gemma4-local --model gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf \
  "Explain what this repository does"
```

스크린샷의 경우:

```bash
pi -p @"/path/to/screenshot.png" "Describe this image and point out anything relevant to the UI"
```

# 최종 설정

최종 local coding-agent stack은 다음과 같았다.

| Layer                | Choice                               |
|:---------------------|:-------------------------------------|
| Inference runtime    | llama.cpp                            |
| macOS acceleration   | Metal + Accelerate                   |
| Main model           | `gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf` |
| Draft model          | `gemma-4-26B-A4B-it-Q8_0-MTP.gguf`   |
| MTP setting          | `--spec-draft-n-max 3`               |
| Multimodal projector | `mmproj-BF16.gguf`                   |
| Server               | `llama-server` on `127.0.0.1:8080`   |
| API                  | OpenAI-compatible `/v1`              |
| Coding agent         | Pi                                   |
| Pi model input       | `["text", "image"]`                  |

핵심 결론은 MTP draft model을 사용할 가치가 있다는 것이다. 이 머신에서는 Gemma 4를 초당 58.2토큰에서 72.2토큰으로 끌어올렸고, 동시에 local OpenAI-compatible server로 실행할 수 있을 만큼 설정을 단순하게 유지했다.

<video controls autoplay loop muted playsinline preload="metadata" title="Gemma 4 offline test" style="display:block; width:100%; max-width:100%; max-height:70vh; height:auto; object-fit:contain; margin:1rem auto;">
  <source src="https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos/Gemma_4_Offline_Test.mp4" type="video/mp4">
  Gemma 4 offline test: https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos/Gemma_4_Offline_Test.mp4
</video>

---

**P.S.** 어떤 사람들은 `Gemma 4 26B-A4B` 대신 `Qwen3.6 35B-A3B`를 쓰라고 제안했다. 내가 찾을 수 있는 benchmark에 따르면 Qwen은 Gemma 4보다 **훨씬** 좋은 coding agent다.  
하지만 더 느리기도 하다. `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` + `unsloth-Qwen3.6-35B-A3B-MTP-GGUF` + `mmproj-BF16.gguf` 조합은 초당 72토큰이 아니라 55토큰이 나온다. 기다리며 앉아 있어야 할 때는 꽤 큰 차이다.

모델을 다운로드한다.

```bash
mkdir -p models/unsloth-Qwen3.6-35B-A3B-MTP-GGUF

huggingface-cli download unsloth/Qwen3.6-35B-A3B-MTP-GGUF \
  Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
  mmproj-BF16.gguf \
  --local-dir models/unsloth-Qwen3.6-35B-A3B-MTP-GGUF
```

서버를 시작한다.

```bash
LLAMA_SERVER=/Users/kylehowells/Developer/ML-Models/Gemma4/repos/llama.cpp/build/bin/llama-server

$LLAMA_SERVER \
  -m models/unsloth-Qwen3.6-35B-A3B-MTP-GGUF/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf \
  --mmproj models/unsloth-Qwen3.6-35B-A3B-MTP-GGUF/mmproj-BF16.gguf \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  -ngl 999 \
  -fa on \
  -c 65536 \
  --parallel 1 \
  --host 127.0.0.1 \
  --port 8081
```

Pi Config:

```json
{
  "providers": {
    "qwen36-local": {
      "name": "Qwen3.6 Local",
      "baseUrl": "http://127.0.0.1:8081/v1",
      "api": "openai-completions",
      "apiKey": "local",
      "authHeader": false,
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false
      },
      "models": [
        {
          "id": "Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf",
          "name": "Qwen3.6 35B-A3B Q4 + MTP",
          "reasoning": true,
          "input": ["text", "image"],
          "contextWindow": 65536,
          "maxTokens": 8192,
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          }
        }
      ]
    }
  }
}
```

<video controls autoplay loop muted playsinline preload="metadata" title="Qwen 3.6 offline test" style="display:block; width:100%; max-width:100%; max-height:70vh; height:auto; object-fit:contain; margin:1rem auto;">
  <source src="https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos/Qwen_3.6_-_Offline_Test.mp4" type="video/mp4">
  Qwen 3.6 offline test: https://ikyle.me/blog/2026/how-to-setup-a-local-coding-agent-on-macos/Qwen_3.6_-_Offline_Test.mp4
</video>

## 참고 자료

- [unsloth.ai/docs/models/qwen3.6](https://unsloth.ai/docs/models/qwen3.6)
- [unsloth.ai/docs/models/gemma-4](https://unsloth.ai/docs/models/gemma-4)
- [unsloth.ai/docs/models/mtp](https://unsloth.ai/docs/models/mtp)
- [github.com/ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- [github.com/earendil-works/pi](https://github.com/earendil-works/pi)
- [Introducing Gemma 4 12B: a unified, encoder-free multimodal model](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemma-4-12b/)
- [“MTP enables Google Gemma 4 run 약 1.4–2.2× faster with no accuracy loss”](https://x.com/UnslothAI/status/2065107734916432189)
- [unsloth/gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF)
- [unsloth/Qwen3.6-35B-A3B-MTP-GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF)
