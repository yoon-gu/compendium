// 장면 7: 사례 2 — 과제 셋(분류 하나·수치 둘) → 전에는 수백 개 트리 모델 → 유저와 상품들을 한 묶음으로 받아 전문가 셋을 붙인다 → 처음 보는 상품도. 캔버스 888x700.
import React from "react";
import { Arrow, Box, C, Card, Stage, Timing, useAt } from "../lib/ui";

const TASKS = [
  { h: "① 분류", sub: "예 / 아니오" },
  { h: "② 수치", sub: "①이 예일 때" },
  { h: "③ 수치", sub: "①이 예일 때" },
];
const PAINS = ["과제 × 상품 = 트리 모델 수백 개", "새 상품마다 모델을 새로 학습", "상품은 처음보다 3배 넘게 늘었다"];
const EXPERTS = [
  { t: "공유", ec: C.ink, fc: C.inkT, c: C.ink },
  { t: "과제별", ec: C.warn, fc: C.warnT, c: C.txt },
  { t: "상품 종류별", ec: C.ok, fc: C.okT, c: C.ok },
];

export const Case2: React.FC<Timing> = ({ marks }) => {
  const a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => useAt(marks, i));
  const [, , , , , , inp, match, exp, kind, fresh] = a;
  const taskA = [a[0], a[1], a[2]];
  return (
    <Stage>
      {TASKS.map((t, k) => (
        <React.Fragment key={t.h}>
          <Card x={k * 304} y={0} w={280} h={120} a={k === 0 ? Math.max(a[0], a[1]) : a[2]} head={t.h} sub={[t.sub]} ec={k === 0 && taskA[1] > 0.5 && a[2] < 0.5 ? C.ink : C.line} hs={32} />
          {k > 0 && <Arrow x1={k * 304 - 22} y1={60} x2={k * 304 - 4} y2={60} a={a[2]} color={C.gray} lw={3} />}
        </React.Fragment>
      ))}

      {/* 전: 아픈 곳 셋 */}
      {PAINS.map((p, k) => (
        <Box key={p} x={44} y={190 + k * 110} w={800} h={84} a={a[3 + k] * (1 - inp)} ec={C.bad} fc={C.badT} r={42} size={30} bold color={C.bad}>
          {p}
        </Box>
      ))}

      {/* 후: 한 묶음 모델 */}
      <Arrow x1={444} y1={196} x2={444} y2={130} a={exp} />
      {EXPERTS.map((e, k) => {
        const hi = k === 2 ? kind : 0;
        return (
          <Box key={e.t} x={k * 304} y={206} w={280} h={110} a={exp} ec={e.ec} fc={e.fc} lw={3 + hi * 3} size={30} bold color={e.c}>
            {e.t}
            <br />
            전문가
            {k === 2 && <span style={{ fontSize: 22, fontWeight: 400, opacity: kind, color: C.ok }}>비슷한 상품끼리 나눠 쓴다</span>}
          </Box>
        );
      })}
      <Arrow x1={444} y1={388} x2={444} y2={326} a={exp} />
      <Box x={144} y={398} w={600} h={92} a={match} ec={C.ink} fc={C.inkT} lw={4} size={32} bold color={C.ink}>
        이 유저 × 이 상품
      </Box>
      <Arrow x1={150} y1={562} x2={300} y2={500} a={match} />
      <Arrow x1={738} y1={562} x2={588} y2={500} a={match} />
      <Card x={0} y={570} w={300} h={130} a={inp} head="유저" sub={["한 번 요약"]} />
      <Card x={588} y={570} w={300} h={130} a={inp} head="상품들" ec={fresh > 0.5 ? C.ink : C.line} lw={3 + fresh * 2}
        sub={[<span key="s" style={{ color: fresh > 0.5 ? C.ink : C.gray, fontWeight: fresh > 0.5 ? 800 : 400 }}>{fresh > 0.5 ? "처음 보는 상품도 바로" : "상품마다 요약"}</span>]} />
    </Stage>
  );
};
