// 장면 8-2: 사람이 하는 판단 셋 ↔ 파이프라인이 하는 비교 넷 → 숫자를 믿을 수 있어야 → '왜 하필 이 날만?'. 캔버스 888x560.
import React from "react";
import { C, Label, Stage, Timing } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const HUMAN = ["무엇을 예측할지 정한다", "쓰기에 충분한지 살핀다", "채택할지 결정한다"];
const PIPE = ["피쳐 수", "모델 구조", "기존 모델과 비교", "입력 점검"];

export const Closing: React.FC<Timing> = ({ marks }) => {
  const [focus, h1, h2, h3, auto, trust, why] = useMarks(marks, 7);
  const ha = [h1, h2, h3];
  return (
    <Stage>
      <Label x={210} y={22} a={focus} size={28} bold color={C.ink} w={420}>사람: 판단</Label>
      <Label x={678} y={22} a={auto} size={28} bold color={C.gray} w={420}>파이프라인: 비교</Label>
      {HUMAN.map((t, i) => (
        <At key={t} x={0} y={60 + i * 96} w={420} h={80} a={ha[i]} style={{ translate: `0px ${(1 - ha[i]) * 14}px`, borderRadius: 14, boxSizing: "border-box", border: `4px solid ${C.ink}`, background: C.inkT, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28, fontWeight: 800, color: C.ink }}>{t}</At>
      ))}
      {PIPE.map((t, i) => (
        <At key={t} x={468} y={60 + i * 72} w={420} h={58} a={auto} style={{ borderRadius: 12, boxSizing: "border-box", border: `3px solid ${C.line}`, background: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 25, color: C.gray }}>{`${i + 1}. ${t}`}</At>
      ))}
      <Pill x={0} y={374} w={888} h={64} a={trust} tone="ink" size={27}>판단은 숫자를 믿을 수 있을 때만 의미가 있다</Pill>
      <At x={244} y={460} w={400} h={86} a={why} style={{ translate: `0px ${(1 - why) * 14}px`, borderRadius: 43, background: C.warn, color: "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 38, fontWeight: 800 }}>왜 하필 이 날만?</At>
    </Stage>
  );
};
