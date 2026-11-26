// 장면 7: 대화마다 폴더를 따로 주면 복사·최신본 관리 → 작업 파일은 함께, 대화 상태는 세션마다 → 조건은 알려 줘야 → 옛 버전으로 안 돌아감·동시 수정 충돌.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Sessions: React.FC<Timing> = ({ marks }) => {
  const [sep, copy, diff, shared, code, own, tell, oldv, clash] = [0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => useAt(marks, i));
  const before = sep * (1 - diff);
  return (
    <Stage>
      {/* 전: 대화마다 폴더 */}
      {["10월 대화", "11월 대화"].map((s, k) => (
        <React.Fragment key={s}>
          <Box x={k * 468} y={20} w={420} h={90} a={before} ec={C.line} size={28} bold>{s}</Box>
          <Box x={k * 468} y={140} w={420} h={90} a={before} ec={C.line} size={24} color={C.gray}>{k ? "compare.py (사본?)" : "compare.py"}</Box>
        </React.Fragment>
      ))}
      <Label x={444} y={290} a={copy * (1 - diff)} size={26} bold color={C.bad} w={888}>복사하고, 어느 사본이 최신인지 사람이 챙긴다</Label>

      {/* 후: 파일은 함께, 상태는 따로 */}
      <Box x={0} y={0} w={888} h={80} a={diff} ec={C.ink} fc={C.inkT} lw={4} size={30} bold color={C.ink}>분석 에이전트</Box>
      {["10월 대화", "11월 대화"].map((s, k) => (
        <React.Fragment key={s}>
          <Box x={k * 468} y={110} w={420} h={84} a={diff} ec={C.line} size={28} bold>{s}</Box>
          <Box x={k * 468 + 30} y={214} w={360} h={84} a={own} ec={C.warn} fc={C.warnT} size={24} bold>{`대화 상태 ${k + 1}`}<span style={{ fontSize: 20, fontWeight: 400, color: C.gray }}>세션마다 따로</span></Box>
          <Arrow x1={k * 468 + 210} y1={300} x2={444 + (k ? 60 : -60)} y2={372} a={shared} />
        </React.Fragment>
      ))}
      <Box x={194} y={380} w={500} h={110} a={shared} ec={C.ink} fc="#FFFFFF" lw={4} size={28} bold color={C.ink}>
        작업 폴더 (함께)
        <span style={{ fontSize: 24, fontWeight: 400, color: C.txt, opacity: code }}>compare.py · 참고 자료</span>
      </Box>
      <Label x={444} y={530} a={tell} size={24} color={C.gray} w={888}>새 대화에는 지난 분석 조건을 알려 줘야 한다</Label>
      <Box x={0} y={570} w={420} h={110} a={oldv} ec={C.warn} fc={C.warnT} size={24} bold>지난 대화를 열어도<span style={{ fontSize: 22, fontWeight: 400 }}>파일은 지금 버전</span></Box>
      <Box x={468} y={570} w={420} h={110} a={clash} ec={C.bad} fc={C.badT} size={24} bold color={C.bad}>동시에 고치면<span style={{ fontSize: 22, fontWeight: 400 }}>충돌할 수 있다</span></Box>
    </Stage>
  );
};
