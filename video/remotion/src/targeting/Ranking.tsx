// 장면 3: 고객마다 점수 → 점수 순으로 줄 세움 → 상위 구간에만 발송 → 회수율·실행률·AUC·PR-AUC 카드. 캔버스 888x610.
import React from "react";
import { C, Stage, Timing, mix } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

// 고객 12명: 점수와 실제 전환 여부. 화면 처음엔 섞인 순서, 정렬 뒤 점수 순.
const CUST = [0.31, 0.92, 0.12, 0.66, 0.85, 0.08, 0.44, 0.71, 0.22, 0.53, 0.37, 0.17];
const CONV = new Set([1, 4, 7, 10]);
const ORDER = CUST.map((s, i) => [s, i] as const).sort((a, b) => b[0] - a[0]).map(([, i]) => i);
const TOP = 3, ROW = 40, Y0 = 50;

export const Ranking: React.FC<Timing> = ({ marks }) => {
  const [score, sort, top, rec, prec, auc, pr] = useMarks(marks, 7, [1]);
  const cards = [
    { a: rec, h: "회수율", t: "전환한 고객 중 상위 구간이 잡은 비율", v: "2 / 4" },
    { a: prec, h: "실행률", t: "상위 구간 안에서 전환한 비율", v: "2 / 3" },
    { a: auc, h: "AUC", t: "전체 순위가 잘 섰나", v: "" },
    { a: pr, h: "PR-AUC", t: "정밀도·재현율을 함께, 전환이 드물 때", v: "" },
  ];
  return (
    <Stage>
      <At x={0} y={6} a={score} style={{ fontSize: 26, fontWeight: 800, color: C.gray }}>고객 · 점수 · 전환</At>
      {CUST.map((s, i) => {
        const y = Y0 + mix(i, ORDER.indexOf(i), sort) * ROW;
        const conv = CONV.has(i);
        return (
          <React.Fragment key={i}>
            <At x={0} y={y + 6} w={28} h={28} a={score} style={{ borderRadius: 14, background: C.line }} />
            <At x={40} y={y + 8} w={300 * s} h={24} a={score} style={{ borderRadius: 6, background: C.ink, opacity: score * (0.35 + 0.65 * s) }} />
            <At x={350} y={y + 4} w={60} h={32} a={score * sort} style={{ fontSize: 22, fontWeight: 800, color: C.ok }}>{conv ? "전환" : ""}</At>
          </React.Fragment>
        );
      })}
      {/* 상위 구간 */}
      <At x={-4} y={Y0 - 4} w={420} h={TOP * ROW + 6} a={top} style={{ border: `4px solid ${C.warn}`, borderRadius: 12, boxSizing: "border-box" }} />
      <Pill x={0} y={Y0 + 12 * ROW + 14} w={410} h={52} a={top} tone="warn" size={24}>상위 구간에만 메시지</Pill>

      {cards.map((c, k) => (
        <At key={c.h} x={450} y={Y0 + k * 132} w={438} h={116} a={c.a} style={{ translate: `0px ${(1 - c.a) * 16}px`, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${k < 2 ? C.ink : C.line}`, background: k < 2 ? C.inkT : "#FFFFFF", padding: "14px 20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 30, fontWeight: 800, color: k < 2 ? C.ink : C.txt }}>
            <span>{c.h}</span>
            <span>{c.v}</span>
          </div>
          <div style={{ fontSize: 23, color: C.gray, marginTop: 10 }}>{c.t}</div>
        </At>
      ))}
    </Stage>
  );
};
