// 장면 9: 파드는 바뀐다 → 영속 볼륨에 파일·상태 → 새 파드가 다시 붙인다 → 메모리는 안 돌아온다 → 상태에 남길 것(질문·답만으론 모자람, 호출↔결과 짝, 압축 요약).
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, mix, useAt } from "../lib/ui";

export const Resume: React.FC<Timing> = ({ marks }) => {
  const [dies, pv, attach, mem, what, qa, pair, sum] = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => useAt(marks, i));
  return (
    <Stage>
      <Box x={0} y={0} w={360} h={130} a={1 - dies * 0.6} ec={C.ink} fc={C.inkT} size={28} bold color={C.ink} rise={false}>
        파드 1
        <span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>메모리 · 중간 계산</span>
      </Box>
      <Label x={180} y={65} a={dies} size={90} bold color={C.bad} w={360}>✕</Label>
      <Box x={528} y={0} w={360} h={130} a={attach} ec={C.ink} fc={C.inkT} size={28} bold color={C.ink}>
        파드 2
        <span style={{ fontSize: 22, fontWeight: 400, color: C.bad, opacity: mem }}>메모리는 비어 있다</span>
      </Box>
      <Box x={244} y={200} w={400} h={110} a={pv} ec={C.warn} fc={C.warnT} lw={4} size={28} bold>
        영속 볼륨
        <span style={{ fontSize: 22, fontWeight: 400, color: C.gray }}>작업 파일 · 대화 상태</span>
      </Box>
      <Arrow x1={240} y1={240} x2={mix(240, 180, 1)} y2={140} a={pv * (1 - dies)} color={C.line} />
      <Arrow x1={648} y1={240} x2={708} y2={140} a={attach} />
      <Label x={444} y={360} a={mem} size={24} color={C.gray} w={888}>메모리에만 있던 중간 계산은 다시 해야 한다</Label>

      <Label x={0} y={420} a={what} size={28} bold align="left" w={888}>대화 상태에 남길 것</Label>
      <Box x={0} y={456} w={888} h={42} a={qa} ec="transparent" fc="transparent" size={24} color={C.gray} rise={false}>
        <span style={{ textDecoration: "line-through" }}>화면의 질문과 답만</span>&nbsp;— 모자라다
      </Box>
      <Box x={0} y={510} w={420} h={90} a={pair} ec={C.ink} fc={C.inkT} size={24} bold color={C.ink}>
        도구 호출 ↔ 결과의 짝
      </Box>
      <Box x={468} y={510} w={420} h={90} a={sum} ec={C.ink} fc={C.inkT} size={24} bold color={C.ink}>
        긴 대화를 압축한 요약
      </Box>
    </Stage>
  );
};
