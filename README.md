# Block52 Playing Cards

Open source SVG playing card graphics for poker applications.

## CDN Usage

Use the GitHub raw content CDN to access card images:

```
https://raw.githubusercontent.com/block52/cards/main/{CARD_CODE}.svg
```

### Card Naming Convention

Cards follow the format: `{Rank}{Suit}.svg`

**Ranks:** 2, 3, 4, 5, 6, 7, 8, 9, T (Ten), J, Q, K, A

**Suits:** C (Clubs), D (Diamonds), H (Hearts), S (Spades)

### Examples

```
AS.svg  - Ace of Spades
KH.svg  - King of Hearts
TC.svg  - Ten of Clubs
2D.svg  - Two of Diamonds
```

### Card Backs

- `b52CardBack.svg` - Block52 branded card back (default)
- `Back.svg` - Simple card back
- `BackCustom.svg` - Custom/Texas HODL branded back

### Additional Assets

- `chip.svg` - Poker chip
- `dealer.svg` - Dealer button
- `chiplg.svg`, `chipmd.svg`, `chipsm.svg` - Chip size variants

## Usage Example

```javascript
const CDN_BASE = "https://raw.githubusercontent.com/block52/cards/main";

function getCardUrl(cardCode) {
    return `${CDN_BASE}/${cardCode}.svg`;
}

// Get Ace of Spades
const aceOfSpades = getCardUrl("AS");
// => https://raw.githubusercontent.com/block52/cards/main/AS.svg
```

## All Cards

The repository contains all 52 playing cards:

| Suit | Cards |
|------|-------|
| Clubs (C) | 2C, 3C, 4C, 5C, 6C, 7C, 8C, 9C, TC, JC, QC, KC, AC |
| Diamonds (D) | 2D, 3D, 4D, 5D, 6D, 7D, 8D, 9D, TD, JD, QD, KD, AD |
| Hearts (H) | 2H, 3H, 4H, 5H, 6H, 7H, 8H, 9H, TH, JH, QH, KH, AH |
| Spades (S) | 2S, 3S, 4S, 5S, 6S, 7S, 8S, 9S, TS, JS, QS, KS, AS |

## License

MIT License

Copyright (c) 2025 Block52

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
