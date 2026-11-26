// 장면 7-3: 세 평가일 중 마지막 날만 크게 앞섬 → 피쳐 단독 AUROC 를 날짜별로 → 두 피쳐만 +17% → 월 단위 집계가 월말까지 다시 계산됨 → 기준일 뒤 행동 = 미래 정보 → SHAP 과 단독 AUROC 의 차이. 캔버스 888x610.
import React from "react";
import { C, Stage, Timing } from "../lib/ui";
import { At, Pill, useMarks } from "./parts";

const DAYS = [{ d: "A", old: 0.8, nw: 0.76 }, { d: "B", old: 0.8, nw: 0.77 }, { d: "C", old: 0.8, nw: 0.97 }];
const FEATS = [{ f: "feat01", b: "+4%", c: "+17%" }, { f: "feat02", b: "+4%", c: "+17%" }, { f: "나머지 피쳐", b: "거의 같음", c: "거의 같음" }];

export const Leak: React.FC<Timing> = ({ marks }) => {
  const [days, lastDay, single, p17, monthly, after, future, shap] = useMarks(marks, 8);
  return (
    <Stage>
      {/* 세 평가일 */}
      {DAYS.map((d, i) => {
        const x = i * 160, hi = i === 2 && lastDay > 0.5;
        return (
          <React.Fragment key={d.d}>
            <At x={x + 20} y={150 - d.old * 120} w={50} h={d.old * 120} a={days} style={{ background: C.line, borderRadius: 6 }} />
            <At x={x + 76} y={150 - d.nw * 120} w={50} h={d.nw * 120} a={days} style={{ background: hi ? C.warn : C.ink, borderRadius: 6 }} />
            <At x={x} y={156} w={146} a={days} style={{ fontSize: 23, textAlign: "center", fontWeight: 800 }}>평가일 {d.d}</At>
          </React.Fragment>
        );
      })}
      <At x={0} y={0} a={days} style={{ fontSize: 20, color: C.gray }}>회색 기존 · 초록 새 모델</At>
      <At x={360} y={10} w={110} a={lastDay} style={{ fontSize: 40, fontWeight: 800, color: C.warn, textAlign: "center" }}>?</At>

      {/* 피쳐 단독 AUROC */}
      <At x={500} y={0} a={single} style={{ fontSize: 23, fontWeight: 800 }}>피쳐 단독 AUROC (평가일 A 대비)</At>
      <At x={500} y={36} w={388} a={single} style={{ display: "grid", gridTemplateColumns: "150px 110px 120px", rowGap: 8, fontSize: 22 }}>
        <span style={{ color: C.gray }}>피쳐</span><span style={{ color: C.gray }}>B</span><span style={{ color: C.gray }}>C</span>
        {FEATS.map((f, k) => (
          <React.Fragment key={f.f}>
            <span style={{ fontWeight: 800 }}>{f.f}</span>
            <span>{f.b}</span>
            <span style={{ fontWeight: 800, color: k < 2 && p17 > 0.5 ? C.bad : C.txt }}>{f.c}</span>
          </React.Fragment>
        ))}
      </At>

      {/* 한 달 타임라인 */}
      <At x={0} y={214} a={monthly} style={{ fontSize: 24, fontWeight: 800 }}>월 단위 피쳐는 달이 끝날 때까지 매일 다시 계산된다</At>
      <At x={20} y={300} w={848} h={6} a={monthly} style={{ background: C.txt, borderRadius: 3 }} />
      <At x={0} y={316} a={monthly} style={{ fontSize: 21, color: C.gray }}>1일</At>
      <At x={820} y={316} a={monthly} style={{ fontSize: 21, color: C.gray }}>말일</At>
      <At x={420} y={260} w={4} h={80} a={monthly} style={{ background: C.ink }} />
      <At x={360} y={344} w={130} a={monthly} style={{ fontSize: 21, fontWeight: 800, color: C.ink, textAlign: "center" }}>월중 기준일</At>
      <At x={20} y={262} w={400} h={30} a={monthly} style={{ background: C.ink, borderRadius: 6, opacity: monthly * 0.8 }} />
      <At x={424} y={262} w={444} h={30} a={after} style={{ background: C.bad, borderRadius: 6 }} />
      <Pill x={500} y={340} w={388} h={52} a={future} tone="bad" size={24}>기준일 뒤 행동 = 미래 정보</Pill>

      {/* SHAP 과 단독 AUROC */}
      <At x={0} y={420} w={420} h={170} a={shap} style={{ border: `3px solid ${C.line}`, borderRadius: 16, boxSizing: "border-box", background: "#FFFFFF", padding: "16px 20px" }}>
        <div style={{ fontSize: 28, fontWeight: 800 }}>SHAP</div>
        <div style={{ fontSize: 23, color: C.gray, marginTop: 10 }}>피쳐 ↔ 모델 점수</div>
        <div style={{ fontSize: 23, color: C.bad, marginTop: 6, fontWeight: 800 }}>실제 전환은 안 본다</div>
      </At>
      <At x={468} y={420} w={420} h={170} a={shap} style={{ border: `4px solid ${C.ink}`, borderRadius: 16, boxSizing: "border-box", background: C.inkT, padding: "16px 20px" }}>
        <div style={{ fontSize: 28, fontWeight: 800, color: C.ink }}>피쳐 단독 AUROC</div>
        <div style={{ fontSize: 23, color: C.gray, marginTop: 10 }}>피쳐 ↔ 정답</div>
        <div style={{ fontSize: 23, color: C.ink, marginTop: 6, fontWeight: 800 }}>SQL 로 몇 분이면 잰다</div>
      </At>
    </Stage>
  );
};
