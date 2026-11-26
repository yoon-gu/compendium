// 장면 6-2: 순열 중요도는 부호가 섞이고 방향이 없다 → 크기(0-1, 거꾸로 쓰는 음수엔 !)와 방향(하위→상위 10% 값으로 바꾼 확률 변화, 오른 고객 비율)을 나눈다. 캔버스 888x720.
import React from "react";
import { C, Stage, Timing, mix } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const OLD = [{ f: "feat01", v: 0.42 }, { f: "feat02", v: 0.01 }, { f: "feat03", v: -0.004 }, { f: "feat04", v: -0.03 }];
const NEW = [
  { f: "feat01", imp: 1.0, d: "+0.01057", up: 85 },
  { f: "feat02", imp: 0.997, d: "n/a", up: -1 },
  { f: "feat03", imp: 0.991, d: "−0.00906", up: 17 },
  { f: "(예시)", imp: -0.12, d: "", up: -2 },
];

export const Direction: React.FC<Timing> = ({ marks }) => {
  const [contrib, perm, back, updown, split, bang, slide, p85, nn] = useMarks(marks, 9, [6]);
  const CX = 330, SC = 260;
  return (
    <Stage>
      <At x={0} y={0} a={contrib} style={{ fontSize: 26, fontWeight: 800, color: C.gray }}>예전: 순열 중요도 그대로</At>
      {OLD.map((o, i) => (
        <React.Fragment key={o.f}>
          <At x={0} y={44 + i * 44} a={perm} style={{ fontSize: 24 }}>{o.f}</At>
          <At x={o.v >= 0 ? CX : CX + o.v * SC * 8} y={48 + i * 44} w={Math.max(4, Math.abs(o.v) * SC * (o.v >= 0 ? 1 : 8))} h={26} a={perm} style={{ background: o.v >= 0 ? C.gray : C.bad, borderRadius: 5 }} />
        </React.Fragment>
      ))}
      <At x={CX - 2} y={40} w={3} h={180} a={perm} style={{ background: C.txt }} />
      <Pill x={480} y={50} w={408} h={58} a={back} tone="bad" size={22}>0에 가까운 음수: 기여 없음? 거꾸로?</Pill>
      <Pill x={480} y={124} w={408} h={58} a={updown} tone="bad" size={22}>높을수록 오르나, 내리나? 답이 없다</Pill>

      <At x={0} y={236} w={888} h={4} a={split} style={{ background: C.ink }} />
      <At x={0} y={252} a={split} style={{ fontSize: 28, fontWeight: 800, color: C.ink }}>지금: 크기와 방향을 나눠서</At>
      <At x={250} y={300} a={bang} style={{ fontSize: 22, color: C.gray }}>크기 (1위 = 1.000)</At>
      <At x={610} y={300} a={p85} style={{ fontSize: 22, color: C.gray }}>방향 (오른 고객 비율)</At>
      {NEW.map((r, i) => {
        const y = 336 + i * 52, neg = r.imp < 0;
        return (
          <React.Fragment key={r.f}>
            <At x={0} y={y} a={split} style={{ fontSize: 25, fontWeight: 800 }}>{i + 1}. {r.f}</At>
            <At x={250} y={y + 4} w={neg ? 30 : 300 * r.imp} h={28} a={bang} style={{ background: neg ? C.bad : C.ink, borderRadius: 6 }} />
            <At x={neg ? 288 : 250 + 300 * r.imp - 90} y={y} a={bang} style={{ fontSize: 23, fontWeight: 800, color: neg ? C.bad : "#FFFFFF" }}>{neg ? "−0.120 !" : r.imp.toFixed(3)}</At>
            <At x={610} y={y} a={p85} style={{ fontSize: 24, fontWeight: 800, color: r.up < 0 ? C.gray : r.up >= 50 ? C.ok : C.bad }}>
              {r.d}{r.up >= 0 ? ` (${r.up}%)` : ""}
            </At>
          </React.Fragment>
        );
      })}
      {/* 값 바꿔 보기 */}
      <At x={0} y={560} w={888} h={70} a={slide} style={{ border: `3px solid ${C.line}`, borderRadius: 35, boxSizing: "border-box", background: "#FFFFFF" }} />
      <At x={24} y={578} a={slide} style={{ fontSize: 22, color: C.gray }}>하위 10% 값</At>
      <At x={736} y={578} a={slide} style={{ fontSize: 22, color: C.gray }}>상위 10% 값</At>
      <At x={mix(160, 680, slide) - 22} y={573} w={44} h={44} a={slide} style={{ borderRadius: 22, background: C.ink }} />
      <At x={300} y={578} w={300} a={slide} style={{ fontSize: 22, fontWeight: 800, color: C.ink, textAlign: "center" }}>고객마다 확률이 오르나?</At>
      <Pill x={0} y={648} w={888} h={64} a={nn} tone="warn" size={24}>신경망은 고객마다 방향이 뒤집힐 수 있다 → 비율을 함께 본다</Pill>
    </Stage>
  );
};
