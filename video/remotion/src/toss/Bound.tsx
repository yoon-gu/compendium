// 장면 10-2: 하나라서 묶인다 — 큰 과제가 덮는다 → 작은 변경도 모든 과제 지표를 다시(매일 자동 채점) → 배포도 묶인다. 캔버스 888x700.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

export const Bound: React.FC<Timing> = ({ marks }) => {
  const [cover, lean, change, score, deploy, easy, hard] = [0, 1, 2, 3, 4, 5, 6].map((i) => useAt(marks, i, i === 1 ? 1.0 : 0.6));
  const abs = (s: React.CSSProperties): React.CSSProperties => ({ position: "absolute", ...s });
  return (
    <Stage>
      {/* 1. 데이터가 많은 과제가 덮는다 */}
      <Label x={0} y={22} a={cover} size={30} bold align="left" w={888}>데이터가 많은 과제가 드문 과제를 덮는다</Label>
      <div style={abs({ left: 0, top: 62, fontSize: 26, color: C.gray, opacity: cover })}>큰 과제</div>
      <div style={abs({ left: 130, top: 60, width: 560, height: 40, borderRadius: 8, background: C.ink, opacity: cover })} />
      <div style={abs({ left: 0, top: 118, fontSize: 26, color: C.gray, opacity: cover })}>드문 과제</div>
      <div style={abs({ left: 130, top: 116, width: 60, height: 40, borderRadius: 8, background: C.ok, opacity: cover })} />
      <Box x={0} y={170} w={888} h={64} a={lean} ec={C.warn} fc={C.warnT} r={32} size={26} bold rise={false}>
        <span style={{ display: "inline-block", rotate: `${-2 * lean}deg` }}>공유층이 정답 많은 과제 쪽으로 기운다</span>
      </Box>

      {/* 2. 작은 변경도 모든 과제를 다시 본다 */}
      <Box x={0} y={290} w={240} h={150} a={change} ec={C.ink} fc={C.inkT} lw={4} size={28} bold color={C.ink}>
        작은 변경
        <br />
        하나
      </Box>
      <Arrow x1={248} y1={365} x2={316} y2={365} a={change} lw={5} />
      {Array.from({ length: 6 }).map((_, k) => {
        const x = 330 + (k % 3) * 190, y = 290 + Math.floor(k / 3) * 82;
        return (
          <React.Fragment key={k}>
            <Box x={x} y={y} w={170} h={68} a={change} ec={score > 0.5 ? C.ok : C.line} fc={score > 0.5 ? C.okT : "#FFFFFF"} size={24} bold color={score > 0.5 ? C.ok : C.gray} rise={false}>
              {`과제 ${k + 1}${score > 0.5 ? " ✓" : ""}`}
            </Box>
          </React.Fragment>
        );
      })}
      <Label x={330} y={470} a={score} size={24} color={C.ok} bold align="left" w={560}>매일 실제 결과로 과제별 자동 채점</Label>

      {/* 3. 배포도 묶인다 */}
      <Label x={0} y={530} a={deploy} size={30} bold align="left" w={888}>배포도 묶인다</Label>
      <Box x={0} y={570} w={420} h={130} a={easy} ec={C.ok} fc={C.okT} size={28} bold color={C.ok}>
        재학습 · 배포 한 번
        <span style={{ fontSize: 24, fontWeight: 400, color: C.gray }}>그래서 편하다</span>
      </Box>
      <Box x={468} y={570} w={420} h={130} a={hard} ec={C.bad} fc={C.badT} size={28} bold color={C.bad}>
        한 과제만 따로
        <span style={{ fontSize: 24, fontWeight: 400, color: C.gray }}>고치거나 되돌리기 어렵다</span>
      </Box>
    </Stage>
  );
};
