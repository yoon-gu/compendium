// 장면 10: 공유층을 거치는 한 → 부정적 전이 → 시소가 기운다 → PLE 로 줄인다 → 손실 독차지 → 표준화. 캔버스 888x610(아래에 약어 각주 한 줄).
import React from "react";
import { C, Label, Stage, Timing, useAt } from "../lib/ui";

const PX = 444, PY = 326, HALF = 360;

export const Seesaw: React.FC<Timing> = ({ marks }) => {
  const [head, neg, tilt, ple, hog, norm] = [0, 1, 2, 3, 4, 5].map((i) => useAt(marks, i, i === 2 ? 1.4 : 0.6));
  const th = (8 * Math.PI) / 180 * tilt;        // 오른쪽이 내려간다
  const lx = PX - HALF * Math.cos(th), ly = PY - HALF * Math.sin(th);
  const rx = PX + HALF * Math.cos(th), ry = PY + HALF * Math.sin(th);
  const box = (x: number, y: number, t: string, ec: string, fc: string, a: number) => (
    <div style={{ position: "absolute", left: x - 120, top: y - 104, width: 240, height: 94, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${ec}`, background: fc, opacity: a, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 34, fontWeight: 800, color: ec }}>
      {t}
    </div>
  );
  const lines = [
    { t: "부정적 전이", a: neg, s: 32, w: 800, c: C.ink },
    { t: "PLE의 과제별 전문가와 게이트로 줄인다", a: ple, s: 28, w: 400, c: C.ink },
    { t: "손실 크기가 다르면 한 과제가 학습을 독차지", a: hog, s: 26, w: 400, c: C.bad },
    { t: "그래서 손실은 과제마다 표준화, 손실 함수도 분포에 맞게", a: norm, s: 24, w: 400, c: C.gray },
  ];
  return (
    <Stage>
      <Label x={444} y={26} a={head} size={34} bold w={888}>공유층을 거치는 한</Label>
      <Label x={444} y={76} a={head} size={28} color={C.gray} w={888}>한 과제를 위한 변경이 다른 과제를 해칠 수 있다</Label>
      <svg style={{ position: "absolute", left: 0, top: 0, opacity: head }} width={888} height={610}>
        <polygon points={`${PX},${PY} ${PX - 44},${PY + 74} ${PX + 44},${PY + 74}`} fill={C.gray} />
        <line x1={lx} y1={ly} x2={rx} y2={ry} stroke={C.txt} strokeWidth={12} strokeLinecap="round" />
      </svg>
      {box(lx + 90, ly, tilt > 0.5 ? "과제 A ↑" : "과제 A", tilt > 0.5 ? C.ok : C.gray, tilt > 0.5 ? C.okT : "#FFFFFF", head)}
      {box(rx - 90, ry, tilt > 0.5 ? "과제 B ↓" : "과제 B", tilt > 0.5 ? C.bad : C.gray, tilt > 0.5 ? C.badT : "#FFFFFF", head)}
      <div style={{ position: "absolute", left: 0, top: 418, width: 888, height: 192, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${C.ink}`, background: C.inkT, opacity: neg }} />
      {lines.map((l, k) => (
        <Label key={k} x={444} y={452 + k * 44} a={l.a} size={l.s} bold={l.w > 400} color={l.c} w={888}>{l.t}</Label>
      ))}
    </Stage>
  );
};
