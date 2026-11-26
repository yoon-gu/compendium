// 장면 4: 워크스페이스 > 에이전트 > 세션 → 사용자마다 파드 하나 → 서버·러너는 파드 밖, 런타임이 하니스를 가둔다 → DB 인증정보는 넘기지 않는다.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Units: React.FC<Timing> = ({ marks }) => {
  const [ws, agents, sess, pod, server, runner, runtime, secret] = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => useAt(marks, i));
  return (
    <Stage>
      <Box x={0} y={0} w={888} h={330} a={ws} ec={C.ink} fc={C.inkT} lw={4} r={18} rise={false} />
      <Label x={24} y={34} a={ws} size={28} bold color={C.ink} align="left" w={500}>워크스페이스 (사용자 1명)</Label>
      <Label x={864} y={34} a={pod} size={24} bold color={C.warn} align="right" w={400}>= 파드 하나</Label>
      {[["분석 에이전트", ["10월 대화", "11월 대화"]], ["문서 에이전트", ["초안 대화"]]].map(([a, ss], k) => (
        <React.Fragment key={a as string}>
          <Box x={24 + k * 432} y={70} w={408} h={90} a={agents} ec={C.ink} size={28} bold color={C.ink}>{a as string}</Box>
          {(ss as string[]).map((s, j) => (
            <Box key={s} x={24 + k * 432 + j * 210} y={190} w={196} h={110} a={sess} ec={C.line} r={14} size={24} rise={false}>
              세션
              <span style={{ fontSize: 22, color: C.gray }}>{s}</span>
            </Box>
          ))}
        </React.Fragment>
      ))}
      {/* 실행 흐름 */}
      <div style={{ position: "absolute", left: 0, top: 370, width: 560, height: 200, borderRadius: 16, border: `3px dashed ${C.line}`, opacity: server, boxSizing: "border-box" }} />
      <Label x={20} y={392} a={server} size={22} color={C.gray} align="left" w={400}>파드 밖</Label>
      <Box x={20} y={420} w={240} h={120} a={server} ec={C.line} size={28} bold>서버<span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>사용자·권한 확인</span></Box>
      <Arrow x1={266} y1={480} x2={300} y2={480} a={runner} />
      <Box x={304} y={420} w={240} h={120} a={runner} ec={C.line} size={28} bold>러너<span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>실행 환경 준비</span></Box>
      <Arrow x1={550} y1={480} x2={600} y2={480} a={runtime} />
      <Box x={604} y={420} w={284} h={120} a={runtime} ec={C.warn} fc={C.warnT} lw={4} size={28} bold>런타임<span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>하니스를 가두고 실행</span></Box>
      <Box x={0} y={600} w={888} h={90} a={secret} ec={C.bad} fc={C.badT} r={45} size={26} bold color={C.bad}>
        플랫폼 DB 인증정보는 하니스에 넘기지 않는다
      </Box>
    </Stage>
  );
};
