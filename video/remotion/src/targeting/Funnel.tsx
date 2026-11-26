// 장면 5: 퍼널 단계 → 단계마다 트리 따로 → 점수는 곱해서 → 남남(신호가 안 넘어감) → 마지막 단계일수록 절실 → 모델 5개 · 조합 11가지 · 수십 개. 캔버스 888x720.
import React from "react";
import { Arrow, Box, C, Stage, Timing, Tree } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const STAGES = ["노출", "진입", "클릭", "신청"];
const TREES = [{ x: 333, p: "P(진입)" }, { x: 555, p: "P(클릭)" }, { x: 777, p: "P(신청)" }];

export const Funnel: React.FC<Timing> = ({ marks }) => {
  const [stages, sep, mult, apart, need, five, eleven, dozens] = useMarks(marks, 8);
  return (
    <Stage>
      {STAGES.map((s, i) => (
        <React.Fragment key={s}>
          <Box x={i * 222 + 12 + i * 4} y={8 + i * 6} w={190 - i * 0} h={84 - i * 12} a={stages} ec={C.ink} fc={C.inkT} size={30 - i} bold color={C.ink} rise={false}>{s}</Box>
          {i > 0 && <Arrow x1={i * 222 - 18 + i * 4} y1={50} x2={i * 222 + 8 + i * 4} y2={50} a={stages} color={C.gray} lw={3} />}
        </React.Fragment>
      ))}
      {TREES.map((t, i) => (
        <React.Fragment key={t.p}>
          <Tree x={t.x} y={196} s={1.3} a={sep} color={i === 2 && need > 0.5 ? C.warn : C.ink} />
          <At x={t.x - 100} y={250} w={200} a={sep} style={{ fontSize: 28, fontWeight: 800, textAlign: "center", color: C.ink }}>{t.p}</At>
        </React.Fragment>
      ))}
      <At x={444 - 2} y={140} w={4} h={150} a={apart} style={{ borderLeft: `5px dashed ${C.bad}` }} />
      <At x={666 - 2} y={140} w={4} h={150} a={apart} style={{ borderLeft: `5px dashed ${C.bad}` }} />
      <At x={20} y={150} w={260} a={apart} style={{ fontSize: 26, fontWeight: 800, color: C.bad, lineHeight: 1.3 }}>단계끼리 남남<br />신호가 안 넘어간다</At>
      <At x={660} y={296} w={228} a={need} style={{ fontSize: 22, fontWeight: 800, color: C.warn, textAlign: "center" }}>데이터가 가장 적은 단계</At>

      <Box x={0} y={340} w={888} h={84} a={mult} ec={C.ink} fc="#FFFFFF" lw={4} size={30} bold color={C.ink}>최종 점수 = P(진입) × P(클릭) × P(신청)</Box>

      <Pill x={0} y={456} w={420} h={70} a={five} tone="warn" size={28}>퍼널 하나에 모델 최대 5개</Pill>
      <Pill x={468} y={456} w={420} h={70} a={eleven} tone="warn" size={28}>곱하는 조합 11가지 비교</Pill>
      <Pill x={0} y={548} w={888} h={70} a={dozens} tone="bad" size={28}>채널이 바뀌면 처음부터 · 퍼널 수십 개 → 트리 모델 수십 개</Pill>
      {Array.from({ length: 18 }).map((_, k) => (
        <Tree key={k} x={50 + k * 47} y={672} s={0.5} a={dozens} />
      ))}
    </Stage>
  );
};
