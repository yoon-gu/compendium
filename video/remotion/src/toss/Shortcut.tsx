// 장면 8: 중요한 신호가 깊은 층에서 흐려진다 → 출력층 가까이 전용 길 → 시점이 다른 맥락을 나란히 → 쓰는 법을 구조로 정한다.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

const CHIPS = [
  { t: "행동 기록", x: 80 },
  { t: "프로필", x: 320 },
  { t: "상품 정보", x: 560 },
  { t: "★ 중요한 신호", x: 800, star: true },
];
const LAYERS = [700, 575, 450, 325];
const STAR_X = 910;

export const Shortcut: React.FC<Timing> = ({ marks }) => {
  const net = useAt(marks, 0), blur = useAt(marks, 1, 1.4), lane = useAt(marks, 2, 1.0), side = useAt(marks, 3), tree = useAt(marks, 4), win = useAt(marks, 5);
  return (
    <Stage>
      {CHIPS.map((c) => (
        <Box key={c.t} x={c.x} y={850} w={220} h={80} a={net} r={40} ec={c.star ? C.warn : C.line} fc={c.star ? C.warnT : "#FFFFFF"} lw={c.star ? 4 : 3} size={28} bold={c.star}>
          {c.t}
        </Box>
      ))}
      {LAYERS.map((y, i) => (
        <Box key={y} x={80} y={y} w={960} h={70} a={net} ec={C.line} fc={C.soft} r={14} size={26} color={C.gray} rise={false}>
          {`층 ${i + 1}`}
        </Box>
      ))}
      <Box x={330} y={150} w={460} h={100} a={net} ec={C.ink} fc={C.inkT} lw={4} size={36} bold color={C.ink}>
        출력층
      </Box>
      <Arrow x1={560} y1={325} x2={560} y2={256} a={net} color={C.line} />

      {/* 층을 지날수록 흐려지는 신호 */}
      {LAYERS.map((y, i) => (
        <div
          key={y}
          style={{
            position: "absolute", left: STAR_X - 26, top: y + 9, width: 52, height: 52, borderRadius: 26,
            background: C.warn, opacity: blur * Math.max(0, Math.min(1, blur * 4 - i)) * [0.95, 0.6, 0.32, 0.12][i],
          }}
        />
      ))}
      <Box x={500} y={516} w={250} h={64} a={blur} ec={C.bad} fc={C.badT} r={32} size={28} bold color={C.bad}>
        흐려진다
      </Box>

      {/* 전용 길 */}
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: lane }} width={1776} height={1000}>
        <path d="M 1024 890 C 1100 890, 1100 600, 1100 420 C 1100 260, 950 200, 800 200" fill="none" stroke={C.ink} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - lane} />
        <polygon points="796,200 818,188 818,212" fill={C.ink} opacity={lane > 0.95 ? 1 : 0} />
      </svg>
      <Label x={1120} y={150} a={lane} size={30} bold color={C.ink} align="left" w={600}>
        출력층 가까이에 한 번 더
      </Label>

      {/* 시점이 다른 맥락을 나란히 */}
      <Box x={1180} y={230} w={240} h={76} a={side} r={38} ec={C.gray} size={28}>
        이전 시점
      </Box>
      <Box x={1460} y={230} w={240} h={76} a={side} r={38} ec={C.ink} fc={C.inkT} size={28} bold color={C.ink}>
        지금
      </Box>
      <Box x={1180} y={340} w={520} h={80} a={side} ec={C.ink} lw={4} size={30} bold color={C.ink}>
        그사이 무엇이 바뀌었나
      </Box>

      {/* 트리 vs 신경망 */}
      <Box x={1180} y={530} w={520} h={140} a={tree} ec={C.line} size={28} color={C.gray}>
        트리 모델
        <span style={{ fontSize: 26 }}>쓰는 법은 모델이 분기하며 정한다</span>
      </Box>
      <Box x={1180} y={700} w={520} h={140} a={tree} ec={win > 0 ? C.ink : C.line} fc={win > 0 ? C.inkT : "#FFFFFF"} lw={3 + win * 3} size={28} bold color={C.ink}>
        딥러닝 멀티태스크 모델
        <span style={{ fontSize: 26, fontWeight: 400 }}>쓰는 법을 사람이 구조로 정한다</span>
      </Box>
    </Stage>
  );
};
