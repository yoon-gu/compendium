// 장면 3-2: 멀티태스크 학습의 두 쓰임새 — 왼쪽(지난 글 TASTE) 다음 오른쪽(이번 글). 캔버스 888x690.
import React from "react";
import { Arrow, C, Card, Label, Stage, Timing, useAt } from "../lib/ui";

export const TwoUses: React.FC<Timing> = ({ marks }) => {
  const [two, rep, taste, now, pred, use] = [0, 1, 2, 3, 4, 5].map((i) => useAt(marks, i));
  const cols = [
    { x: 0, a: [two, rep, rep, taste], title: "공유 표현을 넘긴다", c1: ["여러 행동을", "함께 학습"], h2: "다른 서비스 모델", c2: ["표현을", "가져다 쓴다"], tag: "지난 글 TASTE", ink: false },
    { x: 468, a: [now, pred, use, now], title: "예측값을 바로 쓴다", c1: ["여러 과제를", "함께 학습"], h2: "마케팅 · 서비스", c2: ["예측을", "바로 쓴다"], tag: "이번 글", ink: true },
  ];
  return (
    <Stage>
      {cols.map((c) => {
        const col = c.ink ? C.ink : C.txt;
        return (
          <React.Fragment key={c.x}>
            <div style={{ position: "absolute", left: c.x, top: 0, width: 420, height: 690, borderRadius: 18, boxSizing: "border-box", opacity: c.a[0], background: c.ink ? C.inkT : C.soft, border: c.ink ? `4px solid ${C.ink}` : "none" }} />
            <Label x={c.x + 210} y={58} a={c.a[0]} size={32} bold color={col} w={420}>{c.title}</Label>
            <Card x={c.x + 30} y={106} w={360} h={190} a={c.a[1]} head="멀티태스크 모델" sub={c.c1} ec={c.ink ? C.ink : C.line} hc={col} />
            <Arrow x1={c.x + 210} y1={308} x2={c.x + 210} y2={374} a={c.a[2]} />
            <Card x={c.x + 30} y={384} w={360} h={190} a={c.a[2]} head={c.h2} sub={c.c2} ec={c.ink ? C.ink : C.line} hc={col} />
            <Label x={c.x + 210} y={630} a={c.a[3]} size={30} bold color={col} w={420}>{c.tag}</Label>
          </React.Fragment>
        );
      })}
    </Stage>
  );
};
