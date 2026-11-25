// 장면 4: 정답이 없는 과제 → 샘플을 빼면 분류가 '아니오'를 못 배운다 → 샘플은 두고 손실만 가린다.
import React from "react";
import { Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

const COLS = [
  { x: 80, w: 250, head: "샘플", sub: "" },
  { x: 330, w: 320, head: "신청할까?", sub: "분류" },
  { x: 650, w: 320, head: "결과 ①", sub: "수치" },
  { x: 970, w: 320, head: "결과 ②", sub: "수치" },
  { x: 1290, w: 410, head: "손실에 넣는 칸", sub: "" },
];
const ROWS = [
  { who: "유저 1", yes: true, v: ["1.2", "3.4"] },
  { who: "유저 2", yes: false, v: [] },
  { who: "유저 3", yes: true, v: ["0.8", "2.1"] },
  { who: "유저 4", yes: false, v: [] },
];
const TOP = 70, HEAD_H = 120, ROW_H = 124;

export const Mask: React.FC<Timing> = ({ marks }) => {
  const table = useAt(marks, 0), no = useAt(marks, 1), drop = useAt(marks, 2), mask = useAt(marks, 3), loss = useAt(marks, 4);
  const struck = drop * (1 - mask);
  return (
    <Stage>
      {COLS.map((c, j) => (
        <Box key={c.head} x={c.x} y={TOP} w={c.w} h={HEAD_H} a={j === 4 ? mask : table} ec="transparent" fc="transparent" size={34} bold color={j === 4 ? C.ink : C.txt} rise={false}>
          {c.head}
          {c.sub && <span style={{ fontSize: 26, fontWeight: 400, color: C.gray }}>{c.sub}</span>}
        </Box>
      ))}
      <div style={{ position: "absolute", left: 80, top: TOP + HEAD_H, width: 1620, height: 4, background: C.txt, opacity: table }} />
      {ROWS.map((r, i) => {
        const y = TOP + HEAD_H + 10 + i * ROW_H;
        const fade = r.yes ? 1 : 1 - struck * 0.55;
        return (
          <React.Fragment key={r.who}>
            <Box x={80} y={y} w={250} h={ROW_H - 14} a={table * fade} ec="transparent" fc="transparent" size={34} rise={false}>
              {r.who}
            </Box>
            <Box x={350} y={y} w={280} h={ROW_H - 14} a={table * fade} ec={r.yes ? C.line : no > 0 ? C.warn : C.line} fc={r.yes ? "#FFFFFF" : no > 0 ? C.warnT : "#FFFFFF"} lw={r.yes ? 3 : 3 + no * 2} size={36} bold rise={false}>
              {r.yes ? "예" : "아니오"}
            </Box>
            {[0, 1].map((k) => (
              <Box
                key={k}
                x={670 + k * 320} y={y} w={280} h={ROW_H - 14} a={table * fade} rise={false}
                ec={r.yes ? C.line : C.soft}
                fc={r.yes ? "#FFFFFF" : mask > 0 ? hatch : "#FFFFFF"}
                size={r.yes ? 36 : 28} color={r.yes ? C.txt : C.gray}
              >
                {r.yes ? r.v[k] : <span style={{ opacity: no }}>{mask > 0.5 ? "손실에서 뺌" : "정답 없음"}</span>}
              </Box>
            ))}
            <Box x={1310} y={y} w={390} h={ROW_H - 14} a={mask} ec={C.ink} fc={C.inkT} size={30} bold color={C.ink}>
              {r.yes ? "분류 ✓  결과①② ✓" : "분류 ✓"}
            </Box>
            {/* 샘플을 통째로 뺀다 */}
            {!r.yes && <div style={{ position: "absolute", left: 80, top: y + (ROW_H - 14) / 2 - 3, width: 1210 * struck, height: 6, background: C.bad, borderRadius: 3 }} />}
          </React.Fragment>
        );
      })}

      <Box x={240} y={760} w={1300} h={110} a={struck} ec={C.bad} fc={C.badT} r={55} size={38} bold color={C.bad}>
        샘플을 빼면 → 분류 과제가 &apos;아니오&apos;를 못 배운다
      </Box>
      <Box x={140} y={770} w={1500} h={110} a={loss} ec={C.ink} fc={C.inkT} r={55} size={36} bold color={C.ink}>
        손실 = 모델의 답이 정답에서 틀린 정도 → 이 값을 줄이는 쪽으로 배운다
      </Box>
      <Label x={888} y={930} a={loss} size={30} color={C.gray}>
        정답이 있는 칸만 손실에 더한다
      </Label>
    </Stage>
  );
};

const hatch = `repeating-linear-gradient(45deg, ${C.soft} 0 10px, #FFFFFF 10px 22px)`;
