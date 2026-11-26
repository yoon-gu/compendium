// 장면 8-2: 키를 숨겨도 권한은 그대로 → 게이트웨이가 모델·도구 권한, 업무 서비스가 데이터 권한 → 서비스 권한 ≠ 문서 권한 → 허용된 곳으로 내보내기는 못 막는다.
import React from "react";
import { Box, C, Stage, Timing, useAt } from "../lib/ui";

export const Perms: React.FC<Timing> = ({ marks }) => {
  const [hide, same, gw, mcp, svc, doc, out] = [0, 1, 2, 3, 4, 5, 6].map((i) => useAt(marks, i));
  return (
    <Stage>
      <Box x={0} y={0} w={420} h={110} a={hide} ec={C.ok} fc={C.okT} size={28} bold color={C.ok}>키 숨김 ✓</Box>
      <Box x={468} y={0} w={420} h={110} a={same} ec={C.warn} fc={C.warnT} size={24} bold>
        그 키로 허용된 기능은
        <span style={{ fontSize: 22, fontWeight: 400 }}>그대로 쓸 수 있다</span>
      </Box>
      <Box x={0} y={140} w={888} h={120} a={gw} ec={C.ink} fc={C.inkT} lw={4} size={28} bold color={C.ink}>
        게이트웨이 — 모델 · 도구를 쓸 권한
        <span style={{ fontSize: 22, fontWeight: 400, color: C.gray, opacity: mcp }}>업무 도구는 MCP 게이트웨이를 거친다</span>
      </Box>
      <Box x={0} y={280} w={888} h={120} a={svc} ec={C.ink} fc={C.inkT} lw={4} size={28} bold color={C.ink}>
        업무 서비스 — 그 계정이 읽을 수 있는 데이터
        <span style={{ fontSize: 22, fontWeight: 400, color: C.gray, opacity: doc }}>서비스를 쓸 권한 ≠ 문서 하나를 읽을 권한</span>
      </Box>
      <Box x={0} y={440} w={888} h={130} a={out} ec={C.bad} fc={C.badT} size={26} bold color={C.bad}>
        읽은 데이터를 허용된 서비스로 내보내기
        <span style={{ fontSize: 22, fontWeight: 400 }}>이 구조만으로는 다 막지 못한다</span>
      </Box>
    </Stage>
  );
};
