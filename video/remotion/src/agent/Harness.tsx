// 장면 3: 모델은 글만 → 하니스가 도구를 실행하고 결과를 돌려준다 → 오류도 → 뇌와 몸 → 몸이 너무 자유로우면 아무 파일이나.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Harness: React.FC<Timing> = ({ marks }) => {
  const [model, cant, loop, err, body, free] = [0, 1, 2, 3, 4, 5].map((i) => useAt(marks, i));
  return (
    <Stage>
      <Box x={244} y={0} w={400} h={110} a={model} ec={C.ink} fc={C.inkT} lw={4} size={34} bold color={C.ink}>
        모델
        <span style={{ fontSize: 24, fontWeight: 400, color: C.gray, opacity: body }}>뇌</span>
      </Box>
      <Label x={760} y={55} a={cant} size={24} bold color={C.bad} w={240}>프로세스·파일 ✕</Label>
      <Arrow x1={380} y1={118} x2={380} y2={232} a={loop} />
      <Label x={250} y={170} a={loop} size={22} color={C.gray} w={240}>“이 코드 돌려 봐”</Label>
      <Arrow x1={508} y1={232} x2={508} y2={118} a={loop} />
      <Label x={650} y={170} a={loop} size={22} color={C.gray} w={240}>결과 · <span style={{ color: C.bad, opacity: err }}>오류</span></Label>
      <Box x={244} y={240} w={400} h={110} a={loop} ec={C.warn} fc={C.warnT} lw={4} size={34} bold>
        하니스
        <span style={{ fontSize: 24, fontWeight: 400, color: C.gray, opacity: body }}>몸</span>
      </Box>
      <Arrow x1={444} y1={358} x2={444} y2={420} a={loop} />
      {["코드 실행", "파일 읽기·쓰기", "셸 명령"].map((t, k) => (
        <Box key={t} x={k * 304} y={428} w={280} h={84} a={loop} ec={C.line} size={26} rise={false}>{t}</Box>
      ))}
      {/* 몸이 너무 자유로우면 */}
      {Array.from({ length: 8 }).map((_, k) => (
        <Box key={k} x={k * 111} y={560} w={100} h={56} a={free} ec={C.bad} fc={C.badT} r={8} size={20} color={C.bad} rise={false}>파일</Box>
      ))}
      <Label x={444} y={660} a={free} size={28} bold color={C.bad} w={888}>셸 한 줄이면 아무 파일이나 읽는다</Label>
    </Stage>
  );
};
