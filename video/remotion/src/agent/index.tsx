import React from "react";
import { Timing } from "../lib/ui";
import { Episode } from "../lib/episode";
import { Fences } from "./Fences";
import { Harness } from "./Harness";
import { Layers } from "./Layers";
import { Limits } from "./Limits";
import { Need } from "./Need";
import { Perms } from "./Perms";
import { Proxy } from "./Proxy";
import { Records } from "./Records";
import { Resume } from "./Resume";
import { Sessions } from "./Sessions";
import { State } from "./State";
import { Takeaways } from "./Takeaways";
import { Units } from "./Units";
import { Vm } from "./Vm";

// [이름, 컴포넌트, 높이(폭 888), 표시 수]. 약어 각주가 붙는 화면(vm·proxy·perms·resume)은 낮게, 아래에 보조 줄이 있는 limits 는 더 낮게.
const ITEMS: [string, React.FC<Timing>, number, number][] = [
  ["need", Need, 700, 7],
  ["harness", Harness, 690, 6],
  ["layers", Layers, 700, 6],
  ["units", Units, 700, 8],
  ["vm", Vm, 600, 6],
  ["fences", Fences, 700, 10],
  ["sessions", Sessions, 690, 9],
  ["proxy", Proxy, 600, 9],
  ["perms", Perms, 580, 7],
  ["resume", Resume, 610, 8],
  ["state", State, 690, 7],
  ["records", Records, 690, 9],
  ["takeaways", Takeaways, 700, 3],
  ["limits", Limits, 540, 5],
];

export const AgentFolder: React.FC = () => <Episode name="toss-agent-platform-foundation" prefix="agent" items={ITEMS} />;
