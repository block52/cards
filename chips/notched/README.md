# Notched chip set

Flat vector poker chips (block52/ui#842): a coloured disc with eight edge notches running to the rim, a black centre plate with a thin gold ring, and a large pearl-white value. Dark notches ($1, 10¢, $1K, $1M, $5M) carry a thin light outline so they stand out from the felt.

They're built for legibility at table size (~28 px). The labels are **vector outlines**, not text, so they look the same on every device with no font needed.

The colour code matches the earlier sets, so players don't have to relearn it.

## Two sets

| Folder | What | Values | Used for |
|---|---|---|---|
| `cash/` | Real USDC | 1¢, 5¢, 10¢, 25¢, 50¢, $1, $5, $25, $100, $500, $1K, $5K, $25K, $100K, $250K, $1M, $5M | cash games |
| `tournament/` | Points, no currency | 1, 5, 25, 100, 500, 1K, 5K, 25K, 100K, 250K, 1M, 5M | Sit & Go and tournaments |

Tournament chips reuse the dollar chips' colours (for example, green = 25 in both). They have no cent chips, and 1/5/25/100/… make exact change for any whole-number bet.

File names match the other sets: `1chip`, `5chip`, `25chip`, `100chip`, `500chip`, `1000chip`, `5000chip`, `25000chip`, `100000chip`, `250000chip`, `1000000chip`, `5000000chip`, `50cent`, `25cent`, `10cent`, `5cent`, `1cent` (`.svg`, 100 × 100 viewBox). The `tournament/` folder has only the twelve `*chip` files.

CDN: `https://cdn.jsdelivr.net/gh/block52/cards@main/chips/notched/cash/25chip.svg`

## Rebuilding

`source/labelled/` holds the approved designs with the value as live text. `source/outline_chips.py` (needs `fonttools`) turns the text into outlines and writes both sets:

```bash
python3 source/outline_chips.py source/labelled . "/System/Library/Fonts/Supplemental/Arial Black.ttf"
```

Run it from `chips/notched/`. The font size depends on label length (1 char 44, 2 → 37, 3 → 31, 4 → 24, 5 → 18), with letter-spacing −0.6.
