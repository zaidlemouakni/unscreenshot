# `spec.json` format

One file per slide. Every position and size is in **source-image pixels**, including font sizes (`size`) and line widths. Colours are hex `#RRGGBB`. Elements are listed in paint order: the first one is drawn underneath.

```json
{
  "source": "source.png",
  "size": [1920, 1080],
  "background": "#F7F8FB",
  "analysis": "work/analysis.json",
  "lang": "en-US",
  "title": "Operations Plan 2027",
  "elements": [ ... ]
}
```

- `source`: the original image (relative to the spec's folder). Used for cropped icons and for the check.
- `size`: image width and height in pixels. The slide is 13.333 in wide and keeps this ratio (16:9 snaps to 13.333 × 7.5 in).
- `analysis`: the file produced by analyze.py, used by `"from"`.
- `lang`: language of the slide's text (BCP-47: `fr-FR`, `ar-SA`, `ja-JP`, `zh-TW`…). It picks the default fonts for CJK, the direction of lines without letters, and PowerPoint's spell-checking. Runs in another script get their own tag automatically. `title`: document title.

## Keys shared by all elements

| Key | Purpose |
|---|---|
| `type` | `rect`, `ellipse`, `arrow`, `polygon`, `line`, `text`, `bullets`, `image` |
| `id` | unique name; becomes the shape name in PowerPoint |
| `from` | analysis reference(s) (`T#`, `R#`, `L#`, `G#`, `M#`) that fill missing values; a list = one line each; `"T4+T6+M1"` = pieces of one line |
| `group` | same value on consecutive elements = one PowerPoint group (e.g. a card) |
| `skip` | `true` to ignore the element without deleting it |

## Shapes

**`rect`**: `box`, `fill` (`null` = no fill), `radius` (px, or `"pill"` for round ends), `line` `{"color", "width", "dash"}`, `opacity` (0 to 1), `rotation` (degrees), `text` (centred label, see below).

**`ellipse`**: same keys as `rect`, without `radius`. A numbered circle is an ellipse with a `text`.

**`arrow`**: arrow bar (roadmap chevrons). `box` spans from the left edge to the tip. `tip` = tip depth. `notch: true` = notched left side (a chevron that nests into the previous one), otherwise a flat left side (pentagon). `flip: "h"` mirrors it (pointing left, for right-to-left slides).

**`polygon`**: `points` `[[x, y], ...]`, `fill`, `line`.

**`line`**: `p1` `[x, y]`, `p2` `[x, y]`, `color`, `width`, `dash` (`solid`, `dash`, `dot`, `sysdot`, `dashdot`, `longdash`), `head` (`none`, `end`, `start`, `both`).

**Label inside a shape** (`text` of a rect, ellipse or arrow): `{"content": "2025 – 2026", "font": "Arial", "size": 14, "bold": true, "color": "#0D3A40", "align": "center", "spacing": 0.3, "dy": 1, "pad": 0}`. Vertically centred; `dy` moves it down (px); `lines` replaces `content` for several lines.

## Texts

**`text`**
```json
{"type": "text", "id": "title", "from": ["T4", "T5"],
 "x": 97, "baseline": 159, "pitch": 64, "align": "left",
 "lines": ["Faster deliveries, lower cost per parcel:", "three moves for next year."],
 "font": "Century Gothic", "size": 57, "bold": true, "italic": false, "color": "#1B2340",
 "spacing": 0, "w": 1073, "role": "title",
 "fit": {"mode": "size", "text": "Faster deliveries, lower cost per parcel:", "w": 1073}}
```
- `x`: left edge of the ink (`align: left`), its centre (`center`) or its right edge (`right`). `align` is what you see; it defaults to `right` for right-to-left text.
- `baseline`: baseline of the **first** line. `pitch`: distance between two baselines.
- `lines`: one entry per line of the image. A line can mix styles: `[{"text": "NORTHWIND  |  ", "color": "#6B7392"}, {"text": "OPERATIONS PLAN 2027", "color": "#F26B3A"}]`. Each run can change `font`, `font_ea`, `font_cs`, `lang`, `size`, `bold`, `italic`, `color`, `underline`.
- `lang` (element or run), `dir` (`"rtl"` / `"ltr"`, detected from the letters), `font_ea` (font of CJK characters), `font_cs` (font of Arabic, Hebrew, Thai, Indic characters): see *Languages and scripts* in SKILL.md.
- `w`: measured ink width (used by fit). `width` (optional): text box width, if needed.
- `fit`: `mode` `"size"` (size from width, default) or `"spacing"` (size from cap height `cap`, letter-spacing from width); `text` and `w` pick the reference line (default: the longest). `fixed: true` on the element = do not adjust anything.
- `size`, `spacing`, `lsb`, `rsb` (side bearings) are filled by fit.py; you may force them. `fitted.method` tells how the size was found (`width`, `headline`, `body height`, `cap`).

**`bullets`**
```json
{"type": "bullets", "id": "risks", "from": ["T11", "T15", "T19", "T20"],
 "x": 1380, "text_x": 1410, "baseline": 449, "pitch": 47, "gap": 0,
 "items": ["Sorter supplier lead times slip past Q2",
           ["A bullet whose text wraps", "keeps its continuation aligned"]],
 "font": "Segoe UI", "size": 22, "color": "#D7DBEA",
 "bullet": "●", "bullet_color": "#F26B3A", "bullet_size": 125, "role": "bullet"}
```
- `x`: outer edge of the bullet dot (left; right in right-to-left text); `text_x`: where the text starts (its left edge; its right edge in right-to-left text); `baseline`: first line; `pitch`: baseline to baseline; `gap`: extra space between two bullets.
- An item given as a list = one bullet on several lines (soft line breaks aligned on the text).
- With `from`, list the `T#` in line order: fit.py measures each line.

## Images

**`image`**: `box` (position on the slide), `crop` (area of the source image, default = `box`), `transparent` (`"auto"` = make the border colour transparent, or `"#RRGGBB"`), `upscale` (enlargement, default 3), `file` (an external file instead of a crop), `pad` (margin added around a `G#`), `alt` (alternative text).

## Complete example

`example-spec.json` rebuilds the demo slide of the repository (`examples/demo/source.png`): eyebrow with two colours, two-line title, KPI cards, a dark panel with round bullets, a chevron roadmap and a footer. Built and checked, every text lands within 1 px of the source. The repository's `examples/` folder also has a right-to-left Arabic slide, a Japanese slide and a sampler of twelve scripts.
