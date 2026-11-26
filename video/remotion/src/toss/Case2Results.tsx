// 장면 9: 오차 막대가 기존 100 에서 21·34 로 줄고 → AUC 약 10% → 공정한 채점. 캔버스 888x610(아래에 약어 각주 한 줄).
import React from "react";
import { Box, C, Label, Stage, Timing, mix, useAt } from "../lib/ui";

const ROWS = [
  { name: "수치 과제 ① 오차", v: 21, note: "MAE 약 79% 감소" },
  { name: "수치 과제 ② 오차", v: 34, note: "MAE 약 66% 감소" },
];

export const Case2Results: React.FC<Timing> = ({ marks }) => {
  const base = useAt(marks, 0), r1 = useAt(marks, 1, 1.4), r2 = useAt(marks, 2, 1.4), auc = useAt(marks, 3), fair = useAt(marks, 4);
  const abs = (s: React.CSSProperties): React.CSSProperties => ({ position: "absolute", ...s });
  return (
    <Stage>
      <div style={abs({ left: 0, top: 0, fontSize: 28, color: C.gray, opacity: base })}>상품별 트리 모델 대비</div>
      {ROWS.map((r, i) => {
        const y = 60 + i * 176, p = [r1, r2][i], v = mix(100, r.v, p);
        return (
          <React.Fragment key={r.name}>
            <div style={abs({ left: 0, top: y, fontSize: 32, fontWeight: 800, opacity: base })}>{r.name}</div>
            <div style={abs({ right: 0, top: y + 2, fontSize: 30, fontWeight: 800, color: C.ink, opacity: p })}>{r.note}</div>
            <div style={abs({ left: 0, top: y + 52, width: 888, height: 48, borderRadius: 10, background: C.soft, opacity: base })} />
            <div style={abs({ right: 14, top: y + 60, fontSize: 26, color: C.gray, opacity: base })}>기존 100</div>
            <div style={abs({ left: 0, top: y + 108, width: (888 * v) / 100, height: 48, borderRadius: 10, background: p > 0 ? C.ink : C.line, opacity: base })} />
            <div style={abs({ left: (888 * v) / 100 + 14, top: y + 114, fontSize: 28, fontWeight: 800, color: C.ink, opacity: p > 0.98 ? 1 : 0 })}>{r.v}</div>
          </React.Fragment>
        );
      })}
      <Box x={0} y={424} w={888} h={120} a={auc} ec={C.ok} fc={C.okT} size={34} bold color={C.ok}>
        분류 과제 AUC 약 10% 향상 (상대값)
      </Box>
      <Label x={444} y={584} a={fair} size={26} color={C.gray} w={888}>같은 유저 · 같은 상품만 모아 같은 실제 결과로 채점</Label>
    </Stage>
  );
};
