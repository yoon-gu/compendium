#!/usr/bin/env python3
"""대본 나레이션에 나오는 영어 단어·약어를 뽑아 발음 검토표를 만든다(초안 대본을 쓴 직후 돌린다).

    python3 words.py <슬러그>      # → <슬러그>/words.md (단어 | 횟수 | 지금 읽기 | 제안 읽기 | 첫 등장 문맥)

띄어 쓴 영어 단어가 이어지면 한 덩어리(Jane Street, flow matching)로 본다. '지금 읽기'는 pronounce.tsv 에 있으면
그 읽기, 없으면 '(그대로)'. '제안 읽기'는 사람이(또는 Claude가) 채우고, 확정한 것만 pronounce.tsv 에 옮겨 적는다.
"""
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
slug = sys.argv[1]
text = (HERE / slug / "script.md").read_text(encoding="utf-8")
narr = [ln.strip() for ln in text[text.index("\n## "):].splitlines()
        if ln.strip() and not ln.strip().startswith((">", "##", "<!--"))]
fix = {a.lower(): b for a, b in (ln.split("\t") for ln in (HERE / "pronounce.tsv").read_text(encoding="utf-8").splitlines()
                                 if ln.strip() and not ln.startswith("#"))}
# 영문으로 시작하는 토큰(하이픈·점·숫자 포함: GPT-4, zero-inflated). 띄어쓰기로 이어진 영문 토큰은 한 덩어리
tok = r"[A-Za-z][A-Za-z0-9]*(?:[-.][A-Za-z0-9]+)*"
pat = re.compile(rf"(?<![A-Za-z0-9]){tok}(?: {tok})*")
count, first = Counter(), {}
for para in narr:
    for m in pat.finditer(para):
        w = m[0]
        count[w] += 1
        first.setdefault(w, para[max(0, m.start() - 20):m.end() + 20].replace("|", "/"))
rows = ["| 단어 | 횟수 | 지금 읽기 | 제안 읽기 | 첫 등장 문맥 |", "|---|---|---|---|---|"]
for w, n in sorted(count.items(), key=lambda kv: (-kv[1], kv[0].lower())):
    rows.append(f"| {w} | {n} | {fix.get(w.lower(), '(그대로)')} |  | …{first[w]}… |")
out = HERE / slug / "words.md"
out.write_text(f"# {slug} 나레이션 영어 단어 발음 검토표\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
print(f"{out}: {len(count)}개")
