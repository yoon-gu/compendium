// 장면 12: 읽고 나서 남는 것 넷 — 언급될 때 체크 표시와 함께 하나씩, 방금 말한 것만 잉크색. 캔버스 888x720.
import React from "react";
import { C, Stage, Timing, useAt } from "../lib/ui";

const ITEMS = [
  { h: "운영이 가벼워진다", sub: "재학습 · 평가 · 실험을 한 곳에서 자주" },
  { h: "새 과제 · 새 상품이 많을수록", sub: "효과가 크다" },
  { h: "드문 과제는 묶여서 덕을 본다", sub: "비슷한 과제가 배운 것을 같이 쓴다" },
  { h: "넣기 어려웠던 입력도 쓴다", sub: "중요한 신호엔 전용 길" },
];

export const Takeaways: React.FC<Timing> = ({ marks }) => {
  const a = ITEMS.map((_, i) => useAt(marks, i));
  return (
    <Stage>
      {ITEMS.map((it, i) => {
        const now = a[i] * (i < ITEMS.length - 1 ? 1 - a[i + 1] : 1);
        const ink = now > 0.5;
        return (
          <div key={it.h} style={{ position: "absolute", left: 0, top: i * 182, width: 888, height: 160, borderRadius: 16, boxSizing: "border-box", border: `${3 + now * 2}px solid ${ink ? C.ink : C.line}`, background: ink ? C.inkT : "#FFFFFF", opacity: a[i], translate: `0px ${(1 - a[i]) * 24}px`, display: "flex", alignItems: "center", padding: "0 28px", gap: 26 }}>
            <div style={{ width: 64, height: 64, borderRadius: 32, flex: "none", background: ink ? C.ink : C.soft, color: ink ? "#FFFFFF" : C.gray, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36, fontWeight: 800 }}>✓</div>
            <div>
              <div style={{ fontSize: 34, fontWeight: 800, color: ink ? C.ink : C.txt }}>{it.h}</div>
              <div style={{ fontSize: 27, color: C.gray, marginTop: 10 }}>{it.sub}</div>
            </div>
          </div>
        );
      })}
    </Stage>
  );
};
