// 장면 8: 중요한 신호가 깊은 층에서 흐려진다 → 출력층 가까이 전용 길 → (화면 바꿔) 시점이 다른 맥락을 나란히 → 쓰는 법을 구조로 정한다.
// 캔버스 888x720. 세로 화면이라 신경망 그림과 비교 그림을 한 화면에 나란히 두지 않고 차례로 보인다.
import React from "react";
import { Arrow, Box, C, H, Label, Stage, Timing, useAt, W } from "../lib/ui";

const CHIPS = [
  { t: "행동 기록", x: 0, w: 150 },
  { t: "프로필", x: 160, w: 130 },
  { t: "상품 정보", x: 300, w: 150 },
  { t: "★ 중요한 신호", x: 460, w: 200, star: true },
];
const LAYERS = [470, 380, 290, 200];
const STAR_X = 560;

export const Shortcut: React.FC<Timing> = ({ marks }) => {
  const net0 = useAt(marks, 0), blur = useAt(marks, 1, 1.4), lane = useAt(marks, 2, 1.0), side = useAt(marks, 3), tree = useAt(marks, 4), win = useAt(marks, 5);
  const net = net0 * (1 - side);                // 비교 그림이 들어오면 신경망 그림은 물러난다
  return (
    <Stage>
      {CHIPS.map((c) => (
        <Box key={c.t} x={c.x} y={590} w={c.w} h={70} a={net} r={35} ec={c.star ? C.warn : C.line} fc={c.star ? C.warnT : "#FFFFFF"} lw={c.star ? 4 : 3} size={c.star ? 25 : 26} bold={c.star}>
          {c.t}
        </Box>
      ))}
      {LAYERS.map((y, i) => (
        <Box key={y} x={0} y={y} w={640} h={64} a={net} ec={C.line} fc={C.soft} r={12} size={24} color={C.gray} rise={false}>
          {`층 ${i + 1}`}
        </Box>
      ))}
      <Box x={150} y={40} w={300} h={84} a={net} ec={C.ink} fc={C.inkT} lw={4} size={32} bold color={C.ink}>
        출력층
      </Box>
      <Arrow x1={300} y1={200} x2={300} y2={130} a={net} color={C.line} />

      {/* 층을 지날수록 흐려지는 신호 */}
      {LAYERS.map((y, i) => (
        <div
          key={y}
          style={{
            position: "absolute", left: STAR_X - 22, top: y + 10, width: 44, height: 44, borderRadius: 22,
            background: C.warn, opacity: (1 - side) * blur * Math.max(0, Math.min(1, blur * 4 - i)) * [0.95, 0.6, 0.32, 0.12][i],
          }}
        />
      ))}
      <Box x={340} y={336} w={180} h={56} a={blur * (1 - side)} ec={C.bad} fc={C.badT} r={28} size={26} bold color={C.bad}>
        흐려진다
      </Box>

      {/* 전용 길 */}
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: lane * (1 - side) }} width={W} height={H}>
        <path d="M 662 625 C 770 625, 770 520, 770 380 C 770 170, 640 82, 470 82" fill="none" stroke={C.ink} strokeWidth={7} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - lane} />
        <polygon points="456,82 476,70 476,94" fill={C.ink} opacity={lane > 0.95 ? 1 : 0} />
      </svg>
      <Label x={480} y={24} a={lane * (1 - side)} size={28} bold color={C.ink} align="left" w={408}>
        출력층 가까이에 한 번 더
      </Label>

      {/* 시점이 다른 맥락을 나란히 */}
      <Box x={0} y={30} w={420} h={84} a={side} r={42} ec={C.gray} size={32}>
        이전 시점
      </Box>
      <Box x={468} y={30} w={420} h={84} a={side} r={42} ec={C.ink} fc={C.inkT} size={32} bold color={C.ink}>
        지금
      </Box>
      <Box x={0} y={140} w={888} h={96} a={side} ec={C.ink} lw={4} size={34} bold color={C.ink}>
        그사이 무엇이 바뀌었나
      </Box>

      {/* 트리 vs 신경망 */}
      <Box x={0} y={300} w={888} h={160} a={tree} ec={C.line} size={32} color={C.gray}>
        트리 모델
        <span style={{ fontSize: 28 }}>쓰는 법은 모델이 분기하며 정한다</span>
      </Box>
      <Box x={0} y={490} w={888} h={160} a={tree} ec={win > 0 ? C.ink : C.line} fc={win > 0 ? C.inkT : "#FFFFFF"} lw={3 + win * 3} size={32} bold color={C.ink}>
        딥러닝 멀티태스크 모델
        <span style={{ fontSize: 28, fontWeight: 400 }}>쓰는 법을 사람이 구조로 정한다</span>
      </Box>
    </Stage>
  );
};
