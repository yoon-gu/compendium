// 장면 10: 전 — 플랫폼 기록을 변환 코드로 하니스 형식에 맞춰 되살림(하니스가 바뀌면 깨짐) → 후 — 하니스가 저장한 상태와 세션 ID를 그대로, 플랫폼은 경로만 → 못 찾으면 오류 → 이어 간다의 범위.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const State: React.FC<Timing> = ({ marks }) => {
  const [first, breaks, turn, same, path, err, scope] = [0, 1, 2, 3, 4, 5, 6].map((i) => useAt(marks, i));
  const old = first * (1 - turn * 0.7);
  return (
    <Stage>
      <Label x={0} y={20} a={first} size={26} bold color={C.gray} align="left" w={400}>처음</Label>
      {["플랫폼 대화 기록", "변환 코드", "하니스 형식"].map((t, k) => (
        <React.Fragment key={t}>
          <Box x={k * 304} y={50} w={280} h={96} a={old} ec={k === 1 && breaks > 0.5 ? C.bad : C.line} fc={k === 1 && breaks > 0.5 ? C.badT : "#FFFFFF"} size={25} bold color={k === 1 && breaks > 0.5 ? C.bad : C.txt} rise={false}>
            {t}
          </Box>
          {k < 2 && <Arrow x1={k * 304 + 282} y1={98} x2={k * 304 + 302} y2={98} a={old} color={C.gray} lw={3} />}
        </React.Fragment>
      ))}
      <Label x={444} y={176} a={breaks * (1 - turn * 0.7)} size={23} color={C.bad} w={888}>하니스가 저장 방식을 바꾸면 변환 코드도 고쳐야 한다</Label>

      <Label x={0} y={236} a={turn} size={26} bold color={C.ink} align="left" w={400}>지금</Label>
      <Box x={0} y={266} w={540} h={130} a={same} ec={C.ink} fc={C.inkT} lw={4} size={27} bold color={C.ink}>
        하니스가 저장한 상태 + 세션 ID
        <span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>하니스가 직접 읽는다</span>
      </Box>
      <Box x={588} y={266} w={300} h={130} a={path} ec={C.line} size={25} bold>
        플랫폼
        <span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>경로만 기억</span>
      </Box>
      <Box x={0} y={420} w={888} h={84} a={err} ec={C.bad} fc={C.badT} r={42} size={25} bold color={C.bad}>
        상태를 못 찾으면 이어 가지 않고 오류
      </Box>
      <Label x={444} y={548} a={scope} size={25} bold w={888}>이어 간다 ≠</Label>
      {["멈춘 곳부터 재실행", "고친 파일 되돌리기", "외부 작업 취소"].map((t, k) => (
        <Box key={t} x={k * 304} y={590} w={280} h={90} a={scope} ec={C.warn} fc={C.warnT} size={23} bold rise={false}>{t}</Box>
      ))}
    </Stage>
  );
};
