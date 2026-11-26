// 장면 2-2: 모델이 수백 개면 드는 비용 넷 — 언급될 때 한 줄씩, 방금 말한 줄만 노랑. 캔버스 888x684.
import React from "react";
import { C, Stage, Timing, useAt } from "../lib/ui";

const ROWS = [
  { h: "운영", sub: "모델마다 데이터 준비 · 학습 · 배포 · 모니터링" },
  { h: "재학습", sub: "수백 개를 자주 못 돌려 오래 그대로 남는다" },
  { h: "실험", sub: "새 데이터 효과를 보려면 모델마다 다시 학습" },
  { h: "드문 과제", sub: "혼자 배우기엔 데이터가 모자라다" },
];

export const Costs: React.FC<Timing> = ({ marks }) => {
  const a = [0, 1, 2, 3, 4].map((i) => useAt(marks, i)); // 4번째는 '새 상품은 모델이 없다'
  return (
    <Stage>
      {ROWS.map((r, i) => {
        const now = a[i] * (i < 3 ? 1 - a[i + 1] : 1);
        return (
          <div
            key={r.h}
            style={{
              position: "absolute", left: 0, top: i * 176, width: 888, height: 156, boxSizing: "border-box", borderRadius: 16,
              border: `${3 + now}px solid ${now > 0.5 ? C.warn : C.line}`, background: now > 0.5 ? C.warnT : "#FFFFFF",
              opacity: a[i], translate: `0px ${(1 - a[i]) * 24}px`, padding: "26px 32px",
            }}
          >
            <div style={{ fontSize: 36, fontWeight: 800, color: now > 0.5 ? C.warn : C.txt }}>{r.h}</div>
            <div style={{ fontSize: 28, color: C.gray, marginTop: 14 }}>
              {r.sub}
              {i === 3 && <span style={{ opacity: a[4], color: C.bad, fontWeight: 700 }}> · 새 상품은 모델이 없다</span>}
            </div>
          </div>
        );
      })}
    </Stage>
  );
};
