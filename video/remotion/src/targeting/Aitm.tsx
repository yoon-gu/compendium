// 장면 5-2: AITM — 퍼널 전체를 한 모델로. 정보 전달(고객마다 가중치) → 단조성 제약(넘친 만큼 벌점) → 단계별 정답을 한 테이블에. 캔버스 888x610.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing } from "../lib/ui";
import { At, useMarks } from "./parts";

const ST = [{ n: "진입", x: 40, p: 0.62 }, { n: "클릭", x: 330, p: 0.38 }, { n: "신청", x: 620, p: 0.24 }];
const COLS = ["사용자 ID", "기준일", "label_a", "label_b", "label_c"];

export const Aitm: React.FC<Timing> = ({ marks }) => {
  const [one, transfer, weight, mono, penalty, absurd, table, last] = useMarks(marks, 8);
  const bad = penalty; // 신청 확률이 클릭보다 커진 경우를 보여 준 뒤 벌점으로 깎는다
  return (
    <Stage>
      <At x={0} y={0} w={888} h={300} a={one} style={{ border: `4px solid ${C.ink}`, borderRadius: 18, boxSizing: "border-box", background: C.inkT }} />
      <Label x={444} y={30} a={one} size={28} bold color={C.ink} w={888}>AITM — 퍼널 전체를 한 모델로</Label>
      {ST.map((s, i) => (
        <React.Fragment key={s.n}>
          <Box x={s.x} y={64} w={228} h={110} a={one} ec={C.ink} fc="#FFFFFF" size={30} bold color={C.ink}>
            {s.n}
            <span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>단계 표현</span>
          </Box>
          {i > 0 && <Arrow x1={ST[i - 1].x + 232} y1={119} x2={s.x - 4} y2={119} a={transfer} lw={5} />}
        </React.Fragment>
      ))}
      <Label x={300} y={210} a={transfer} size={24} bold color={C.ink} w={260}>정보 전달 →</Label>
      <Label x={590} y={210} a={transfer} size={24} bold color={C.ink} w={260}>정보 전달 →</Label>
      <Label x={444} y={262} a={weight} size={24} color={C.gray} w={888}>앞 단계를 얼마나 참고할지 = 고객마다 가중치</Label>

      {/* 단조성 제약: 확률 막대 */}
      <At x={0} y={322} a={mono} style={{ fontSize: 26, fontWeight: 800 }}>단조성 제약: 뒤 단계 확률 ≤ 앞 단계 확률</At>
      {ST.map((s, i) => {
        const p = i === 2 ? s.p + 0.24 * (1 - bad * 0) : s.p;
        return (
          <React.Fragment key={s.n}>
            <At x={s.x} y={366} w={228} h={30} a={mono} style={{ background: C.soft, borderRadius: 8 }} />
            <At x={s.x} y={366} w={228 * Math.min(p, ST[1].p)} h={30} a={mono} style={{ background: C.ink, borderRadius: 8 }} />
            {i === 2 && <At x={s.x + 228 * ST[1].p} y={366} w={228 * (p - ST[1].p)} h={30} a={mono} style={{ background: C.bad, borderRadius: 8 }} />}
            <At x={s.x} y={402} w={228} a={mono} style={{ fontSize: 22, color: C.gray, textAlign: "center" }}>P({s.n})</At>
          </React.Fragment>
        );
      })}
      <At x={560} y={432} w={328} a={penalty} style={{ fontSize: 23, fontWeight: 800, color: C.bad, textAlign: "center" }}>넘친 만큼 손실에 벌점</At>
      <At x={0} y={432} w={540} a={absurd} style={{ fontSize: 23, color: C.bad }}>클릭도 안 할 사람이 신청할 확률이 더 높다? ✗</At>

      {/* 라벨 테이블 */}
      {COLS.map((c, k) => {
        const hi = k === 4 && last > 0.5;
        return (
          <At key={c} x={k * 178} y={490} w={170} h={64} a={table} style={{ border: `3px solid ${hi ? C.ink : C.line}`, background: hi ? C.inkT : "#FFFFFF", borderRadius: 10, boxSizing: "border-box", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 23, fontWeight: 800, color: hi ? C.ink : C.txt }}>{c}</At>
        );
      })}
      <At x={0} y={566} w={888} a={table} style={{ fontSize: 22, color: C.gray, textAlign: "center" }}>
        단계별 정답을 한 테이블에 → 몇 단계인지 알아서 판별{last > 0.5 ? " · 운영엔 마지막 단계 점수" : ""}
      </At>
    </Stage>
  );
};
