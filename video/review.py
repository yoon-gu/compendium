#!/usr/bin/env python3
"""빌드한 영상을 화면별로 훑어보며 메모를 남기는 검토 페이지를 만든다.

    python3 video/review.py <슬러그> --script=script-2.md --wide     # → <슬러그>/work/review-2/index.html

왼쪽은 영상(out/…-small.mp4가 있으면 그걸, 없으면 원본), 오른쪽은 화면마다 캡처(70% 지점)·화면 글·나레이션·메모 칸.
화면 길이는 마지막 빌드의 work/slides-*/list.txt 에서 읽는다(빌드한 목소리 기준). 메모는 브라우저에 저장되고 '메모 모아 복사'로 한꺼번에 옮긴다.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

sys.argv = ["build.py"] + sys.argv[1:]
import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location("build", Path(__file__).with_name("build.py"))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

text = b.SCRIPT.read_text(encoding="utf-8")
_, scenes = b.parse(text)
titles = dict(re.findall(r"^## (\d+) \| .+? \| (.+)$", text, re.M))
tag = re.sub(r"^script-?|\.md$", "", b.SCRIPT.name) or "1"
kind = f"-{tag}" if tag != "1" else ""
video = next(p for p in (b.OUT.with_name(b.OUT.stem + "-small.mp4"), b.OUT) if p.exists())
lst = next(b.WORK.glob(f"slides{kind}*/list.txt"))
secs = [float(x) for x in re.findall(r"^duration ([\d.]+)", lst.read_text(), re.M)]
frames = [(s, f) for s in scenes for f in s["frames"]]
assert len(secs) == len(frames), (len(secs), len(frames))
starts = [sum(secs[:i]) for i in range(len(secs))]

out = b.WORK / f"review-{tag}"
(out / "img").mkdir(parents=True, exist_ok=True)
for i, (t0, d) in enumerate(zip(starts, secs), 1):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t0 + d * 0.7:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", "scale=960:-1", "-q:v", "4", str(out / f"img/s-{i:02d}.jpg")], check=True)

md = lambda s: re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(s))
mmss = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"
body, nav, seen = [], [], set()
for i, ((s, f), t0, d) in enumerate(zip(frames, starts, secs), 1):
    if f is s["frames"][0]:
        body.append(f'<h2 id="sec-{i}">{html.escape(s["label"])} · {html.escape(titles.get(str(s["n"]), ""))}</h2>')
        if s["label"] not in seen:
            seen.add(s["label"]); nav.append(f'<a href="#sec-{i}">{html.escape(s["label"])}</a>')
    media = [ln for ln in f["slide"][1:] if ln.startswith("![")]
    lines = "".join(f"<div>{md(ln)}</div>" for ln in f["slide"][1:] if not ln.startswith("!["))
    narr = "".join("<p>" + html.escape(p).replace("‖", "<span class=pause>‖</span>") + "</p>" for p in f["narration"])
    chars = sum(len(p.replace("‖", "").strip()) for p in f["narration"])
    body.append(f'''<article id="s{i}" data-t="{t0:.2f}">
  <div class="meta"><button class="seek">{mmss(t0)}</button> <span>화면 {i}/{len(frames)} · {d:.0f}초 · {chars}자</span></div>
  <img src="img/s-{i:02d}.jpg" loading="lazy" class="seek">
  <div class="slide"><div class="title">{md(f["slide"][0].replace(" / ", " / "))}</div>{lines}
  <div class="media">{html.escape(" ".join(media))}</div></div>
  <div class="narr">{narr}</div>
  <textarea placeholder="메모 (자동 저장)" data-i="{i}"></textarea>
</article>''')

CSS = """:root{--ink:#3F7A66;--bg:#FAFAF7;--fg:#222;--mut:#777;--card:#fff;--line:#e3e3dd}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,"Apple SD Gothic Neo",sans-serif}
.wrap{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;max-width:1700px;margin:auto;padding:16px}
.left{position:sticky;top:16px;align-self:start} video{width:100%;border-radius:6px;background:#000}
.left h1{font-size:18px;margin:12px 0 4px} .left nav a{margin-right:10px;color:var(--ink)} .info{color:var(--mut);font-size:13px}
.toolbar button{margin:8px 6px 0 0}
h2{color:var(--ink);font-size:17px;border-bottom:2px solid var(--ink);padding-bottom:4px;margin:28px 0 8px}
article{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin-bottom:14px}
article.now{outline:3px solid var(--ink)}
article img{width:100%;border-radius:4px;cursor:pointer;display:block}
.meta{color:var(--mut);font-size:13px;margin-bottom:6px} .meta button{font-weight:600;color:var(--ink);cursor:pointer}
.slide{background:#f3f3ee;border-radius:4px;padding:8px 10px;margin:8px 0;font-size:14px} .slide .title{font-weight:600}
.media{color:var(--mut);font-family:ui-monospace,monospace;font-size:12px}
.narr p{margin:6px 0} .pause{color:#c0392b;font-weight:700}
textarea{width:100%;box-sizing:border-box;min-height:44px;font:inherit;border:1px solid var(--line);border-radius:4px;padding:6px}
textarea.has{border-color:var(--ink);background:#f1f7f4}
@media (max-width:900px){.wrap{grid-template-columns:1fr}.left{position:static}}"""
JS = f"""const v=document.getElementById('v'), arts=[...document.querySelectorAll('article')];
const K='{b.SLUG}-{tag}-review', load=()=>{{try{{return JSON.parse(localStorage.getItem(K))||{{}}}}catch(e){{return {{}}}}}};
let notes=load();
const mark=()=>{{document.querySelectorAll('textarea').forEach(t=>t.classList.toggle('has',!!t.value.trim()));
  document.getElementById('cnt').textContent=Object.values(notes).filter(x=>x.trim()).length+'개 메모';}};
document.querySelectorAll('textarea').forEach(t=>{{t.value=notes[t.dataset.i]||'';
  t.oninput=()=>{{notes[t.dataset.i]=t.value;try{{localStorage.setItem(K,JSON.stringify(notes))}}catch(e){{}};mark();}};}});
mark();
document.querySelectorAll('.seek').forEach(x=>x.onclick=()=>{{v.currentTime=+x.closest('article').dataset.t;v.play();}});
v.ontimeupdate=()=>{{let cur=null;for(const a of arts)if(+a.dataset.t<=v.currentTime)cur=a;arts.forEach(a=>a.classList.toggle('now',a===cur));}};
document.getElementById('copy').onclick=()=>{{const out=arts.map((a,i)=>{{const n=(notes[i+1]||'').trim();
  return n?`- {tag}편 화면 ${{i+1}} (${{a.querySelector('.meta button').textContent}}) ${{a.querySelector('.title').textContent}}: ${{n}}`:''}}).filter(Boolean).join('\\n');
  navigator.clipboard.writeText(out||'(메모 없음)');}};"""
total = sum(secs)
page = f"""<!doctype html><html lang="ko"><meta charset="utf-8"><title>{b.SLUG} {tag}편 검토</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style>
<div class="wrap"><div class="left">
<video id="v" controls preload="metadata" src="{Path("../../out") / video.name}"></video>
<h1>{b.SLUG} · {tag}편</h1>
<div class="info">{len(frames)}화면 · {mmss(total)} · 목소리 {b.VOICE} · 캡처는 각 화면 70% 지점. 시각이나 그림을 누르면 영상이 그 화면으로 넘어갑니다.</div>
<nav>{"".join(nav)}</nav>
<div class="toolbar"><button id="copy">메모 모아 복사</button><span id="cnt" class="info"></span></div>
</div><div class="right">{"".join(body)}</div></div>
<script>{JS}</script></html>"""
(out / "index.html").write_text(page, encoding="utf-8")
print(out / "index.html", f"· {len(frames)}화면 · {mmss(total)} · {video.name}")
