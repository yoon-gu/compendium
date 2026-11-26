// 장면 7-2: 원천 테이블 1/4 이 멈춤 → 피쳐 조인은 빈 값(NULL)을 조용히 채움 → 13-21% → 매번 결손을 센다 → 10% 넘으면 적재 중단·알람 → 추세는 재학습 신호(0% → 6-8%). 캔버스 888x720.
import React from "react";
import { C, Stage, Timing, mix } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const STOPPED = new Set([2, 7, 9]);
const NULLS = new Set([3, 9, 14, 21, 26]);

export const Missing: React.FC<Timing> = ({ marks }) => {
  const [src, quarter, nul, pct, count, limit, alarm, signal, trend] = useMarks(marks, 9, [8]);
  const fill = 17 * count; // 게이지에 보이는 결손 비율(예시)
  return (
    <Stage>
      <At x={0} y={0} a={src} style={{ fontSize: 26, fontWeight: 800, color: C.gray }}>원천 테이블 12개</At>
      {Array.from({ length: 12 }).map((_, i) => {
        const off = STOPPED.has(i) && quarter > 0.5;
        return (
          <At key={i} x={(i % 6) * 148} y={40 + Math.floor(i / 6) * 62} w={136} h={50} a={src} style={{ borderRadius: 10, boxSizing: "border-box", border: `3px solid ${off ? C.bad : C.line}`, background: off ? C.badT : "#FFFFFF", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 21, fontWeight: 800, color: off ? C.bad : C.gray }}>
            {off ? "생산 중단" : `테이블 ${i + 1}`}
          </At>
        );
      })}
      <At x={0} y={172} w={888} a={quarter} style={{ fontSize: 22, color: C.bad, textAlign: "right" }}>몇 달 사이 4분의 1가량이 멈췄다</At>

      <At x={0} y={210} a={nul} style={{ fontSize: 26, fontWeight: 800, color: C.gray }}>그날의 피쳐 한 줄</At>
      {Array.from({ length: 30 }).map((_, i) => {
        const n = NULLS.has(i) && nul > 0.5;
        return <At key={i} x={i * 29.6} y={250} w={25} h={44} a={nul} style={{ borderRadius: 5, background: n ? `repeating-linear-gradient(45deg, ${C.soft} 0 6px, #FFFFFF 6px 12px)` : C.ink, border: n ? `2px dashed ${C.bad}` : "none", boxSizing: "border-box" }} />;
      })}
      <At x={0} y={304} w={888} a={nul} style={{ fontSize: 22, color: C.gray }}>데이터가 없으면 에러 없이 빈 값(NULL)</At>
      <Pill x={0} y={340} w={888} h={58} a={pct} tone="bad" size={24}>그대로 뒀다면 피쳐 13-21%가 빈 채로 점수가 나갔다</Pill>

      {/* 결손 게이지 */}
      <At x={0} y={424} a={count} style={{ fontSize: 24, fontWeight: 800 }}>추론마다 결손 피쳐를 센다</At>
      <At x={0} y={462} w={600} h={40} a={count} style={{ background: C.soft, borderRadius: 10 }} />
      <At x={0} y={462} w={(600 * fill) / 20} h={40} a={count} style={{ background: fill > 10 && limit > 0.5 ? C.bad : C.warn, borderRadius: 10 }} />
      <At x={300 - 2} y={452} w={4} h={60} a={limit} style={{ background: C.txt }} />
      <At x={262} y={514} a={limit} style={{ fontSize: 22, fontWeight: 800 }}>한도 10%</At>
      <Pill x={624} y={444} w={264} h={76} a={alarm} tone="bad" size={23}>배치 실패<br />점수 적재 ✗ · 알람</Pill>

      {/* 추세 */}
      <At x={0} y={560} a={signal} style={{ fontSize: 24, fontWeight: 800 }}>결손 비율의 추세 = 재학습 신호</At>
      <svg style={{ position: "absolute", left: 0, top: 596, opacity: signal }} width={888} height={124}>
        <line x1={20} y1={110} x2={560} y2={110} stroke={C.txt} strokeWidth={3} />
        {[0, 1, 2].map((k) => {
          const end = [6, 7, 8][k];
          const pts = Array.from({ length: 6 }, (_, t) => `${20 + t * 108},${110 - (end * mix(0, 1, Math.min(1, trend * 1.2 - t / 8)) * (t / 5)) * 11}`).join(" ");
          return <polyline key={k} points={pts} fill="none" stroke={[C.ink, C.ok, C.warn][k]} strokeWidth={4} />;
        })}
        <text x={600} y={40} fontSize={24} fontWeight={800} fill={C.ink} fontFamily="NanumGothic" opacity={trend}>모델 세 개</text>
        <text x={600} y={80} fontSize={24} fill={C.gray} fontFamily="NanumGothic" opacity={trend}>몇 달 사이 0% → 6-8%</text>
      </svg>
    </Stage>
  );
};
