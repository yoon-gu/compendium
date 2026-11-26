// 장면 12-2: 모든 문제를 한 모델로 풀 수는 없다 → 그래도 과제마다·상품마다 늘던 트리들이 하나로 모일 수 있을까 → 질문은 계속 는다. 캔버스 888x560.
import React from "react";
import { Box, C, Label, Stage, Timing, Tree, mix, useAt } from "../lib/ui";

export const Closing: React.FC<Timing> = ({ marks }) => {
  const [not1, others, many, merge, grow] = [0, 1, 2, 3, 4].map((i) => useAt(marks, i, i === 3 ? 1.4 : 0.6));
  return (
    <Stage>
      <Label x={444} y={26} a={not1} size={34} bold w={888}>모든 문제를 한 모델로 풀 수는 없다</Label>
      <Label x={444} y={76} a={others} size={27} color={C.gray} w={888}>토스도 문제에 따라 다른 모델을 함께 쓴다</Label>
      {Array.from({ length: 3 }).map((_, i) =>
        Array.from({ length: 7 }).map((__, j) => {
          const k = i * 7 + j;
          const x = mix(84 + j * 120, 444, merge), y = mix(170 + i * 86, 300, merge);
          return <Tree key={k} x={x} y={y} s={mix(0.8, 0.3, merge)} a={Math.max(0, Math.min(1, many * 3 - k / 10)) * (1 - merge)} />;
        }),
      )}
      <Box x={194} y={250} w={500} h={110} a={merge} ec={C.ink} fc={C.inkT} lw={4} size={34} bold color={C.ink}>
        하나로 묶을 수 있을까?
      </Box>
      <Box x={94} y={440} w={700} h={84} a={grow} ec={C.warn} fc={C.warnT} r={42} size={30} bold>
        회사가 크는 한 질문은 계속 는다
      </Box>
    </Stage>
  );
};
