// 장면 5: 에이전트마다 VM(커널까지 따로, 준비할 게 많다) vs 파드 안 네임스페이스(범위만 따로) → 버블랩 선택 → 커널은 공유.
import React from "react";
import { Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Vm: React.FC<Timing> = ({ marks }) => {
  const [vm, kernel, cost, narrow, pick, price] = [0, 1, 2, 3, 4, 5].map((i) => useAt(marks, i));
  const col = (x: number, title: string, a: number, hi: number) => (
    <>
      <Box x={x} y={0} w={420} h={440} a={a} ec={hi > 0.5 ? C.ink : C.line} fc={hi > 0.5 ? C.inkT : "#FFFFFF"} lw={3 + hi * 2} r={18} rise={false} />
      <Label x={x + 210} y={36} a={a} size={28} bold color={hi > 0.5 ? C.ink : C.txt} w={420}>{title}</Label>
    </>
  );
  return (
    <Stage>
      {col(0, "에이전트마다 VM", vm, 0)}
      {[0, 1, 2].map((k) => (
        <Box key={k} x={24 + k * 128} y={76} w={116} h={190} a={vm} ec={C.line} r={12} size={22} bold rise={false}>
          {`에이전트 ${k + 1}`}
          <span style={{ fontSize: 20, fontWeight: 800, color: C.ok, opacity: kernel, marginTop: 8 }}>커널</span>
        </Box>
      ))}
      <Label x={210} y={310} a={kernel} size={24} bold color={C.ok} w={400}>커널까지 따로 — 가장 단단하다</Label>
      <Label x={210} y={370} a={cost} size={22} color={C.bad} w={400}>이미지 · 볼륨 · 생성/종료를</Label>
      <Label x={210} y={404} a={cost} size={22} color={C.bad} w={400}>플랫폼에 엮어야 한다</Label>

      {col(468, "파드 안 네임스페이스", narrow, pick)}
      <Box x={492} y={76} w={372} h={190} a={narrow} ec={C.ink} r={12} rise={false} />
      {[0, 1, 2].map((k) => (
        <Box key={k} x={506 + k * 120} y={90} w={108} h={110} a={narrow} ec={C.warn} fc={C.warnT} r={10} size={20} bold rise={false}>
          {`에이전트 ${k + 1}`}
        </Box>
      ))}
      <Label x={678} y={234} a={narrow} size={22} bold color={C.gray} w={372}>커널 하나를 함께 쓴다</Label>
      <Label x={678} y={310} a={narrow} size={24} bold color={C.ink} w={400}>파일·통신 범위만 따로</Label>
      <Label x={678} y={370} a={pick} size={22} color={C.ink} w={400}>기존 워크스페이스를 그대로</Label>
      <Label x={678} y={404} a={pick} size={22} color={C.ink} w={400}>→ bubblewrap 선택</Label>

      <Box x={0} y={480} w={888} h={110} a={price} ec={C.warn} fc={C.warnT} size={26} bold>
        대가: 호스트 커널을 함께 쓴다
        <span style={{ fontSize: 23, fontWeight: 400, color: C.gray }}>VM 같은 커널 격리는 아니다</span>
      </Box>
    </Stage>
  );
};
