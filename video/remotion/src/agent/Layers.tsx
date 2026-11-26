// 장면 3-2: 울타리 두 겹 — 쿠버네티스 위 사용자별 파드(OpenSandbox) → 파드 안 에이전트별 하니스(bubblewrap) → 네임스페이스가 나누는 것 셋.
import React from "react";
import { Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Layers: React.FC<Timing> = ({ marks }) => {
  const [two, osb, pods, bwrap, perAgent, ns] = [0, 1, 2, 3, 4, 5].map((i) => useAt(marks, i));
  return (
    <Stage>
      <Box x={0} y={0} w={888} h={500} a={two} ec={C.line} fc={C.soft} r={20} rise={false} />
      <Label x={24} y={30} a={osb} size={26} bold color={C.gray} align="left" w={840}>쿠버네티스 · OpenSandbox (바깥 울타리)</Label>
      {["사용자 A", "사용자 B"].map((u, k) => {
        const x = 24 + k * 432;
        return (
          <React.Fragment key={u}>
            <Box x={x} y={64} w={408} h={410} a={pods} ec={C.ink} fc="#FFFFFF" lw={4} r={18} rise={false} />
            <Label x={x + 20} y={96} a={pods} size={26} bold color={C.ink} align="left" w={380}>{u}의 파드</Label>
            {["분석 에이전트", "문서 에이전트"].map((g, j) => (
              <Box key={g} x={x + 24} y={136 + j * 164} w={360} h={140} a={perAgent} ec={C.warn} fc={C.warnT} lw={3 + bwrap * 2} r={14} size={26} bold rise={false}>
                하니스
                <span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>{g} · bubblewrap</span>
              </Box>
            ))}
          </React.Fragment>
        );
      })}
      <Label x={444} y={540} a={bwrap} size={26} bold color={C.warn} w={888}>안쪽 울타리: 에이전트마다 하니스를 따로 가둔다</Label>
      {["보이는 파일", "보이는 프로세스", "네트워크"].map((t, k) => (
        <Box key={t} x={k * 304} y={600} w={280} h={90} a={ns} ec={C.ink} fc={C.inkT} r={45} size={26} bold color={C.ink}>{t}</Box>
      ))}
    </Stage>
  );
};
