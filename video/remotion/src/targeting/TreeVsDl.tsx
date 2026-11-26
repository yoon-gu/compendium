// 장면 5-3: 운영 퍼널 두 곳은 AITM 이 앞섬(+1.4%, +0.6%) ↔ 양성이 적은 퍼널은 트리가 앞섬(+7.5%·+7.2%, 같은 조건 +2.9%) → 데이터 적으면 트리부터. 캔버스 888x720.
import React from "react";
import { Box, C, Stage, Timing } from "../lib/ui";
import { At, Bar, Pill, useMarks } from "./parts";

const MAX = 8;

export const TreeVsDl: React.FC<Timing> = ({ marks }) => {
  const [ops, b14, b06, opp, b7, b3, stable, early] = useMarks(marks, 8, [1, 2, 4, 5]);
  const row = (x: number, y: number, label: string, v: number, p: number, col: string) => (
    <>
      <At x={x + 20} y={y} a={Math.min(1, p * 3)} style={{ fontSize: 25, fontWeight: 800 }}>{label}</At>
      <Bar x={x + 20} y={y + 40} w={380} h={34} p={(v / MAX) * p} a={Math.min(1, p * 3)} color={col} />
      <At x={x + 20} y={y + 80} w={380} a={p} style={{ fontSize: 26, fontWeight: 800, color: col, textAlign: "right" }}>+{v}%</At>
    </>
  );
  return (
    <Stage>
      <Box x={0} y={0} w={420} h={480} a={ops} ec={C.ink} fc={C.inkT} lw={4} />
      <At x={20} y={20} w={380} a={ops} style={{ fontSize: 28, fontWeight: 800, color: C.ink }}>운영 퍼널 두 곳<br /><span style={{ fontSize: 24, fontWeight: 400, color: C.gray }}>AITM 이 트리 조합보다 (AUROC)</span></At>
      {row(0, 130, "2단계 퍼널", 1.4, b14, C.ink)}
      {row(0, 270, "3단계 퍼널", 0.6, b06, C.ink)}
      <At x={20} y={420} w={380} a={b06} style={{ fontSize: 22, color: C.gray }}>모델 수는 줄고 성능은 지켰다</At>

      <Box x={468} y={0} w={420} h={480} a={opp} ec={C.warn} fc={C.warnT} lw={4} />
      <At x={488} y={20} w={380} a={opp} style={{ fontSize: 28, fontWeight: 800 }}>양성이 적은 퍼널<br /><span style={{ fontSize: 24, fontWeight: 400, color: C.gray }}>트리가 AITM 보다 (AUROC)</span></At>
      {row(468, 130, "CatBoost · XGBoost", 7.5, b7, C.warn)}
      {row(468, 270, "XGBoost, 같은 학습 조건", 2.9, b3, C.warn)}
      <At x={488} y={420} w={380} a={b7} style={{ fontSize: 22, color: C.gray }}>XGBoost 는 +7.2%</At>

      <Pill x={0} y={510} w={888} h={74} a={stable} tone="bad" size={27}>정답이 적으면 파라미터 많은 모델은 불안정</Pill>
      <Pill x={0} y={606} w={888} h={96} a={early} tone="ink" size={27}>초기엔 트리 + auto_k → 바꾸기 전 퍼널마다 나란히 잰다</Pill>
    </Stage>
  );
};
