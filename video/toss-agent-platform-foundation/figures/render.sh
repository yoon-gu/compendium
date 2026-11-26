#!/bin/sh
# Remotion 컴포지션 열네 편을 이 폴더의 mp4 로 굽는다. <이름>-timing.json(timing.py 가 씀)이 있으면 그 시각을 속성으로 넘긴다.
#   sh render.sh            # 전부
#   sh render.sh mask       # 하나만
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE/../../remotion"
for n in ${@:-need harness layers units vm fences sessions proxy perms resume state records takeaways limits}; do
  P=""; [ -f "$HERE/$n-timing.json" ] && P="--props=$HERE/$n-timing.json"
  npx remotion render "agent-$n" "$HERE/$n.mp4" $P --codec=h264 --muted --scale=2 --log=error
  echo "$n.mp4"
done
