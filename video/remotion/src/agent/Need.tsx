// 장면 2: 지난달 기준으로 비교해 달라 → 망분리(내부망 | 인터넷) → 데이터는 못 나간다 → 에이전트가 안에서 → 다 열 수는 없다 → 이어 가기.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Need: React.FC<Timing> = ({ marks }) => {
  const [ask, wall, data, agent, closed, prompt, cont] = [0, 1, 2, 3, 4, 5, 6].map((i) => useAt(marks, i));
  const files = [[70, 330], [180, 400], [70, 470], [200, 520], [430, 330], [470, 470]];
  return (
    <Stage>
      <Box x={0} y={0} w={888} h={96} a={ask} ec={C.ink} fc={C.inkT} r={48} size={28} bold color={C.ink}>
        “지난달과 같은 기준으로 이번 달도 비교해줘”
      </Box>
      {/* 내부망 | 인터넷 */}
      <Box x={0} y={130} w={600} h={440} a={wall} ec={C.ink} fc="#FFFFFF" lw={4} r={18} rise={false} />
      <Label x={24} y={160} a={wall} size={28} bold color={C.ink} align="left" w={400}>내부망</Label>
      <Box x={660} y={130} w={228} h={440} a={wall} ec={C.line} fc={C.soft} r={18} rise={false} />
      <Label x={774} y={160} a={wall} size={28} bold color={C.gray} w={228}>인터넷</Label>
      <div style={{ position: "absolute", left: 622, top: 120, width: 16, height: 460, background: C.txt, opacity: wall, borderRadius: 4 }} />
      {/* 데이터는 못 나간다 */}
      <Box x={300} y={200} w={200} h={90} a={data} ec={C.warn} fc={C.warnT} size={28} bold>데이터</Box>
      <Arrow x1={505} y1={245} x2={700} y2={245} a={data} color={C.bad} lw={4} dash />
      <Label x={630} y={245} a={data} size={64} bold color={C.bad} w={80}>✕</Label>
      {/* 에이전트가 안에서 */}
      <Box x={290} y={380} w={220} h={90} a={agent} ec={C.ink} fc={C.inkT} lw={4} size={28} bold color={C.ink}>에이전트</Box>
      {files.map(([x, y], k) => {
        const ok = k === 4 || k === 5;
        return (
          <React.Fragment key={k}>
            <Box x={x} y={y} w={90} h={56} a={agent * (ok ? 1 : 1 - closed * 0.65)} ec={ok ? C.ink : C.line} r={8} size={22} color={C.gray} rise={false}>파일</Box>
          </React.Fragment>
        );
      })}
      <Label x={300} y={545} a={closed} size={25} bold color={C.bad} w={600}>내부망 전체를 열어 줄 수는 없다</Label>
      <Box x={660} y={300} w={228} h={150} a={prompt} ec={C.bad} fc={C.badT} size={24} bold color={C.bad}>
        프롬프트로
        <br />
        “조심해” ✕
      </Box>
      {/* 이어 가기 */}
      <Box x={0} y={600} w={400} h={90} a={cont} ec={C.line} size={26} color={C.gray}>지난달 코드 · 기준</Box>
      <Arrow x1={410} y1={645} x2={480} y2={645} a={cont} />
      <Box x={488} y={600} w={400} h={90} a={cont} ec={C.ink} fc={C.inkT} size={26} bold color={C.ink}>이번 달 분석</Box>
    </Stage>
  );
};
