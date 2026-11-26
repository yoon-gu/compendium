// 장면 6: AP 54%·상위 N명 재현율 20% 막대가 자라고 AUC 는 그대로 → AUC 와 AP 가 보는 곳의 차이. 캔버스 888x538(아래에 약어 각주 두 줄).
import React from "react";
import { C, Stage, Timing, useAt } from "../lib/ui";

const BARS = [
  { name: "AP", v: 54, note: "약 54% 개선" },
  { name: "상위 N명 재현율", v: 20, note: "약 20% 개선" },
  { name: "AUC", v: 1, note: "거의 같음" },
];
const LINES = [
  { t: "AUC  전체 순위가 잘 섰나", c: C.txt, s: 30 },
  { t: "AP · 상위 재현율  맨 위 N명이 정확한가", c: C.ink, s: 30 },
  { t: "마케팅이 실제로 쓰는 건 맨 위 N명", c: C.gray, s: 26 },
];

export const Topn: React.FC<Timing> = ({ marks }) => {
  const a = [0, 1, 2, 3, 4, 5].map((i) => useAt(marks, i, i < 3 ? 1.2 : 0.6));
  const abs = (s: React.CSSProperties): React.CSSProperties => ({ position: "absolute", ...s });
  return (
    <Stage>
      <div style={abs({ left: 0, top: 0, fontSize: 28, color: C.gray, opacity: a[0] })}>목적별 트리 모델 대비 (상대값)</div>
      {BARS.map((b, i) => {
        const y = 54 + i * 104, p = a[i];
        return (
          <React.Fragment key={b.name}>
            <div style={abs({ left: 0, top: y, fontSize: 32, fontWeight: 800, opacity: Math.min(1, p * 2) })}>{b.name}</div>
            <div style={abs({ right: 0, top: y + 2, fontSize: 30, fontWeight: 800, color: b.v > 1 ? C.ink : C.gray, opacity: p })}>{b.note}</div>
            <div style={abs({ left: 0, top: y + 48, width: 888, height: 44, borderRadius: 10, background: C.soft, opacity: Math.min(1, p * 2) })} />
            <div style={abs({ left: 0, top: y + 48, width: Math.max(14, b.v * 12 * p), height: 44, borderRadius: 10, background: b.v > 1 ? C.ink : C.line, opacity: Math.min(1, p * 2) })} />
          </React.Fragment>
        );
      })}
      <div style={abs({ left: 0, top: 374, width: 888, height: 162, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${C.line}`, background: "#FFFFFF", opacity: a[3] })} />
      {LINES.map((l, k) => (
        <div key={k} style={abs({ left: 30, top: 396 + k * 48, fontSize: l.s, fontWeight: k < 2 ? 800 : 400, color: l.c, opacity: a[3 + k], translate: `0px ${(1 - a[3 + k]) * 12}px` })}>{l.t}</div>
      ))}
    </Stage>
  );
};
