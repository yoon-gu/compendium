// 장면 4-3: auto_k 세 단계 → K 를 늘리며 잰 성능 곡선 → 구별 안 되는 가장 작은 K(75) → 근거 없으면 예전 비율 → 실제 발송 성과. 캔버스 888x720.
import React from "react";
import { C, Stage, Timing } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const STEPS = ["① 전체 피쳐로 한 번 학습 → 중요도 순서", "② K = 10, 20, 30, 50, 75 … 늘려 가며 다시 학습·평가", "③ 최고점과 구별되지 않는 가장 작은 K"];
const KS = [10, 20, 30, 50, 75, 100, 150];
const PR = [0.55, 0.7, 0.68, 0.84, 0.97, 0.99, 1.0];
const CX = 70, CY = 300, CW = 760, CH = 190;

export const Autok: React.FC<Timing> = ({ marks }) => {
  const [name, s1, s2, s3, back, x5, x26] = useMarks(marks, 7, [2]);
  const sa = [s1, s2, s3];
  const px = (i: number) => CX + (i / (KS.length - 1)) * CW;
  const py = (v: number) => CY + CH - ((v - 0.5) / 0.52) * CH;
  return (
    <Stage>
      {STEPS.map((t, i) => (
        <At key={t} x={0} y={i * 84} w={888} h={70} a={sa[i]} style={{ translate: `0px ${(1 - sa[i]) * 14}px`, borderRadius: 14, boxSizing: "border-box", border: `3px solid ${i === 2 ? C.ink : C.line}`, background: i === 2 ? C.inkT : "#FFFFFF", display: "flex", alignItems: "center", padding: "0 22px", fontSize: 27, fontWeight: 800, color: i === 2 ? C.ink : C.txt }}>{t}</At>
      ))}
      {/* 성능 곡선 */}
      <At x={CX} y={CY + CH} w={CW} h={3} a={name} style={{ background: C.txt }} />
      <At x={CX} y={py(0.985) - 20} w={CW} h={40} a={s3} style={{ background: C.okT, borderRadius: 8 }} />
      <At x={CX + CW - 330} y={py(0.985) - 56} a={s3} style={{ fontSize: 22, color: C.ok, fontWeight: 800 }}>최고점과 구별 안 되는 구간</At>
      {KS.map((k, i) => {
        const a = Math.max(0, Math.min(1, s2 * KS.length - i));
        const pick = k === 75 && s3 > 0.5;
        return (
          <React.Fragment key={k}>
            <At x={px(i) - (pick ? 14 : 10)} y={py(PR[i]) - (pick ? 14 : 10)} w={pick ? 28 : 20} h={pick ? 28 : 20} a={a} style={{ borderRadius: 14, background: pick ? C.ink : C.gray }} />
            <At x={px(i) - 40} y={CY + CH + 10} w={80} a={a} style={{ fontSize: 24, textAlign: "center", fontWeight: pick ? 800 : 400, color: pick ? C.ink : C.gray }}>{k}</At>
          </React.Fragment>
        );
      })}
      <At x={0} y={CY - 10} a={name} style={{ fontSize: 22, color: C.gray }}>PR-AUC</At>
      <Pill x={px(4) - 90} y={py(PR[4]) + 30} w={180} h={48} a={s3} tone="ink" size={24}>K = 75</Pill>

      <Pill x={0} y={548} w={888} h={56} a={back} tone="gray" size={25}>판단할 근거가 없으면 → 예전 비율 그대로</Pill>
      <At x={0} y={620} w={888} a={x5} style={{ fontSize: 22, color: C.gray, textAlign: "center" }}>상위 1% 고객 · 규칙 기반 세그먼트 대비</At>
      <Pill x={0} y={652} w={420} h={64} a={x5} tone="ok" size={30}>클릭률 약 5배</Pill>
      <Pill x={468} y={652} w={420} h={64} a={x26} tone="ok" size={30}>신청 전환율 약 2.6배</Pill>
    </Stage>
  );
};
