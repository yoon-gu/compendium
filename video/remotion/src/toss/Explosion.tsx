// 장면 2: 질문 하나에 트리 하나 → 과제 × 상품 → 수백 개 → 매일. 캔버스 888x720(세로 영상 본문 폭).
import React from "react";
import { Box, C, Label, Stage, Timing, Tree, useAt } from "../lib/ui";

const TASKS = ["신청할까", "어떤 결과", "어떤 조건"];
const PRODUCTS = ["상품 1", "상품 2", "상품 3", "상품 4", "상품 5", "상품 6"];
const ROWS = 12, COLS = 21;

export const Explosion: React.FC<Timing> = ({ marks }) => {
  const one = useAt(marks, 0), tasks = useAt(marks, 1), prods = useAt(marks, 2), times = useAt(marks, 3);
  const many = useAt(marks, 4, 1.2), daily = useAt(marks, 5);
  const small = 1 - many;                       // 작은 격자는 수백 개 격자가 들어오면 물러난다
  const colX = (j: number) => 266 + j * 112;
  const rowY = (i: number) => 175 + i * 140;
  return (
    <Stage>
      {/* 과제 줄 머리 */}
      {TASKS.map((t, i) => (
        <Box key={t} x={0} y={rowY(i) - 46} w={200} h={92} a={(i === 0 ? one : tasks) * small} ec={C.ink} fc={C.inkT} size={30} bold color={C.ink}>
          {t}?
        </Box>
      ))}
      {/* 상품 열 머리 */}
      {PRODUCTS.map((p, j) => (
        <Label key={p} x={colX(j)} y={60} a={(j === 0 ? one : prods) * small} size={26} color={C.gray} bold w={110}>
          {p}
        </Label>
      ))}
      {/* 트리 격자: (0,0) → 첫 열 → 전체 */}
      {TASKS.map((_, i) =>
        PRODUCTS.map((__, j) => {
          const a = i === 0 && j === 0 ? one : j === 0 ? tasks : prods;
          return <Tree key={`${i}-${j}`} x={colX(j)} y={rowY(i)} s={1.35} a={a * small} />;
        }),
      )}
      <Box x={44} y={600} w={800} h={92} a={times * small} ec={C.warn} fc={C.warnT} r={46} size={36} bold color={C.txt}>
        모델 수 = 과제 수 × 상품 수
      </Box>

      {/* 수백 개 */}
      {Array.from({ length: ROWS }).map((_, i) =>
        Array.from({ length: COLS }).map((__, j) => (
          <Tree key={`m${i}-${j}`} x={24 + j * 42} y={140 + i * 38} s={0.5} a={interp(many, (i * COLS + j) / (ROWS * COLS))} color={daily > 0 && (i * 7 + j) % 5 === 0 ? C.warn : C.ink} />
        )),
      )}
      <Label x={444} y={56} a={many} size={52} bold color={C.ink} w={888}>
        수십 개, 수백 개
      </Label>
      <Box x={24} y={608} w={840} h={92} a={daily} ec={C.warn} fc={C.warnT} r={46} size={34} bold>
        매일 학습 · 배포 · 모니터링 × 수백
      </Box>
    </Stage>
  );
};

// 격자를 앞에서부터 차례로 채운다: 전체 진행 p 에서 순번 k(0-1) 칸의 투명도.
const interp = (p: number, k: number) => Math.max(0, Math.min(1, (p - k * 0.7) / 0.3));
