#!/bin/zsh
# Renders the full Block52 marble chip set, matching the denominations and colour code in
# ui/src/constants/chips.ts. Output names mirror the UI's chip files (5000chip.svg -> 5000chip.png).
#   ./source/render_set.sh table     -> renders/set/table/*.png    (top-down sprites, transparent)
#   ./source/render_set.sh showcase  -> renders/set/showcase/*.png (3/4 hero shots)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE/.."
MODE=${1:-table}
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
OUT=renders/set/$MODE
mkdir -p $OUT

# file | label | body scan | body dye | inlay scan | inlay dye | metal | extra args
CHIPS=(
  "1chip|1|Marble016|#f2efe8|Marble016||gold|--vein #141414 --insert-solid #0b0b0c"
  "5chip|5|Marble016|#c1121f|Marble021||gold"
  "25chip|25|Marble016|#0f7a3d|Marble021||gold"
  "100chip|100|Marble016||Marble021||gold"
  "500chip|500|Marble016|#7e22ce|Marble021||gold"
  "1000chip|1K|Marble016|#ffd21a|Marble021||gold|--vein #3b2233"
  "5000chip|5K|Marble016|#ef6a12|Marble021||gold|--vein #2a0703 --vein2 #ffe2c2"
  "25000chip|25K|Marble016|#1e40af|Marble021||gold|--vein #e0b04a --vein-metal"
  "100000chip|100K|Marble016|#ec5c9c|Marble021||gold|--vein #1f3a2e --vein2 #ffffff"
  "250000chip|250K|Marble016|#1d4ed8|Marble016|#e8590c|gold|--vein #e07a2c"
  "1000000chip|1M|Marble016|#b07d14|Marble016||gold|--insert-solid #0b0b0c --vein #0d0b08 --vein2 #ffe7a0"
  "5000000chip|5M|Marble016|#b4bac2|Marble016||platinum|--vein #15171a --vein2 #f4f5f6 --insert-solid #0b0b0c"
  "50cent|50¢|Marble016|#7e22ce|Marble021||platinum"
  "25cent|25¢|Marble016|#0f7a3d|Marble021||platinum"
  "10cent|10¢|Marble016|#f5c400|Marble016||platinum|--insert-solid #0b0b0c"
  "5cent|5¢|Marble016|#1d4ed8|Marble021||platinum"
  "1cent|1¢|Marble016|#c1121f|Marble021||platinum"
)

# Optional filter: ./render_set.sh table 1chip 1000chip  (renders only those)
ONLY=(${@:2})
for row in $CHIPS; do
  [[ ${#ONLY} -gt 0 && -z ${ONLY[(r)${row%%|*}]} ]] && continue
  IFS="|" read -r file label body tint insert itint metal extra <<< "$row"
  args=(--value "$label" --body $body --insert $insert --metal $metal --out $OUT/$file.png)
  [[ -n $tint ]] && args+=(--tint "$tint")
  [[ -n $itint ]] && args+=(--insert-tint "$itint")
  [[ -n $extra ]] && args+=(${=extra})
  if [[ $MODE == table ]]; then
    args+=(--topdown --tilt 72 --thick 2.0 --res 512 --samples 96)
  else
    args+=(--res 1400 --samples 128)
  fi
  $BLENDER -b --factory-startup --python "$HERE/hero.py" -- $args 2>&1 | grep -E "Error|Traceback|WROTE"
done
echo SET_DONE $MODE
