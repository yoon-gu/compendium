import { CalculateMetadataFunction, Composition, Folder } from "remotion";
import { FPS, H, Timing, W } from "./lib/ui";
import { Explosion } from "./toss/Explosion";
import { Mask } from "./toss/Mask";
import { Ple } from "./toss/Ple";
import { Shortcut } from "./toss/Shortcut";

// 클립 길이는 화면 길이(props.duration 초)를 따른다. 렌더할 때 --props=<이름>-timing.json 으로 넘긴다.
const byDuration: CalculateMetadataFunction<Timing> = ({ props }) => ({
  durationInFrames: Math.ceil(props.duration * FPS),
});

export const RemotionRoot: React.FC = () => {
  return (
    <Folder name="toss-multi-task-learning-finance">
      <Composition
        id="toss-explosion"
        component={Explosion}
        durationInFrames={40 * FPS}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{ duration: 40, marks: [5, 11, 15, 19, 23, 29] }}
        calculateMetadata={byDuration}
      />
      <Composition
        id="toss-ple"
        component={Ple}
        durationInFrames={50 * FPS}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{ duration: 50, marks: [3, 9, 14, 20, 27, 34, 41] }}
        calculateMetadata={byDuration}
      />
      <Composition
        id="toss-mask"
        component={Mask}
        durationInFrames={50 * FPS}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{ duration: 50, marks: [6, 14, 24, 32, 40] }}
        calculateMetadata={byDuration}
      />
      <Composition
        id="toss-shortcut"
        component={Shortcut}
        durationInFrames={50 * FPS}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{ duration: 50, marks: [6, 10, 15, 22, 30, 40] }}
        calculateMetadata={byDuration}
      />
    </Folder>
  );
};
