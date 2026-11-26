// 장면 6-2: 온라인 A/B 결과 — 상품군마다 숫자가 세어 올라간다 → 널리 쓰인다. 캔버스 888x690.
import React from "react";
import { Box, C, Label, Stage, Timing, mix, useAt } from "../lib/ui";

export const Online: React.FC<Timing> = ({ marks }) => {
  const [ab, g1, n1, n2, g2, n3, n4, wide] = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => useAt(marks, i, i === 2 || i === 5 ? 1.2 : 0.6));
  const cards = [
    { x: 0, a: g1, name: "상품군 1", big1: `−${Math.round(mix(0, 35, n1))}%`, a1: n1, l1: "불필요한 발송", big2: "약 2배", a2: n2, l2: "발송 대비 효율" },
    { x: 468, a: g2, name: "상품군 2", big1: `${mix(1, 1.7, n3).toFixed(1)}배`, a1: n3, l1: "클릭률", big2: "수 배", a2: n4, l2: "최종 전환율" },
  ];
  return (
    <Stage>
      {cards.map((c) => (
        <React.Fragment key={c.x}>
          <Box x={c.x} y={0} w={420} h={520} a={c.a} ec={C.ink} fc={C.inkT} lw={4} />
          <Label x={c.x + 210} y={60} a={c.a} size={36} bold color={C.ink} w={420}>{c.name}</Label>
          <Label x={c.x + 210} y={186} a={c.a1} size={92} bold color={C.ink} w={420}>{c.big1}</Label>
          <Label x={c.x + 210} y={262} a={c.a1} size={30} color={C.gray} w={420}>{c.l1}</Label>
          <Label x={c.x + 210} y={384} a={c.a2} size={68} bold color={C.ink} w={420}>{c.big2}</Label>
          <Label x={c.x + 210} y={450} a={c.a2} size={30} color={C.gray} w={420}>{c.l2}</Label>
        </React.Fragment>
      ))}
      <Label x={444} y={562} a={ab} size={28} color={C.gray} w={888}>기존 모델과 A/B 테스트 · 둘 다 p &lt; 0.001</Label>
      <Box x={84} y={606} w={720} h={80} a={wide} ec={C.ok} fc={C.okT} r={40} size={30} bold color={C.ok}>
        마케팅 타기팅에 널리 쓰인다
      </Box>
    </Stage>
  );
};
