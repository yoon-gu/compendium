// 듣는편람 모션 그래픽 공용 부품: 숲 톤 팔레트, 나눔고딕, 언급 시각(marks) 기준 등장.
import { loadFont } from "@remotion/fonts";
import React from "react";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

export const C = {
  paper: "#F4F4F1", ink: "#3F7A66", inkT: "#E3EEEA", txt: "#141414", gray: "#6B6B68", line: "#B9B9B4", soft: "#E4E4DF",
  ok: "#4E8F76", okT: "#EAF3EE", warn: "#C9963A", warnT: "#F8F0E0", bad: "#C0605A", badT: "#F6E7E5",
};

for (const [w, f] of [["400", "Regular"], ["700", "Bold"], ["800", "ExtraBold"]] as const) {
  loadFont({ family: "NanumGothic", url: staticFile(`fonts/NanumGothic-${f}.ttf`), weight: w });
}

// 클립 길이 = 그 화면의 길이(초), marks = 나레이션에서 각 요소가 언급되는 시각(초). timing.py 가 채운다.
export type Timing = { duration: number; marks: number[] };
export const FPS = 25;
export const W = 888;   // 세로 영상 본문 폭 그대로(화면 px). 렌더는 --scale=2 로 선명하게
export const H = 720;

const ease = Easing.bezier(0.16, 1, 0.3, 1);

/** marks[i] 시각부터 0.6초 동안 0→1. i 가 없으면 늘 1(정지 화면 미리보기용). */
export const useAt = (marks: number[], i: number, len = 0.6) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = marks[i];
  if (t === undefined) return 1;
  return interpolate(frame, [t * fps, (t + len) * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
};

export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ backgroundColor: C.paper, fontFamily: "NanumGothic", color: C.txt }}>{children}</AbsoluteFill>
);

type BoxProps = {
  x: number; y: number; w: number; h: number; a?: number; ec?: string; fc?: string; lw?: number; r?: number;
  children?: React.ReactNode; size?: number; color?: string; bold?: boolean; rise?: boolean;
};

/** 둥근 상자 + 가운데 글. a 로 나타나고(투명도), rise 면 아래에서 살짝 올라온다. */
export const Box: React.FC<BoxProps> = ({ x, y, w, h, a = 1, ec = C.line, fc = "#FFFFFF", lw = 3, r = 18, children, size = 34, color = C.txt, bold = false, rise = true }) => (
  <div
    style={{
      position: "absolute", left: x, top: y, width: w, height: h, boxSizing: "border-box",
      border: `${lw}px solid ${ec}`, background: fc, borderRadius: r, opacity: a,
      translate: rise ? `0px ${(1 - a) * 24}px` : undefined,
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      fontSize: size, fontWeight: bold ? 800 : 400, color, textAlign: "center", lineHeight: 1.25,
    }}
  >
    {children}
  </div>
);

/** 상자 없는 글. align 은 x 기준 정렬. */
export const Label: React.FC<{ x: number; y: number; a?: number; size?: number; color?: string; bold?: boolean; align?: "left" | "center" | "right"; children: React.ReactNode; w?: number }> = ({ x, y, a = 1, size = 36, color = C.txt, bold = false, align = "center", children, w = 1400 }) => (
  <div
    style={{
      position: "absolute", top: y, width: w, left: align === "center" ? x - w / 2 : align === "right" ? x - w : x,
      textAlign: align, fontSize: size, fontWeight: bold ? 800 : 400, color, opacity: a, lineHeight: 1.25,
      translate: `0px ${(1 - a) * 16}px`, transform: "translateY(-50%)",
    }}
  >
    {children}
  </div>
);

/** SVG 화살표(직선). 전체 캔버스 좌표. */
export const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; a?: number; color?: string; lw?: number; dash?: boolean }> = ({ x1, y1, x2, y2, a = 1, color = C.ink, lw = 5, dash = false }) => {
  const ang = Math.atan2(y2 - y1, x2 - x1);
  const hx = x2 - 18 * Math.cos(ang), hy = y2 - 18 * Math.sin(ang);
  const p = (s: number) => `${hx + 11 * Math.cos(ang + s)},${hy + 11 * Math.sin(ang + s)}`;
  return (
    <svg style={{ position: "absolute", left: 0, top: 0, opacity: a }} width={W} height={H}>
      <line x1={x1} y1={y1} x2={hx} y2={hy} stroke={color} strokeWidth={lw} strokeDasharray={dash ? "12 10" : undefined} strokeLinecap="round" />
      <polygon points={`${x2},${y2} ${p(Math.PI / 2)} ${p(-Math.PI / 2)}`} fill={color} />
    </svg>
  );
};

/** 작은 트리 모델 아이콘(삼각형 세 단 + 줄기). */
export const Tree: React.FC<{ x: number; y: number; s?: number; a?: number; color?: string }> = ({ x, y, s = 1, a = 1, color = C.ink }) => (
  <svg style={{ position: "absolute", left: x - 30 * s, top: y - 36 * s, opacity: a }} width={60 * s} height={72 * s} viewBox="0 0 60 72">
    <polygon points="30,2 50,26 10,26" fill={color} />
    <polygon points="30,16 56,46 4,46" fill={color} />
    <rect x="26" y="46" width="8" height="20" fill={color} />
  </svg>
);
