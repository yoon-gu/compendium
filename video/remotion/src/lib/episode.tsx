// 회차 하나의 컴포지션들을 폴더로 등록한다. 클립 길이는 props.duration(초) — 렌더할 때 --props=<이름>-timing.json 으로 넘긴다.
import React from "react";
import { CalculateMetadataFunction, Composition, Folder } from "remotion";
import { FPS, Timing, W } from "./ui";

const byDuration: CalculateMetadataFunction<Timing> = ({ props }) => ({ durationInFrames: Math.ceil(props.duration * FPS) });

/** [이름, 컴포넌트, 높이(폭 888), 표시 수] 목록 → 컴포지션 id 는 `${prefix}-${이름}` */
export const Episode: React.FC<{ name: string; prefix: string; items: [string, React.FC<Timing>, number, number][] }> = ({ name, prefix, items }) => (
  <Folder name={name}>
    {items.map(([id, component, h, n]) => (
      <Composition key={id} id={`${prefix}-${id}`} component={component} durationInFrames={40 * FPS} fps={FPS} width={W} height={h}
        defaultProps={{ duration: 40, marks: Array.from({ length: n }, (_, i) => 2 + i * 4) }} calculateMetadata={byDuration} />
    ))}
  </Folder>
);
