// 장면 2: 2년 전엔 손으로 → 학습은 2주 → 1일. 남은 질문 '써도 되나?' → 비교 네 가지가 차례로 → 손으로 하던 것이 파이프라인으로. 캔버스 888x720.
import React from "react";
import { C, Label, Stage, Timing } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const QS = ["피쳐를 몇 개 쓸까", "어떤 구조를 쓸까", "기존 모델보다 나은가", "입력 데이터를 믿어도 되나"];

export const Questions: React.FC<Timing> = ({ marks }) => {
  const [before, fast, q1, q2, q3, q4, hand, pipe] = useMarks(marks, 8);
  const q = [q1, q2, q3, q4];
  return (
    <Stage>
      <Pill x={44} y={0} w={800} h={84} a={before * (1 - fast)} tone="gray" size={28}>2년 전: 노트북 켜고 · 쿼리 짜고 · 함수 만들고</Pill>
      <Pill x={44} y={0} w={800} h={84} a={fast} tone="ok" size={32}>모델 학습  두 주 → 하루</Pill>
      <Label x={444} y={142} a={q1} size={32} bold w={888}>이 모델을 써도 되나? → 네 번 비교한다</Label>
      {QS.map((t, i) => (
        <At key={t} x={0} y={190 + i * 128} w={888} h={108} a={q[i]} style={{ translate: `0px ${(1 - q[i]) * 20}px`, borderRadius: 16, boxSizing: "border-box", border: `3px solid ${pipe > 0.5 ? C.ink : C.line}`, background: pipe > 0.5 ? C.inkT : "#FFFFFF", display: "flex", alignItems: "center", padding: "0 24px", gap: 20 }}>
          <div style={{ width: 60, height: 60, borderRadius: 30, flex: "none", background: C.ink, color: "#FFFFFF", fontSize: 32, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
          <div style={{ fontSize: 33, fontWeight: 800, flex: 1 }}>{t}</div>
          <div style={{ position: "relative", width: 170, height: 56 }}>
            <Pill x={0} y={0} w={170} a={hand * (1 - pipe)} tone="warn" size={26}>손으로</Pill>
            <Pill x={0} y={0} w={170} a={pipe} tone="ink" size={26}>파이프라인</Pill>
          </div>
        </At>
      ))}
    </Stage>
  );
};
