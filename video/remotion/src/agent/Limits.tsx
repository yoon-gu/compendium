// 장면 12-2: 원문이 그어 둔 선 셋 — 막는다 ≠ 검증한다, 키를 숨긴다 ≠ 권한을 줄인다, 대화를 잇는다 ≠ 작업을 되돌린다 → 못 막는 것까지 적는다.
import React from "react";
import { Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

const PAIRS = [
  ["접근을 막는다", "결과를 검증한다"],
  ["키를 숨긴다", "권한을 줄인다"],
  ["대화를 잇는다", "작업을 되돌린다"],
];

export const Limits: React.FC<Timing> = ({ marks }) => {
  const [lines, p1, p2, p3, write] = [0, 1, 2, 3, 4].map((i) => useAt(marks, i));
  const pa = [p1, p2, p3];
  return (
    <Stage>
      {PAIRS.map(([l, r], i) => (
        <React.Fragment key={l}>
          <Box x={0} y={i * 130} w={380} h={104} a={pa[i]} ec={C.ok} fc={C.okT} size={28} bold color={C.ok}>{l}</Box>
          <Label x={444} y={i * 130 + 52} a={pa[i]} size={44} bold color={C.bad} w={100}>≠</Label>
          <Box x={508} y={i * 130} w={380} h={104} a={pa[i]} ec={C.warn} fc={C.warnT} size={28} bold>{r}</Box>
        </React.Fragment>
      ))}
      <Label x={444} y={420} a={lines * (1 - p1)} size={28} bold color={C.gray} w={888}>원문이 곳곳에 그어 둔 선</Label>
      <Box x={44} y={420} w={800} h={110} a={write} ec={C.ink} fc={C.inkT} lw={4} r={55} size={28} bold color={C.ink}>
        울타리가 못 막는 것까지 적어 둔다
      </Box>
    </Stage>
  );
};
