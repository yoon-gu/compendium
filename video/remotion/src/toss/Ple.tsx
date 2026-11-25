// 장면 3: 공유 인코더 + 과제별 출력층 → 간섭 → PLE(공유 전문가·과제별 전문가·게이트).
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

const TASKS = [
  { name: "과제 A", x: 780 },
  { name: "과제 B", x: 1160 },
  { name: "과제 C", x: 1540 },
];
const SHARED_X = 320;

export const Ple: React.FC<Timing> = ({ marks }) => {
  const one = useAt(marks, 0), enc = useAt(marks, 1), heads = useAt(marks, 2), clash = useAt(marks, 3);
  const experts = useAt(marks, 4), gates = useAt(marks, 5), own = useAt(marks, 6);
  const direct = heads * (1 - experts);
  return (
    <Stage>
      <Box x={80} y={840} w={1620} h={84} a={one} ec={C.line} fc="#FFFFFF" size={32} color={C.gray}>
        입력 — 유저 행동 기록 · 프로필 · 상품 정보
      </Box>
      <Box x={80} y={690} w={1620} h={96} a={enc} ec={C.ink} fc={C.inkT} lw={4} size={40} bold color={C.ink}>
        공유 인코더 — 모든 과제가 함께 쓴다
      </Box>
      <Arrow x1={888} y1={840} x2={888} y2={792} a={enc} color={C.line} />

      <Label x={330} y={200} a={one * (1 - own)} size={60} bold color={C.ink}>
        모델 하나
      </Label>
      <Label x={330} y={280} a={one * (1 - own)} size={32} color={C.gray}>
        앞부분은 함께, 끝부분만 따로
      </Label>
      <Label x={340} y={250} a={own} size={40} bold color={C.ink} w={560}>
        과제 A의 게이트는
        <br />
        공유 전문가와
        <br />
        자기 전문가만 본다
      </Label>

      {/* 과제별 출력층 */}
      {TASKS.map((t) => (
        <Box key={t.name} x={t.x - 150} y={140} w={300} h={104} a={heads} ec={C.ink} lw={4} size={34} bold color={C.ink}>
          {t.name}
          <span style={{ fontSize: 26, fontWeight: 400, color: C.gray }}>출력층</span>
        </Box>
      ))}
      {TASKS.map((t) => (
        <Arrow key={t.name} x1={t.x} y1={690} x2={t.x} y2={250} a={direct} color={C.ink} />
      ))}
      {/* 간섭 */}
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: clash * (1 - own) }} width={1776} height={1000}>
        {[[780, 1160], [1160, 1540]].map(([a, b]) => (
          <polyline key={a} points={zig(a + 20, b - 20, 455)} fill="none" stroke={C.bad} strokeWidth={6} strokeLinejoin="round" />
        ))}
      </svg>
      <Box x={180} y={420} w={300} h={64} a={clash * (1 - experts)} ec={C.bad} fc={C.badT} r={32} size={30} bold color={C.bad}>
        서로 간섭
      </Box>

      {/* 전문가 */}
      <Box x={80} y={500} w={480} h={104} a={experts} ec={C.ink} fc={C.inkT} lw={4} size={36} bold color={C.ink}>
        공유 전문가
      </Box>
      {TASKS.map((t, i) => (
        <Box key={t.name} x={t.x - 140} y={500} w={280} h={104} a={experts * (i === 0 ? 1 : 1 - own * 0.6)} ec={C.warn} fc={C.warnT} lw={3} size={30} bold rise={false}>
          {t.name} 전문가
        </Box>
      ))}

      {/* 게이트: 공유 전문가 + 자기 전문가 → 출력층 */}
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: gates }} width={1776} height={1000}>
        {TASKS.map((t, i) => {
          const hi = i === 0 ? 1 : 1 - own * 0.75;
          const col = i === 0 && own > 0 ? C.ink : C.gray;
          const lw = i === 0 ? 4 + own * 3 : 4;
          return (
            <g key={t.name} opacity={hi}>
              <line x1={SHARED_X + 120 + i * 60} y1={500} x2={t.x - 48} y2={392} stroke={col} strokeWidth={lw} />
              <line x1={t.x} y1={500} x2={t.x} y2={440} stroke={col} strokeWidth={lw} />
              <line x1={t.x} y1={344} x2={t.x} y2={248} stroke={col} strokeWidth={lw} />
              <circle cx={t.x} cy={392} r={48} fill="#FFFFFF" stroke={i === 0 && own > 0 ? C.ink : C.gray} strokeWidth={4} />
              <text x={t.x} y={400} textAnchor="middle" fontSize={24} fontWeight={800} fill={C.ink} fontFamily="NanumGothic">
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
  const n = 8, pts: string[] = [];
  for (let k = 0; k <= n; k++) pts.push(`${x1 + ((x2 - x1) * k) / n},${y + (k % 2 ? -18 : 18)}`);
  return pts.join(" ");
};
