// 장면 4: 중요도 막대 → 비율로 자름 → 엘보(꺾이는 점)에서 자름 → 75개가 더 낫다 → 앞에 몰려서 → 뒤에도 쓸모 있는 피쳐. 캔버스 888x720.
import React from "react";
import { C, Stage, Timing } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const N = 40, X0 = 20, BW = 21, BASE = 470, MAXH = 390;
const imp = (i: number) => 0.88 * Math.exp(-i / 2.6) + 0.16 * Math.exp(-i / 22);
const ELBOW = 4, RATIO = 8;

export const Elbow: React.FC<Timing> = ({ marks }) => {
  const [bars, ratio, elbow, cut, more, crowd, rest] = useMarks(marks, 7, [0]);
  return (
    <Stage>
      <At x={0} y={0} a={bars} style={{ fontSize: 26, fontWeight: 800, color: C.gray }}>피쳐 중요도 (높은 순)</At>
      {Array.from({ length: N }).map((_, i) => {
        const h = imp(i) * MAXH;
        const show = Math.max(0, Math.min(1, bars * 1.6 - i / N));
        const head = i < ELBOW;
        const dim = i >= ELBOW ? cut * (1 - rest) * 0.7 : 0;
        const col = head && crowd > 0.5 ? C.warn : i >= ELBOW && i < 30 && rest > 0.5 ? C.ok : C.ink;
        return <At key={i} x={X0 + i * BW} y={BASE - h * show} w={BW - 5} h={h * show} style={{ background: col, borderRadius: 3, opacity: 1 - dim }} />;
      })}
      <At x={X0} y={BASE} w={N * BW} h={3} a={bars} style={{ background: C.txt }} />
      {/* 비율로 자름 */}
      <At x={X0 + RATIO * BW - 3} y={60} w={4} h={BASE - 60} a={ratio * (1 - elbow)} style={{ background: C.gray }} />
      <At x={X0 + RATIO * BW + 10} y={70} a={ratio * (1 - elbow)} style={{ fontSize: 26, fontWeight: 800, color: C.gray }}>상위 20%만 남긴다 · 언제나 같은 비율</At>
      {/* 엘보 */}
      <At x={X0 + ELBOW * BW - 14} y={BASE - imp(ELBOW) * MAXH - 20} w={36} h={36} a={elbow} style={{ borderRadius: 18, border: `4px solid ${C.bad}`, boxSizing: "border-box" }} />
      <At x={X0 + ELBOW * BW + 30} y={BASE - imp(ELBOW) * MAXH - 60} a={elbow} style={{ fontSize: 28, fontWeight: 800, color: C.bad }}>엘보: 꺾이는 점</At>
      <At x={X0 + ELBOW * BW - 2} y={60} w={4} h={BASE - 60} a={cut} style={{ background: C.bad }} />

      <Pill x={0} y={510} w={888} h={62} a={more} tone="bad" size={28}>엘보에서 자른 20개 모델 &lt; 75개를 쓴 모델</Pill>
      <Pill x={0} y={584} w={420} h={62} a={crowd} tone="warn" size={25}>중요도가 앞쪽에 몰림</Pill>
      <Pill x={468} y={584} w={420} h={62} a={rest} tone="ok" size={25}>뒤에도 보탬이 되는 피쳐</Pill>
      <At x={0} y={664} w={888} a={rest} style={{ fontSize: 26, color: C.gray, textAlign: "center" }}>곡선 모양만 보고 자르면 쓸모 있는 피쳐를 버린다</At>
    </Stage>
  );
};
