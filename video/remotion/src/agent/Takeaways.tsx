// 장면 12: 읽고 나서 남는 것 셋 — 언급될 때 하나씩, 방금 말한 것만 잉크색.
import React from "react";
import { C, Stage, Timing, useAt } from "../lib/ui";

const ITEMS = [
  { h: "접근 제한", sub: "하니스가 돌리는 코드까지 파일·네트워크 제한" },
  { h: "작업 유지", sub: "파드가 바뀌어도 작업 파일과 대화 상태를 남긴다" },
  { h: "공통 기록", sub: "지난 대화 보기와 다른 하니스로 넘기기" },
];

export const Takeaways: React.FC<Timing> = ({ marks }) => {
  const a = ITEMS.map((_, i) => useAt(marks, i));
  return (
    <Stage>
      {ITEMS.map((it, i) => {
        const now = a[i] * (i < ITEMS.length - 1 ? 1 - a[i + 1] : 1);
        const ink = now > 0.5;
        return (
          <div key={it.h} style={{ position: "absolute", left: 0, top: i * 236, width: 888, height: 210, borderRadius: 16, boxSizing: "border-box", border: `${3 + now * 2}px solid ${ink ? C.ink : C.line}`, background: ink ? C.inkT : "#FFFFFF", opacity: a[i], translate: `0px ${(1 - a[i]) * 24}px`, display: "flex", alignItems: "center", padding: "0 32px", gap: 28 }}>
            <div style={{ width: 72, height: 72, borderRadius: 36, flex: "none", background: ink ? C.ink : C.soft, color: ink ? "#FFFFFF" : C.gray, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, fontWeight: 800 }}>{i + 1}</div>
            <div>
              <div style={{ fontSize: 38, fontWeight: 800, color: ink ? C.ink : C.txt }}>{it.h}</div>
              <div style={{ fontSize: 27, color: C.gray, marginTop: 12 }}>{it.sub}</div>
            </div>
          </div>
        );
      })}
    </Stage>
  );
};
