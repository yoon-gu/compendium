// 장면 4-2: 피쳐 수 K 별 AUROC·PR-AUC(458개 = 100%) → 75가 구별 안 되는 가장 작은 K → −84% → AUROC 는 다 비슷 → PR-AUC 는 77% → 지표가 결론을 바꾼다. 캔버스 888x610.
import React from "react";
import { C, Stage, Timing } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const ROWS = [
  { k: 20, auc: 99.1, pr: 77.4, sig: true },
  { k: 30, auc: 99.5, pr: 74.2, sig: true },
  { k: 50, auc: 100.0, pr: 88.7, sig: true },
  { k: 75, auc: 100.1, pr: 98.4, sig: false },
  { k: 100, auc: 100.2, pr: 100.0, sig: false },
  { k: 458, auc: 100, pr: 100, sig: false },
];
const LO = 60, HI = 102, BW = 300;
const w = (v: number) => (BW * (v - LO)) / (HI - LO);
const Y0 = 56, RH = 64;

export const Ktable: React.FC<Timing> = ({ marks }) => {
  const [rows, best, cut, auc, pr, ends] = useMarks(marks, 6, [0]);
  const col = (x: number, t: string, hi: number) => (
    <At x={x} y={0} w={BW + 70} a={rows} style={{ fontSize: 28, fontWeight: 800, color: hi > 0.5 ? C.ink : C.gray }}>{t}</At>
  );
  return (
    <Stage>
      <At x={0} y={0} a={rows} style={{ fontSize: 28, fontWeight: 800, color: C.gray }}>피쳐 수 K</At>
      {col(140, "AUROC", auc * (1 - pr))}
      {col(520, "PR-AUC", pr)}
      {ROWS.map((r, i) => {
        const a = Math.max(0, Math.min(1, rows * 1.8 - (ROWS.length - 1 - i) / ROWS.length));
        const y = Y0 + i * RH, isBest = r.k === 75;
        const prBad = r.k === 20 && pr > 0.5;
        return (
          <React.Fragment key={r.k}>
            <At x={0} y={y} w={888} h={RH - 8} a={a * best * (isBest ? 1 : 0)} style={{ border: `4px solid ${C.ink}`, borderRadius: 12, boxSizing: "border-box", background: C.inkT }} />
            <At x={20} y={y + 12} a={a} style={{ fontSize: 30, fontWeight: 800 }}>{r.k}</At>
            <At x={140} y={y + 14} w={w(r.auc)} h={28} a={a} style={{ borderRadius: 7, background: auc > 0.5 && pr < 0.5 ? C.ink : C.line }} />
            <At x={140 + w(r.auc) + 8} y={y + 14} a={a} style={{ fontSize: 24, color: C.gray }}>{r.auc.toFixed(1)}</At>
            <At x={520} y={y + 14} w={w(r.pr)} h={28} a={a} style={{ borderRadius: 7, background: prBad ? C.bad : C.ink }} />
            <At x={520 + w(r.pr) + 8} y={y + 14} a={a} style={{ fontSize: 24, fontWeight: prBad ? 800 : 400, color: prBad ? C.bad : C.gray }}>{r.pr.toFixed(1)}</At>
          </React.Fragment>
        );
      })}
      <At x={0} y={Y0 + 6 * RH + 4} w={888} a={rows} style={{ fontSize: 22, color: C.gray, textAlign: "right" }}>458개 모델 = 100 (상대값)</At>
      <Pill x={0} y={Y0 + 6 * RH + 40} w={430} h={60} a={best} tone="ink" size={25}>75개 = 구별 안 되는 최소 K</Pill>
      <Pill x={458} y={Y0 + 6 * RH + 40} w={430} h={60} a={cut} tone="ok" size={28}>피쳐 −84%, 성능 그대로</Pill>
      <At x={0} y={Y0 + 6 * RH + 112} w={888} a={ends} style={{ fontSize: 27, fontWeight: 800, color: C.bad, textAlign: "center" }}>AUROC 로는 20개도 99%, PR-AUC 로는 77%</At>
    </Stage>
  );
};
