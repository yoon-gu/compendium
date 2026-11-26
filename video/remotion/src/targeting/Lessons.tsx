// 장면 8: 정리 세 가지 — 실험으로 정한다 / 손일을 줄였다 / 계속 의심했다. 근거가 언급될 때 한 줄씩. 캔버스 888x720.
import React from "react";
import { C, Stage, Timing } from "../lib/ui";
import { At, useMarks } from "./parts";

export const Lessons: React.FC<Timing> = ({ marks }) => {
  const a = useMarks(marks, 8);
  const cards = [
    { h: "실험으로 정한다", y: 0, hh: 200, lines: [["피쳐 −84%에도 성능 그대로", a[1]], ["딥러닝이 늘 낫다고 가정하지 않는다", a[1]]], show: a[0] },
    { h: "손일을 줄였다", y: 220, hh: 200, lines: [["조합 11가지 비교 → 라벨 테이블 하나", a[2]], ["평가 30분 → 1분", a[3]]], show: a[2] },
    { h: "계속 의심했다", y: 440, hh: 280, lines: [["명단이 흔들리면 → 모델 고정", a[5]], ["입력이 비면 → 점수를 멈춤", a[6]], ["한 날짜만 튀면 → 원인까지 쫓는다", a[7]]], show: a[4] },
  ] as const;
  return (
    <Stage>
      {cards.map((c, i) => {
        const last = i === 2 ? 1 : 1 - cards[i + 1].show;
        const ink = c.show * last > 0.5;
        return (
          <At key={c.h} x={0} y={c.y} w={888} h={c.hh} a={c.show} style={{ translate: `0px ${(1 - c.show) * 20}px`, borderRadius: 18, boxSizing: "border-box", border: `4px solid ${ink ? C.ink : C.line}`, background: ink ? C.inkT : "#FFFFFF", padding: "22px 30px" }}>
            <div style={{ fontSize: 36, fontWeight: 800, color: ink ? C.ink : C.txt }}>{c.h}</div>
            {c.lines.map(([t, la]) => (
              <div key={t as string} style={{ fontSize: 28, color: C.gray, marginTop: 14, opacity: la as number }}>· {t}</div>
            ))}
          </At>
        );
      })}
    </Stage>
  );
};
