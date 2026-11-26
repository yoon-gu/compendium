// 장면 3: 공유 인코더 + 과제별 출력층 → 간섭 → PLE(공유 전문가·과제별 전문가·게이트). 캔버스 888x720.
import React from "react";
import { Arrow, Box, C, H, Label, Stage, Timing, useAt, W } from "../lib/ui";

const TASKS = [
  { name: "과제 A", x: 340 },
  { name: "과제 B", x: 555 },
  { name: "과제 C", x: 770 },
];
const SHARED_X = 105;          // 공유 전문가 열 가운데
const HEAD_Y = 150, EXP_Y = 400, GATE_Y = 318;

export const Ple: React.FC<Timing> = ({ marks }) => {
  const one = useAt(marks, 0), enc = useAt(marks, 1), heads = useAt(marks, 2), clash = useAt(marks, 3);
  const experts = useAt(marks, 4), gates = useAt(marks, 5), own = useAt(marks, 6);
  const direct = heads * (1 - experts);
  return (
    <Stage>
      <Box x={0} y={642} w={888} h={70} a={one} ec={C.line} fc="#FFFFFF" size={27} color={C.gray}>
        입력 — 유저 행동 기록 · 프로필 · 상품 정보
      </Box>
      <Box x={0} y={524} w={888} h={84} a={enc} ec={C.ink} fc={C.inkT} lw={4} size={32} bold color={C.ink}>
        공유 인코더 — 모든 과제가 함께 쓴다
      </Box>
      <Arrow x1={444} y1={642} x2={444} y2={612} a={enc} color={C.line} />

      <Label x={444} y={42} a={one * (1 - own)} size={46} bold color={C.ink} w={888}>
        모델 하나
      </Label>
      <Label x={444} y={100} a={one * (1 - own)} size={28} color={C.gray} w={888}>
        앞부분은 함께, 끝부분만 따로
      </Label>
      <Label x={444} y={66} a={own} size={32} bold color={C.ink} w={888}>
        과제 A의 게이트는
        <br />
        공유 전문가와 자기 전문가만 본다
      </Label>

      {/* 과제별 출력층 */}
      {TASKS.map((t) => (
        <Box key={t.name} x={t.x - 95} y={HEAD_Y} w={190} h={96} a={heads} ec={C.ink} lw={4} size={30} bold color={C.ink}>
          {t.name}
          <span style={{ fontSize: 24, fontWeight: 400, color: C.gray }}>출력층</span>
        </Box>
      ))}
      {TASKS.map((t) => (
        <Arrow key={t.name} x1={t.x} y1={524} x2={t.x} y2={HEAD_Y + 100} a={direct} color={C.ink} />
      ))}
      {/* 간섭 */}
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: clash * (1 - experts) }} width={W} height={H}>
        {[[340, 555], [555, 770]].map(([a, b]) => (
          <polyline key={a} points={zig(a + 14, b - 14, 400)} fill="none" stroke={C.bad} strokeWidth={5} strokeLinejoin="round" />
        ))}
      </svg>
      <Box x={10} y={370} w={190} h={60} a={clash * (1 - experts)} ec={C.bad} fc={C.badT} r={30} size={27} bold color={C.bad}>
        서로 간섭
      </Box>

      {/* 전문가 */}
      <Box x={SHARED_X - 95} y={EXP_Y} w={190} h={96} a={experts} ec={C.ink} fc={C.inkT} lw={4} size={28} bold color={C.ink}>
        공유
        <br />
        전문가
      </Box>
      {TASKS.map((t, i) => (
        <Box key={t.name} x={t.x - 95} y={EXP_Y} w={190} h={96} a={experts * (i === 0 ? 1 : 1 - own * 0.6)} ec={C.warn} fc={C.warnT} lw={3} size={27} bold rise={false}>
          {t.name}
          <br />
          전문가
        </Box>
      ))}

      {/* 게이트: 공유 전문가 + 자기 전문가 → 출력층 */}
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: gates }} width={W} height={H}>
        {TASKS.map((t, i) => {
          const hi = i === 0 ? 1 : 1 - own * 0.75;
          const col = i === 0 && own > 0 ? C.ink : C.gray;
          const lw = i === 0 ? 3 + own * 3 : 3;
          return (
            <g key={t.name} opacity={hi}>
              <line x1={SHARED_X + 40 + i * 25} y1={EXP_Y} x2={t.x - 40} y2={GATE_Y + 8} stroke={col} strokeWidth={lw} />
              <line x1={t.x} y1={EXP_Y} x2={t.x} y2={GATE_Y + 40} stroke={col} strokeWidth={lw} />
              <line x1={t.x} y1={GATE_Y - 40} x2={t.x} y2={HEAD_Y + 98} stroke={col} strokeWidth={lw} />
              <circle cx={t.x} cy={GATE_Y} r={40} fill="#FFFFFF" stroke={i === 0 && own > 0 ? C.ink : C.gray} strokeWidth={3} />
              <text x={t.x} y={GATE_Y + 8} textAnchor="middle" fontSize={21} fontWeight={800} fill={C.ink} fontFamily="NanumGothic">
                게이트
              </text>
            </g>
          );
        })}
      </svg>
    </Stage>
  );
};

const zig = (x1: number, x2: number, y: number) => {
  const n = 6, pts: string[] = [];
  for (let k = 0; k <= n; k++) pts.push(`${x1 + ((x2 - x1) * k) / n},${y + (k % 2 ? -16 : 16)}`);
  return pts.join(" ");
};
