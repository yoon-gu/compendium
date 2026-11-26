import React from "react";
import { Timing } from "../lib/ui";
import { Episode } from "../lib/episode";
import { Aitm } from "./Aitm";
import { Autok } from "./Autok";
import { Closing } from "./Closing";
import { Direction } from "./Direction";
import { Elbow } from "./Elbow";
import { Fixes } from "./Fixes";
import { Funnel } from "./Funnel";
import { Ktable } from "./Ktable";
import { Leak } from "./Leak";
import { Lessons } from "./Lessons";
import { Missing } from "./Missing";
import { Pinned } from "./Pinned";
import { Questions } from "./Questions";
import { Ranking } from "./Ranking";
import { Report } from "./Report";
import { TreeVsDl } from "./TreeVsDl";

// [이름, 컴포넌트, 높이(폭 888), 표시 수]. 약어 각주가 한 줄 붙는 화면은 610, 끝 화면(아래 '원문' 줄)은 560.
const ITEMS: [string, React.FC<Timing>, number, number][] = [
  ["questions", Questions, 720, 8],
  ["ranking", Ranking, 610, 7],
  ["elbow", Elbow, 720, 7],
  ["ktable", Ktable, 610, 6],
  ["autok", Autok, 720, 7],
  ["funnel", Funnel, 720, 8],
  ["aitm", Aitm, 610, 8],
  ["treevsdl", TreeVsDl, 720, 8],
  ["report", Report, 610, 9],
  ["direction", Direction, 720, 9],
  ["pinned", Pinned, 720, 8],
  ["missing", Missing, 720, 9],
  ["leak", Leak, 610, 8],
  ["fixes", Fixes, 720, 4],
  ["lessons", Lessons, 720, 8],
  ["closing", Closing, 560, 7],
];

export const TargetingFolder: React.FC = () => <Episode name="toss-targeting-model-automation" prefix="targeting" items={ITEMS} />;
