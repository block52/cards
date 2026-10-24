"""Build the notched chip sets (ui#842) from the approved Option 2 SVGs.

Reads chip-design/svg-chips-v4b/*.svg (cash labels, $ and ¢) and writes two sets
with the label converted to vector outlines (no font needed at display time):
  <out>/cash/*.svg        - all 17, labels as approved
  <out>/tournament/*.svg  - the 12 dollar chips, same colours, plain point values
Font size follows the approved rule by label length; letter-spacing -0.6.
"""
import re, sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SRC, OUT, FONT = sys.argv[1], sys.argv[2], sys.argv[3]
font = TTFont(FONT)
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
upm = font["head"].unitsPerEm
SIZE_BY_LEN = {1: 44, 2: 37, 3: 31, 4: 24, 5: 18}
SPACING = -0.6

def label_path(label: str) -> str:
    fs = SIZE_BY_LEN[len(label)]
    scale = fs / upm
    names = [cmap[ord(ch)] for ch in label]
    advances = [glyphs[n].width * scale for n in names]
    total = sum(advances) + SPACING * len(label)  # browsers add spacing after every glyph
    x = 50 - total / 2
    baseline = 50 + 0.35 * fs
    pen = SVGPathPen(glyphs)
    for n, adv in zip(names, advances):
        # font units are y-up; flip into SVG's y-down space at the baseline
        glyphs[n].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        x += adv + SPACING
    return f'<path d="{pen.getCommands()}" fill="#fbf8f2"/>'

TEXT_RE = re.compile(r'<text[^>]*>([^<]*)</text>')
TOURNAMENT = ["1chip", "5chip", "25chip", "100chip", "500chip", "1000chip", "5000chip",
              "25000chip", "100000chip", "250000chip", "1000000chip", "5000000chip"]

os.makedirs(f"{OUT}/cash", exist_ok=True)
os.makedirs(f"{OUT}/tournament", exist_ok=True)
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".svg"):
        continue
    svg = open(f"{SRC}/{fn}").read()
    label = TEXT_RE.search(svg).group(1)
    name = fn[:-4]
    open(f"{OUT}/cash/{fn}", "w").write(TEXT_RE.sub(lambda m: label_path(label), svg))
    if name in TOURNAMENT:
        points = label.replace("$", "")
        open(f"{OUT}/tournament/{fn}", "w").write(TEXT_RE.sub(lambda m: label_path(points), svg))
        print(f"{name}: cash {label!r}  tournament {points!r}")
    else:
        print(f"{name}: cash {label!r}")
