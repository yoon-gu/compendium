// 타겟팅 회차 공용 소품. lib/ui 위에 이 회차에서만 쓰는 것만 둔다.
import React from "react";
import { C, useAt } from "../lib/ui";

/** marks 앞 n 개의 등장 값(0-1). long 에 든 번호는 1.2초에 걸쳐 나타난다. */
export const useMarks = (marks: number[], n: number, long: number[] = []) =>
  Array.from({ length: n }, (_, i) => useAt(marks, i, long.includes(i) ? 1.2 : 0.6));

/** 절대 위치 div. */
export const At: React.FC<{ x: number; y: number; w?: number; h?: number; a?: number; style?: React.CSSProperties; children?: React.ReactNode }> = ({ x, y, w, h, a = 1, style, children }) => (
  <div style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: a, ...style }}>{children}</div>
);

/** 알약 모양 라벨. */
export const Pill: React.FC<{ x: number; y: number; w: number; h?: number; a?: number; tone?: "ink" | "ok" | "warn" | "bad" | "gray"; size?: number; children: React.ReactNode }> = ({ x, y, w, h = 56, a = 1, tone = "ink", size = 26, children }) => {
  const ec = { ink: C.ink, ok: C.ok, warn: C.warn, bad: C.bad, gray: C.line }[tone];
  const fc = { ink: C.inkT, ok: C.okT, warn: C.warnT, bad: C.badT, gray: "#FFFFFF" }[tone];
  const tc = { ink: C.ink, ok: C.ok, warn: C.txt, bad: C.bad, gray: C.gray }[tone];
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, borderRadius: h / 2, boxSizing: "border-box", border: `3px solid ${ec}`, background: fc, color: tc, opacity: a, translate: `0px ${(1 - a) * 14}px`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: size, fontWeight: 800, textAlign: "center", lineHeight: 1.2 }}>
      {children}
    </div>
  );
};

/** 가로 막대(배경 + 값). */
export const Bar: React.FC<{ x: number; y: number; w: number; h?: number; p: number; a?: number; color?: string; bg?: string }> = ({ x, y, w, h = 26, p, a = 1, color = C.ink, bg = C.soft }) => (
  <>
    <At x={x} y={y} w={w} h={h} a={a} style={{ background: bg, borderRadius: 8 }} />
    <At x={x} y={y} w={Math.max(0, w * p)} h={h} a={a} style={{ background: color, borderRadius: 8 }} />
  </>
);
