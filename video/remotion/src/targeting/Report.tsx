// 장면 6: 손으로 조인하던 비교 → 정답 테이블만 적으면 보고서 → AUROC·KS·상위 구간 → 기존 모델 비교표 → 30분이 1분 → 숫자를 믿기 위한 규칙 셋. 캔버스 888x610.
import React from "react";
import { C, Stage, Timing, mix } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const LINES = [
  "[모형 성능 지표]",
  "  AUROC 0.xxx    KS 0.xxx",
  "  구분      누적 실행률   타겟 커버리지",
  "  상위 5%      0.xx%        15.xx%",
  "  상위 10%     0.xx%        30.xx%",
];
const RULES = ["상위 N%는 마케터가 쓰는 백분위 그대로", "정답을 아는 고객만 센다", "KS 는 부호를 지킨다 (절댓값 ✗)"];

export const Report: React.FC<Timing> = ({ marks }) => {
  const [hand, table, log, ks, cmp, fast, r1, r2, r3] = useMarks(marks, 9, [5]);
  const mins = Math.round(mix(30, 1, fast));
  return (
    <Stage>
      <Pill x={0} y={0} w={420} h={64} a={hand * (1 - table * 0.5)} tone="warn" size={24}>예전: 점수와 정답을 손으로 조인</Pill>
      <Pill x={468} y={0} w={420} h={64} a={table} tone="ink" size={24}>지금: 정답 테이블만 적는다</Pill>

      <At x={0} y={84} w={600} h={250} a={log} style={{ background: "#FFFFFF", border: `3px solid ${C.line}`, borderRadius: 14, boxSizing: "border-box", padding: "14px 18px", fontFamily: "NanumGothic", fontSize: 22, lineHeight: 1.75, whiteSpace: "pre" }}>
        {LINES.map((l, k) => (
          <div key={k} style={{ color: k === 1 && ks > 0.5 ? C.ink : C.txt, fontWeight: k === 1 && ks > 0.5 ? 800 : 400 }}>{l}</div>
        ))}
        <div style={{ color: C.ink, fontWeight: 800, opacity: cmp }}>+ 기존 모델 비교표 (같은 고객 · 같은 정답)</div>
      </At>
      <At x={620} y={84} w={268} h={250} a={log} style={{ border: `3px solid ${C.ink}`, borderRadius: 14, boxSizing: "border-box", background: C.inkT, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontSize: 24, color: C.gray }}>평가 한 번</div>
        <div style={{ fontSize: 76, fontWeight: 800, color: C.ink }}>{mins}분</div>
      </At>
      <At x={0} y={346} w={888} a={ks} style={{ fontSize: 23, color: C.gray }}>KS: 전환한 고객과 아닌 고객의 점수 분포가 벌어진 정도</At>

      {RULES.map((t, k) => {
        const a = [r1, r2, r3][k];
        return (
          <At key={t} x={0} y={392 + k * 72} w={888} h={60} a={a} style={{ translate: `0px ${(1 - a) * 12}px`, borderRadius: 12, boxSizing: "border-box", border: `3px solid ${C.ink}`, background: "#FFFFFF", display: "flex", alignItems: "center", padding: "0 20px", gap: 14, fontSize: 26, fontWeight: 800 }}>
            <span style={{ color: C.ink }}>✓</span>
            {t}
          </At>
        );
      })}
    </Stage>
  );
};
