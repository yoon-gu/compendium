// 장면 8: 하니스 → 전용 통로 → 런타임 프록시(막을 곳 차단) → OpenSandbox(이그레스 허용 목적지, 대체값→진짜 키) → 업무 서비스. 환경변수에 진짜 키를 두면 샌다.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Proxy: React.FC<Timing> = ({ marks }) => {
  const [pipe, noway, two, egress, key, env, log, ph, swap] = [0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => useAt(marks, i));
  const steps = [
    { t: "하니스", s: "갇힌 실행 환경", a: pipe, ec: C.warn, fc: C.warnT },
    { t: "런타임 프록시", s: "① 닿으면 안 되는 곳 차단", a: two, ec: C.ink, fc: C.inkT },
    { t: "OpenSandbox", s: "② 나가도 되는 목적지만 (egress)", a: egress, ec: C.ink, fc: C.inkT },
    { t: "업무 서비스", s: "", a: egress, ec: C.line, fc: "#FFFFFF" },
  ];
  return (
    <Stage>
      {steps.map((st, k) => (
        <React.Fragment key={st.t}>
          <Box x={0} y={k * 150} w={500} h={110} a={st.a} ec={st.ec} fc={st.fc} lw={3} size={28} bold>
            {st.t}
            {st.s && <span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>{st.s}</span>}
          </Box>
          {k < 3 && <Arrow x1={250} y1={k * 150 + 114} x2={250} y2={k * 150 + 146} a={steps[k + 1].a} />}
        </React.Fragment>
      ))}
      <Label x={694} y={130} a={noway} size={22} color={C.gray} w={380}>전용 통로 하나 — 다른 길 없음</Label>
      {/* 키: 환경변수에 두면 */}
      <Box x={530} y={0} w={358} h={110} a={key * (1 - ph)} ec={C.bad} fc={C.badT} size={22} bold color={C.bad}>
        환경변수에 진짜 키
        <span style={{ fontSize: 20, fontWeight: 400, opacity: env }}>코드가 읽는다{log > 0.5 ? " · 로그에 섞인다" : ""}</span>
      </Box>
      {/* 대체값 → 진짜 키 */}
      <Box x={530} y={0} w={358} h={110} a={ph} ec={C.ok} fc={C.okT} size={22} bold color={C.ok}>
        헤더에 대체값
        <span style={{ fontSize: 20, fontWeight: 400, fontFamily: "monospace" }}>key: PLACEHOLDER</span>
      </Box>
      <Arrow x1={530} y1={360} x2={506} y2={360} a={swap} color={C.ok} />
      <Box x={530} y={300} w={358} h={120} a={swap} ec={C.ok} fc={C.okT} size={22} bold color={C.ok}>
        나가는 길에 바꿔 끼움
        <span style={{ fontSize: 20, fontWeight: 400, fontFamily: "monospace" }}>key: sk-••••</span>
      </Box>
      <Label x={709} y={500} a={swap} size={24} bold color={C.ink} w={358}>하니스는 키를 모른다</Label>
    </Stage>
  );
};
