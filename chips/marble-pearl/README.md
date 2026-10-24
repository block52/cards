# Marble chips: pearl face

The photoreal marble chips (see `../marble/`), re-rendered for legibility at table size (block52/ui#842):

- a **bigger black centre face** with a thinner rim (plate radius 0.72);
- the value in **pearl white** (#fbf8f2, Arial Black), with no wordmark, so it fills the face.

Marble bodies, inlays, metals and the colour code are unchanged from `../marble/`. This is the **default** chip style in the UI; players can switch to the flat `../notched/` set in Settings ("Marble Chips").

## Two sets

| Folder | Values | Used for |
|---|---|---|
| `cash/` | 1¢, 5¢, 10¢, 25¢, 50¢, $1, $5, $25, $100, $500, $1K, $5K, $25K, $100K, $250K, $1M, $5M | cash games (real USDC) |
| `tournament/` | 1, 5, 25, 100, 500, 1K, 5K, 25K, 100K, 250K, 1M, 5M | Sit & Go and tournaments (points, no currency) |

Files are 256 × 256 transparent WebP table sprites with the same names as the other sets (`25chip.webp`, `50cent.webp`, …). The tournament folder has only the twelve whole-number chips.

CDN: `https://cdn.jsdelivr.net/gh/block52/cards@main/chips/marble-pearl/cash/25chip.webp`

## Rebuilding

`source/` holds the Blender scripts that produced these. `hero.py` is the model, with the `--value-color`, `--value-glow`, `--no-wordmark` and `--plate-r` options this look uses. `render_cash.sh` and `render_tournament.sh` render the 512 px PNGs, and `export_webp.py` downsizes them to 256 px WebP:

```bash
./render_cash.sh table && ./render_tournament.sh table
Blender -b --factory-startup --python export_webp.py -- <png_dir> <out_dir> 256
```

The render scripts expect to be run from the chip-design workspace (`blender/hero.py`, `renders/clarity/…`); adjust the paths at the top if you run them from here.
