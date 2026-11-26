// 장면 11: 메타는 수천 개 모델을 비슷한 것끼리 묶었다(점이 무리로 모인다) → 무작정 합치면 안 된다 → 토스가 묶은 단위 → 평가 기준부터. 캔버스 888x690.
import React from "react";
import { Box, C, Card, Label, Stage, Timing, mix, useAt } from "../lib/ui";

// 흩어진 점 48개 → 네 무리. 위치는 고정된 의사 난수.
const DOTS = Array.from({ length: 48 }).map((_, k) => {
  const r = (n: number) => ((Math.sin(k * 12.9898 + n * 78.233) * 43758.5453) % 1 + 1) % 1;
  const g = k % 4;
  return { x0: 40 + r(1) * 520, y0: 70 + r(2) * 110, x1: 80 + g * 140 + (r(3) - 0.5) * 50, y1: 125 + (r(4) - 0.5) * 50 };
});

export const Group: React.FC<Timing> = ({ marks }) => {
  const [meta, merge, infra, bad, user, prod, eval_, some] = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => useAt(marks, i, i === 1 ? 1.6 : 0.6));
  return (
    <Stage>
      <div style={{ position: "absolute", left: 0, top: 0, width: 888, height: 200, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${C.line}`, background: "#FFFFFF", opacity: meta }} />
      <Label x={24} y={34} a={meta} size={28} bold align="left" w={600}>Meta Lattice (KDD 2026) · 광고 추천</Label>
      {DOTS.map((d, k) => (
        <div key={k} style={{ position: "absolute", left: mix(d.x0, d.x1, merge) - 7, top: mix(d.y0, d.y1, merge) - 7, width: 14, height: 14, borderRadius: 7, background: C.ink, opacity: meta * 0.85 }} />
      ))}
      <Label x={740} y={92} a={merge} size={28} bold color={C.ink} w={280}>수천 개 → 몇 개</Label>
      <Label x={740} y={144} a={infra} size={24} color={C.gray} w={280}>품질 ↑ · 인프라 약 20% ↓</Label>

      <Box x={0} y={224} w={888} h={100} a={bad} ec={C.bad} fc={C.badT} size={34} bold color={C.bad}>
        무작정 합치면 품질이 떨어진다
      </Box>

      <Card x={0} y={350} w={420} h={150} a={user} head="같은 유저의 행동끼리" sub={["사례 1 · 수십 개 금융 행동"]} ec={C.ink} fc={C.inkT} hc={C.ink} hs={30} ss={24} />
      <Card x={468} y={350} w={420} h={150} a={prod} head="같은 상품의 과제끼리" sub={["사례 2 · 분류 하나 + 수치 둘"]} ec={C.ink} fc={C.inkT} hc={C.ink} hs={30} ss={24} />

      <Box x={0} y={526} w={888} h={164} a={eval_} ec={C.warn} fc={C.warnT} size={32} bold>
        합치기 전에 과제별 평가 기준부터
        <span style={{ fontSize: 26, fontWeight: 400, color: C.gray, opacity: some, marginTop: 10 }}>평균은 좋아져도 일부 과제는 나빠질 수 있다</span>
      </Box>
    </Stage>
  );
};
