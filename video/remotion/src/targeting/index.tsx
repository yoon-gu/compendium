import React from "react";
import { Timing } from "../lib/ui";
import { Episode } from "../lib/episode";

// [이름, 컴포넌트, 높이, 표시 수]
const ITEMS: [string, React.FC<Timing>, number, number][] = [];

export const TargetingFolder: React.FC = () => <Episode name="toss-targeting-model-automation" prefix="targeting" items={ITEMS} />;
