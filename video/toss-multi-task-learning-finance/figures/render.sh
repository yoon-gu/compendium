#!/bin/sh
# Remotion 컴포지션 열일곱 편을 이 폴더의 mp4 로 굽는다. <이름>-timing.json(timing.py 가 씀)이 있으면 그 시각을 속성으로 넘긴다.
#   sh render.sh            # 전부
#   sh render.sh mask       # 하나만
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE/../../remotion"
for n in ${@:-explosion costs ple two-uses mask share case1 topn online case2 shortcut case2-results seesaw bound group takeaways closing}; do
  P=""; [ -f "$HERE/$n-timing.json" ] && P="--props=$HERE/$n-timing.json"
  npx remotion render "toss-$n" "$HERE/$n.mp4" $P --codec=h264 --muted --scale=2 --log=error
  echo "$n.mp4"
done
