// 장면 5: 사례 1 — 목적마다 트리 하나 → 입력 두 요약을 섞어 전문가를 지나 수십 개 확률을 한 번에. 아래에서 위로 쌓는다. 캔버스 888x700.
import React from "react";
import { Arrow, Box, C, Card, Label, Stage, Timing, Tree, useAt } from "../lib/ui";

export const Case1: React.FC<Timing> = ({ marks }) => {
  const [trees, seq, prof, mixA, exp, out, consent, weight] = [0, 1, 2, 3, 4, 5, 6, 7].map((i) => useAt(marks, i));
  return (
    <Stage>
      {/* 전: 목적마다 트리 모델 하나씩 */}
      {Array.from({ length: 8 }).map((_, k) => (
        <Tree key={k} x={70 + k * 107} y={96} s={0.9} a={trees * (1 - out)} />
      ))}
      <Label x={444} y={28} a={trees * (1 - out)} size={30} bold color={C.gray} w={888}>전에는 목적마다 트리 모델 하나씩</Label>

      {/* 후: 수십 개 행동 확률을 한 번에 */}
      <Label x={444} y={28} a={out * (1 - weight)} size={30} bold color={C.ink} w={888}>수십 개 행동 확률을 한 번에</Label>
      <Label x={444} y={28} a={weight} size={28} bold color={C.warn} w={888}>드문 행동일수록 맞힌 사례에 무게를 더 (상한 있음)</Label>
      {Array.from({ length: 10 }).map((_, k) => {
        const rare = k % 4 === 0;
        return (
          <Box key={k} x={4 + k * 88} y={58} w={76} h={84} a={out} r={10} rise={false}
            ec={rare ? (weight > 0.5 ? C.warn : C.ink) : C.line} fc={rare && weight > 0.5 ? C.warnT : "#FFFFFF"} lw={rare ? 3 + weight * 2 : 3} size={28} color={C.gray}>
            %
          </Box>
        );
      })}
      <Arrow x1={444} y1={204} x2={444} y2={150} a={out} />

      <Box x={0} y={212} w={420} h={100} a={exp} ec={C.ink} fc={C.inkT} size={32} bold color={C.ink}>공유 전문가</Box>
      <Box x={468} y={212} w={420} h={100} a={exp} ec={C.warn} fc={C.warnT} size={32} bold>행동별 전문가</Box>
      <Arrow x1={444} y1={384} x2={444} y2={320} a={exp} />

      <Box x={124} y={392} w={640} h={92} a={mixA} ec={C.ink} fc={C.inkT} lw={4} size={32} bold color={C.ink}>두 요약을 섞는다</Box>
      <Arrow x1={210} y1={556} x2={330} y2={494} a={mixA} />
      <Arrow x1={678} y1={556} x2={558} y2={494} a={mixA} />

      <Card x={0} y={562} w={420} h={138} a={seq} head="최근 행동 기록" sub={["시간 순서대로 읽는다"]} />
      <Card x={468} y={562} w={420} h={138} a={prof} head="유저 프로필" ec={consent > 0.5 ? C.ink : C.line} lw={3 + consent * 2}
        sub={[<span key="c" style={{ color: consent > 0.5 ? C.ink : C.gray, fontWeight: consent > 0.5 ? 800 : 400 }}>{consent > 0.5 ? "동의 기반 정보만" : "프로필 요약"}</span>]} />
    </Stage>
  );
};
