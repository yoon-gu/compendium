// 장면 4-2: 공유 부분은 모든 과제의 데이터로 배운다 → 드문 과제도 출발점 → 입력도 넓어진다(트리: 표 한 줄 / 신경망: 순서 그대로). 캔버스 888x690.
import React from "react";
import { Arrow, Box, C, Card, Label, Stage, Timing, useAt } from "../lib/ui";

const TASKS = [
  { name: "흔한 과제", n: 9 },
  { name: "보통 과제", n: 5 },
  { name: "드문 과제", n: 1 },
];

export const Share: React.FC<Timing> = ({ marks }) => {
  const [shared, rare, start, wide, tree, nn] = [0, 1, 2, 3, 4, 5].map((i) => useAt(marks, i));
  return (
    <Stage>
      <Label x={0} y={24} a={shared} size={32} bold align="left" w={888}>공유 부분은 모든 과제의 데이터로 배운다</Label>
      {TASKS.map((t, i) => {
        const x = i * 304, hi = i === 2 ? rare : 0;
        return (
          <React.Fragment key={t.name}>
            <Box x={x} y={64} w={280} h={146} a={shared} ec={hi > 0.5 ? C.ok : C.line} fc={hi > 0.5 ? C.okT : "#FFFFFF"} lw={3 + hi * 2} size={30} bold rise={false}>
              {t.name}
              <span style={{ display: "flex", gap: 8, marginTop: 14 }}>
                {Array.from({ length: t.n }).map((_, k) => (
                  <span key={k} style={{ width: 20, height: 20, borderRadius: 10, background: C.ink }} />
                ))}
              </span>
              {i === 2 && <span style={{ fontSize: 24, color: C.ok, fontWeight: 800, opacity: start, marginTop: 6 }}>출발점이 생긴다</span>}
            </Box>
            <Arrow x1={x + 140} y1={216} x2={444} y2={282} a={shared} color={C.line} lw={4} />
          </React.Fragment>
        );
      })}
      <Box x={104} y={290} w={680} h={100} a={shared} ec={C.ink} fc={C.inkT} lw={4} r={18} size={34} bold color={C.ink}>
        공유 인코더 · 공유 전문가
      </Box>
      {/* 배운 것을 드문 과제에 되돌려 준다 */}
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: rare }} width={888} height={690}>
        <path d="M 784 340 C 860 340, 860 260, 800 218" fill="none" stroke={C.ok} strokeWidth={5} strokeDasharray="10 8" />
        <polygon points="796,214 812,232 818,212" fill={C.ok} />
      </svg>

      <Label x={0} y={462} a={wide} size={32} bold align="left" w={888}>입력도 넓어진다</Label>
      <Card x={0} y={500} w={420} h={190} a={tree} head="트리 모델" sub={["표 한 줄로 편다", "순서는 집계해 넣는다"]} />
      <Card x={468} y={500} w={420} h={190} a={nn} head="신경망" sub={["시간 순 기록 그대로", "상품 묶음 그대로"]} ec={C.ink} fc={C.inkT} hc={C.ink} />
    </Stage>
  );
};
