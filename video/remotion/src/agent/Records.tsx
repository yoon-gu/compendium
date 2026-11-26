// 장면 11: 하려는 일마다 쓰는 기록 — 이어 가기(하니스 상태) · 지난 대화 보기(공통 실행 기록, OpenResponses) · 다른 하니스로 넘기기(요약 → 새 세션) → 사용자가 고른다.
import React from "react";
import { Arrow, Box, C, Label, Stage, Timing, useAt } from "../lib/ui";

const ROWS = [
  { job: "같은 하니스로 이어 가기", rec: "하니스 고유 상태", how: "하니스가 읽어 다음 요청 처리", c: C.warn, f: C.warnT },
  { job: "화면에서 지난 대화 보기", rec: "공통 실행 기록", how: "하니스를 띄우지 않고 조회", c: C.ink, f: C.inkT },
  { job: "다른 하니스로 넘기기", rec: "공통 기록 요약", how: "요약을 들고 새 세션 시작", c: C.ink, f: C.inkT },
];

export const Records: React.FC<Timing> = ({ marks }) => {
  const [show, diff, common, open, noRun, hand, sumA, fresh, pick] = [0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => useAt(marks, i));
  const rowA = [show, common, hand];
  const howA = [diff, noRun, fresh];
  return (
    <Stage>
      {ROWS.map((r, i) => (
        <React.Fragment key={r.job}>
          <Box x={0} y={i * 190} w={300} h={160} a={rowA[i]} ec={C.line} size={25} bold>{r.job}</Box>
          <Arrow x1={304} y1={i * 190 + 80} x2={344} y2={i * 190 + 80} a={rowA[i]} />
          <Box x={350} y={i * 190} w={538} h={160} a={i === 2 ? Math.max(hand * 0.999, sumA) : rowA[i]} ec={r.c} fc={r.f} lw={4} size={28} bold color={r.c === C.ink ? C.ink : C.txt}>
            {r.rec}
            {i === 1 && <span style={{ fontSize: 22, fontWeight: 400, color: C.gray, opacity: open }}>OpenResponses 형식 + 원본 이벤트</span>}
            <span style={{ fontSize: 22, fontWeight: 400, color: C.gray, opacity: howA[i] }}>{r.how}</span>
          </Box>
        </React.Fragment>
      ))}
      <Label x={444} y={620} a={diff * (1 - common)} size={24} color={C.bad} w={888}>하니스마다 저장 형식이 다르다</Label>
      <Box x={84} y={590} w={720} h={90} a={pick} ec={C.warn} fc={C.warnT} r={45} size={25} bold>
        어느 쪽으로 이어 갈지는 사용자가 고른다
      </Box>
    </Stage>
  );
};
