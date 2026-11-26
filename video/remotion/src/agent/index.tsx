import React from "react";
import { Timing } from "../lib/ui";
import { Episode } from "../lib/episode";

// [이름, 컴포넌트, 높이, 표시 수]
const ITEMS: [string, React.FC<Timing>, number, number][] = [];

export const AgentFolder: React.FC = () => <Episode name="toss-agent-platform-foundation" prefix="agent" items={ITEMS} />;
