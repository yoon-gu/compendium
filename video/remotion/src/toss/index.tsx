import { CalculateMetadataFunction, Composition, Folder } from "remotion";
import { FPS, Timing, W } from "../lib/ui";
import { Bound } from "./Bound";
import { Case1 } from "./Case1";
import { Case2 } from "./Case2";
import { Case2Results } from "./Case2Results";
import { Closing } from "./Closing";
import { Costs } from "./Costs";
import { Explosion } from "./Explosion";
import { Group } from "./Group";
import { Mask } from "./Mask";
import { Online } from "./Online";
import { Ple } from "./Ple";
import { Seesaw } from "./Seesaw";
import { Share } from "./Share";
import { Shortcut } from "./Shortcut";
import { Takeaways } from "./Takeaways";
import { Topn } from "./Topn";
import { TwoUses } from "./TwoUses";

// 클립 길이는 화면 길이(props.duration 초)를 따른다. 렌더할 때 --props=<이름>-timing.json 으로 넘긴다.
const byDuration: CalculateMetadataFunction<Timing> = ({ props }) => ({
  durationInFrames: Math.ceil(props.duration * FPS),
});

// [이름, 컴포넌트, 높이(폭은 888), 표시 수]. 높이는 화면에서 제목 아래 남는 자리(약어 각주가 붙는 화면은 낮게).
const TOSS: [string, React.FC<Timing>, number, number][] = [
  ["explosion", Explosion, 720, 6],
  ["costs", Costs, 684, 5],
  ["ple", Ple, 720, 7],
  ["two-uses", TwoUses, 690, 6],
  ["mask", Mask, 720, 5],
  ["share", Share, 690, 6],
  ["case1", Case1, 700, 8],
  ["topn", Topn, 538, 6],
  ["online", Online, 690, 8],
  ["case2", Case2, 700, 11],
  ["shortcut", Shortcut, 720, 6],
  ["case2-results", Case2Results, 610, 5],
  ["seesaw", Seesaw, 610, 6],
  ["bound", Bound, 700, 7],
  ["group", Group, 690, 8],
  ["takeaways", Takeaways, 720, 4],
  ["closing", Closing, 560, 5],
];

export const TossFolder: React.FC = () => {
  return (
    <Folder name="toss-multi-task-learning-finance">
      {TOSS.map(([id, component, h, n]) => (
        <Composition
          key={id}
          id={`toss-${id}`}
          component={component}
          durationInFrames={40 * FPS}
          fps={FPS}
          width={W}
          height={h}
          defaultProps={{ duration: 40, marks: Array.from({ length: n }, (_, i) => 2 + i * 4) }}
          calculateMetadata={byDuration}
        />
      ))}
    </Folder>
  );
};
