// 장면 6: 울타리 셋 — 파일(필요한 곳만, 참고 자료는 읽기 전용) · 프로세스와 네트워크(프록시로만) · 실행 권한(낮추고, 실패하면 실행 안 함) → 한계.
import React from "react";
import { C, Stage, Timing, useAt } from "../lib/ui";

const ROWS = [
  { h: "① 파일", items: [["작업 폴더", "ok"], ["허용 폴더", "ok"], ["세션 상태", "ok"], ["다른 에이전트", "no"], ["참고 자료 🔒", "ro"]] },
  { h: "② 프로세스 · 네트워크", items: [["다른 프로세스", "no"], ["파드 네트워크", "no"], ["프록시로만", "ok"]] },
  { h: "③ 실행 권한", items: [["낮춘 사용자", "ok"], ["capability", "no"], ["실패하면 중단", "ok"]] },
];

export const Fences: React.FC<Timing> = ({ marks }) => {
  // 표시: 0 세 가지, 1 파일, 2 다른 에이전트, 3 읽기 전용, 4 프로세스·네트워크, 5 프록시, 6 실행 권한, 7 capability, 8 실패하면, 9 한계
  const a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => useAt(marks, i));
  const itemA = [
    [a[1], a[1], a[1], a[2], a[3]],
    [a[4], a[4], a[5]],
    [a[6], a[7], a[8]],
  ];
  const rowA = [a[1], a[4], a[6]].map((v, i) => Math.max(v, i === 0 ? a[0] * 0.999 : 0));
  return (
    <Stage>
      {ROWS.map((r, i) => (
        <div key={r.h} style={{ position: "absolute", left: 0, top: i * 186, width: 888, height: 168, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${C.line}`, background: "#FFFFFF", opacity: rowA[i], padding: "18px 22px" }}>
          <div style={{ fontSize: 30, fontWeight: 800 }}>{r.h}</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 16 }}>
            {r.items.map(([t, k], j) => {
              const col = k === "ok" ? C.ok : k === "no" ? C.bad : C.warn;
              const bg = k === "ok" ? C.okT : k === "no" ? C.badT : C.warnT;
              return (
                <span key={t} style={{ opacity: itemA[i][j], padding: "8px 16px", borderRadius: 24, border: `3px solid ${col}`, background: bg, color: col, fontSize: 24, fontWeight: 800, textDecoration: k === "no" ? "line-through" : "none" }}>
                  {t}
                </span>
              );
            })}
          </div>
        </div>
      ))}
      <div style={{ position: "absolute", left: 0, top: 572, width: 888, height: 120, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${C.warn}`, background: C.warnT, opacity: a[9], display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8 }}>
        <div style={{ fontSize: 27, fontWeight: 800 }}>허락한 폴더 안의 실수까지는 못 막는다</div>
        <div style={{ fontSize: 23, color: C.gray }}>결과가 맞는지는 따로 확인</div>
      </div>
    </Stage>
  );
};
