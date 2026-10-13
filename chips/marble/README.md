# Marble chip set

Photoreal poker chips rendered in Blender (Cycles) from a single parametric model.

Each chip has:
- a polished stone body;
- a coin-milled gold edge (platinum on the $5M and the cent chips);
- recessed inlays;
- a black guilloché centre plate, carrying the **block52** wordmark in brand-gradient enamel set in gold, above a raised gold denomination.

The colour code matches the original flat chips (`../*.svg`), so players don't have to relearn it.

## Files

| Path | What | Used by |
|---|---|---|
| `{file}.webp` | Table sprite: 128 × 128, transparent, slight tilt so stacks read as piles (~8 KB each) | `block52/ui` `src/constants/chips.ts` |
| `dealer.webp` | The dealer button, same theme (white marble, gold veins, gold "D") | `block52/ui` `getDealerImageUrl()` |
| `showcase/{file}.webp` | 1400 × 980 three-quarter hero shot | large views and marketing |
| `source/` | The Blender scripts that produced everything here | re-rendering, new skins |

`{file}` uses the same base names as the SVG set: `1chip`, `5chip`, `25chip`, `100chip`, `500chip`, `1000chip`, `5000chip`, `25000chip`, `100000chip`, `250000chip`, `1000000chip`, `5000000chip`, `50cent`, `25cent`, `10cent`, `5cent`, `1cent`.

CDN: `https://cdn.jsdelivr.net/gh/block52/cards@main/chips/marble/5000chip.webp`

## The set

| Value | Colour | Stone / veining | Trim |
|---|---|---|---|
| $1 | white | white with black veining (Carrara), jet-black inlays | gold |
| $5 | red | red, pale veins | gold |
| $25 | green | green, pale veins | gold |
| $100 | black | Nero Marquina (black, white veins) | gold |
| $500 | purple | purple, pale veins | gold |
| $1K | yellow | Giallo Siena (brown-violet veins) | gold |
| $5K | orange | Breccia (oxblood and cream veins) | gold |
| $25K | blue | lapis (metallic gold veins) | gold |
| $100K | pink | Norwegian Rose (green and white veins) | gold |
| $250K | blue / orange | copper veins, orange inlays | gold |
| $1M | gold | Portoro-style antique gold (black and pale-gold veins), jet-black inlays | gold |
| $5M | platinum | Bardiglio silver (black and white streaks), jet-black inlays | platinum |
| 50¢, 25¢, 10¢, 5¢, 1¢ | purple, green, yellow, blue, red | as the matching dollar colour | platinum |

## Re-rendering

You need Blender 4.5 LTS. The scripts expect this layout next to `source/`, i.e. one level up from where the scripts run:

- `materials/Marble016/`, `materials/Marble021/`: ambientCG 2K-JPG scans (CC0): https://ambientcg.com/a/Marble016 and https://ambientcg.com/a/Marble021
- `materials/hdri/studio_small_09_2k.hdr`: Poly Haven (CC0): https://polyhaven.com/a/studio_small_09
- `b52-wordmark.svg`: the block52 wordmark

```
./source/render_set.sh table      # renders/set/table/*.png (512 px sprites)
./source/render_set.sh showcase   # renders/set/showcase/*.png
Blender -b --factory-startup --python source/export_webp.py -- renders/set/table chips/marble 128
```

`render_set.sh` holds the whole set as one table: stone, dye colour, vein colours, inlays and trim per chip. A new skin is a new table.

The dealer button is rendered with the same model, inlays off:

```
Blender -b --factory-startup --python source/hero.py -- --topdown --tilt 72 --thick 1.8 \
  --inlays 0 --value D --body Marble016 --tint "#f6f2ea" --vein "#c8a35a" \
  --samples 96 --res 512 --out dealer.png
```
