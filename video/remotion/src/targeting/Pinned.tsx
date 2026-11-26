// 장면 7: 매일 재학습 vs 고정 → 회수율은 같다 → 상위 10% 명단이 이틀 연속 겹치는 비율 71% vs 95% → 고정하는 건 피쳐 목록(+해시). 캔버스 888x720.
import React from "react";
import { C, Stage, Timing } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const N = 20;
// 이틀째 명단에서 첫날과 다른 사람 자리(20명 중): 매일 재학습 ≈ 29%, 고정 ≈ 5%
const CHANGED = [new Set([2, 5, 8, 11, 13, 16]), new Set([14])];

export const Pinned: React.FC<Timing> = ({ marks }) => {
  const [daily, same, twoDays, p71, p95, pin, list, hash] = useMarks(marks, 8);
  const pct = [p71, p95];
  return (
    <Stage>
      {[{ x: 0, t: "매일 다시 학습", v: "71%" }, { x: 468, t: "고정", v: "95%" }].map((c, k) => (
        <React.Fragment key={c.t}>
          <At x={c.x} y={0} w={420} h={420} a={daily} style={{ border: `4px solid ${k ? C.ink : C.line}`, borderRadius: 18, boxSizing: "border-box", background: k ? C.inkT : "#FFFFFF" }} />
          <At x={c.x} y={20} w={420} a={daily} style={{ fontSize: 30, fontWeight: 800, textAlign: "center", color: k ? C.ink : C.txt }}>{c.t}</At>
          <At x={c.x} y={66} w={420} a={same} style={{ fontSize: 23, textAlign: "center", color: C.gray }}>회수율은 같다</At>
          {["첫날", "다음 날"].map((d, r) => (
            <React.Fragment key={d}>
              <At x={c.x + 20} y={124 + r * 64} a={twoDays} style={{ fontSize: 21, color: C.gray }}>{d}</At>
              {Array.from({ length: N }).map((_, i) => {
                const moved = r === 1 && CHANGED[k].has(i);
                return <At key={i} x={c.x + 110 + (i % 10) * 29} y={118 + r * 64 + Math.floor(i / 10) * 26} w={22} h={22} a={twoDays} style={{ borderRadius: 11, background: moved ? C.warn : C.ink }} />;
              })}
            </React.Fragment>
          ))}
          <At x={c.x} y={262} w={420} a={pct[k]} style={{ fontSize: 22, textAlign: "center", color: C.gray }}>상위 10% 명단이 이틀 연속 겹친 비율</At>
          <At x={c.x} y={298} w={420} a={pct[k]} style={{ fontSize: 76, fontWeight: 800, textAlign: "center", color: k ? C.ink : C.warn }}>{c.v}</At>
        </React.Fragment>
      ))}
      <Pill x={0} y={444} w={888} h={64} a={twoDays} tone="warn" size={25}>명단이 매일 바뀌면 마케터가 쓰기 어렵다</Pill>

      <At x={0} y={530} w={540} h={190} a={pin} style={{ border: `4px solid ${C.ink}`, borderRadius: 18, boxSizing: "border-box", background: "#FFFFFF", padding: "18px 24px" }}>
        <div style={{ fontSize: 30, fontWeight: 800, color: C.ink }}>🔒 고정하는 것</div>
        <div style={{ fontSize: 26, marginTop: 12, opacity: list }}>모델 파일 ✗ → 피쳐 목록 ✓</div>
        <div style={{ fontSize: 22, marginTop: 10, color: C.gray, opacity: list }}>feat01, feat02, feat03, …</div>
      </At>
      <At x={568} y={530} w={320} h={190} a={hash} style={{ border: `3px solid ${C.line}`, borderRadius: 18, boxSizing: "border-box", background: "#FFFFFF", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10 }}>
        <div style={{ fontSize: 24, color: C.gray }}>목록의 해시값</div>
        <div style={{ fontSize: 30, fontWeight: 800, color: C.ink }}>a3f9…c21</div>
        <div style={{ fontSize: 21, color: C.gray }}>같을 때만 추론</div>
      </At>
    </Stage>
  );
};
