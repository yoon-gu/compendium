// 회차마다 src/<회차>/index.tsx 에 컴포지션 목록을 두고 여기서 모은다(회차끼리 이 파일을 함께 고치지 않게).
import React from "react";
import { AgentFolder } from "./agent";
import { TargetingFolder } from "./targeting";
import { TossFolder } from "./toss";

export const RemotionRoot: React.FC = () => (
  <>
    <TossFolder />
    <AgentFolder />
    <TargetingFolder />
  </>
);
