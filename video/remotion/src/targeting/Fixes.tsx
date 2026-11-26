// 장면 7-4: 원인을 찾은 뒤 바꾼 세 가지 — 언급될 때 하나씩. 캔버스 888x720.
import React from "react";
import { C, Stage, Timing } from "../lib/ui";
import { At, useMarks } from "./parts";

const ITEMS = [
  { h: "문제 피쳐 두 개를 뺐다", s: ["지난달까지의 데이터만 담은 테이블로 대신"] },
  { h: "평가 날짜를 섞는다", s: ["월말과 월중처럼 성격이 다른 날짜", "한 날짜에서만 앞서면 피쳐를 날짜별로 다시"] },
  { h: "새 데이터 원천은 먼저 확인", s: ["그 값이 기준일에 이미 확정돼 있었나?"] },
];

export const Fixes: React.FC<Timing> = ({ marks }) => {
  const [a1, a2, a2b, a3] = useMarks(marks, 4);
  const show = [a1, a2, a3];
  const subA = [[a1], [a2, a2b], [a3]];
  return (
    <Stage>
      {ITEMS.map((it, i) => (
        <At key={it.h} x={0} y={i * 240} w={888} h={216} a={show[i]} style={{ translate: `0px ${(1 - show[i]) * 20}px`, borderRadius: 18, boxSizing: "border-box", border: `4px solid ${C.ink}`, background: C.inkT, display: "flex", alignItems: "center", gap: 26, padding: "0 30px" }}>
          <div style={{ width: 70, height: 70, flex: "none", borderRadius: 35, background: C.ink, color: "#FFFFFF", fontSize: 38, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
          <div>
            <div style={{ fontSize: 36, fontWeight: 800, color: C.ink }}>{it.h}</div>
            {it.s.map((s, k) => (
              <div key={s} style={{ fontSize: 27, color: C.gray, marginTop: 10, opacity: subA[i][k] }}>{s}</div>
            ))}
          </div>
        </At>
      ))}
    </Stage>
  );
};
