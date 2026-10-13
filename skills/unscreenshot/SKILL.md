---
name: unscreenshot
description: Rebuild a slide from an image (screenshot, PNG/JPG/WebP, PDF page) as an editable PowerPoint (.pptx) that matches it pixel for pixel - positions, sizes, colours, fonts and every word, in any language or script. Use when someone shares a picture of a slide and wants it recreated, made editable, converted to PowerPoint, or "the PPTX back".
license: MIT
metadata:
  version: 1.0.0
---

# unscreenshot: screenshot in, editable PowerPoint out

The deliverable is a .pptx where every element is **measured** on the image, never guessed by eye. Everything is native and editable (text boxes, real bullets, shapes, lines). Only icons, logos, photos and illustrations are taken from the image.

- All coordinates are **source-image pixels** (the pixels of `work/source.png`); boxes are `[x0, y0, x1, y1]`.
- `$SKILL` = the folder of this file (scripts in `$SKILL/scripts`). Work in a writable folder, e.g. `/tmp/rs`, with `work/` (measurements) and `out/` (results).
- Needs Python 3 with Pillow and numpy only. LibreOffice (or PowerPoint on Windows) is used for the visual check when present.
- Talk to the user in **their** language. The slide's text stays in its own language and script (see *Languages and scripts*).

## Steps (always in this order)

**0. Environment.** `python $SKILL/scripts/env_check.py`
Note the "metric-exact" fonts (sizes and spacing come out exact), the fonts found for each script, and whether a renderer exists. If Pillow or numpy is missing, try `pip install pillow numpy`; if that fails, tell the user.

**1. Input.** `python $SKILL/scripts/prepare.py <attached file> --out work` → `work/source.png`.
A PDF gives one image per page: one slide per page, in order. Several images: process each in its own folder (`work_1/`, `work_2/`…) and build them into one .pptx at step 8.

**2. Analysis.** `python $SKILL/scripts/analyze.py work/source.png --out work`
- `work/analysis.json`: background, palette (measured hex), filled regions `R#` (cards, bars, pills, circles, bands; `container` = a frame holding other elements), rules `L#`, graphics `G#` (icons, logos), marks `M#` (bullet dots), text lines `T#` (ink box, `cap_top`, `x_top`, `baseline`, `core`, `headline`, colour, `light` = light text on a dark fill). Dots and accents drawn apart from their letters (Arabic, Persian, Thai, Vietnamese, Hindi) are already part of their line.
- **Look at** `work/annotated.png` (ids drawn on the slide) and `work/lines_*.png` (every text line enlarged with its id).
- The analysis is a strong base, not the truth: regions can be merged or split, and a line can come in pieces (around CJK punctuation such as 、：（ or wide Arabic digits). Join the pieces of one line with `+`: `"from": "T4+T6+T5+M1"`. Step 4 measurements win.

**3. Exact reading.** Transcribe every text character for character from `lines_*.png`: case, accents, typographic quotes (’ “ ”), dashes (– —), arrows (→ ↔), symbols. Keep each text in its own script and its digits as shown (١٢٪, ۱۲٪ and 12% are different texts); write right-to-left text in reading order, as it would be typed, not as it is displayed. For small details: `python $SKILL/scripts/crop.py work/source.png x0 y0 x1 y1 --zoom 4` (enlarged crop with a coordinate grid).

**4. Precise measurements.** For anything that matters: card and bar edges, chevron tips, radii, rules, colours.
- `python $SKILL/scripts/probe.py work/source.png h <y> [x0 x1]` → colour runs along a row (exact edges, to the pixel)
- `... v <x> [y0 y1]` (a column) · `color <x> <y>` · `box <x> <y>` (extent of a flat area) · `ink x0 y0 x1 y1` (text: ink box, baseline, colour)
- Rule: **no coordinate by eye when it can be measured.** Probe along lines that do not cross text.

**5. Fonts.** Use the image's font if it is an Office font; otherwise the closest Office font per role:
- geometric sans (round o, wide headings, like Poppins, Montserrat, Figtree) → **Century Gothic**; neutral (Helvetica, Inter) → **Arial**; humanist UI (Open Sans, Source Sans, Lato) → **Segoe UI** (or **Segoe UI Semibold** for semibold); narrow body text → **Calibri**; serif → **Georgia**, **Cambria** or **Times New Roman**; monospace → **Courier New**.
- At equal resemblance, prefer a font listed as metric-exact by env_check: its size is computed exactly.
- Other scripts: see the table in *Languages and scripts*. Vietnamese needs a font with its letters (Arial, Segoe UI, Calibri; not Century Gothic).
- One font per role, two or three families per slide at most.

**6. Spec.** Write `work/spec.json` following `reference/spec-format.md` (complete example: `reference/example-spec.json`).
- Elements in **paint order**: background → frames and cards → inner panels → bars, pills, shapes → rules → icons → texts.
- Anchor geometry on the analysis with `"from": "T12"` (or `["T12", "T13"]` for a multi-line block), `"from": "R4"`, `"from": "L2"`, `"from": "G7"`. The script fills x, baseline, width, cap height, line pitch, boxes and colours, without overwriting what you wrote.
- `"role"` on texts of the same kind (`"bullet"`, `"kpi"`, `"card-title"`…): fit.py gives them one size (median), and check.py keeps it.
- Letter-spaced capitals (eyebrows, labels): `"fit": {"mode": "spacing"}` → size from the cap height, letter-spacing from the width. Never for Arabic or Devanagari: letter-spacing breaks their joins.
- `"lang"` on the spec (the slide's language, BCP-47 such as `ar-SA`, `ja-JP`) and on elements in another language. `"dir": "rtl"` is detected from the letters: give it only for a line without letters in a mixed slide.

**7. Fit.** `python $SKILL/scripts/fit.py work/spec.json` → `work/spec.fitted.json`
Computes each text's size (and letter-spacing) so its ink width equals the source, with the font PowerPoint will use for that script. The method column says how: `width` (exact), `headline` / `body height` (Indic scripts measured without a shaping engine), `cap` (estimated). `APPROX` = the font is not available here: verify at step 9.

**8. Build.** `python $SKILL/scripts/build_pptx.py work/spec.fitted.json [work_2/spec.fitted.json …] --out out/<name>.pptx`
One slide per spec. 16:9 slides snap to the standard 13.333 × 7.5 in size.

**9. Check.** `python $SKILL/scripts/check.py out/<name>.pptx work/spec.fitted.json --out out/check`
(several slides: add `--slide N` for the N-th spec, e.g. `check.py out/<name>.pptx work_2/spec.fitted.json --slide 2 --out out/check_2`)
- **Look at** `out/check/side_by_side.png` (source above, rebuild below) and `out/check/overlay.png` (black = identical, cyan = only in the source, red = only in the rebuild).
- `report.txt` gives dx, dy (baseline) and width ratio per text; `spec.corrected.json` holds the useful fixes. Rebuild from it and check again, **three rounds at most**.
- Fix by hand in the spec what the script cannot see: a missing element, a wrong colour, an overflowing text, a misplaced shape (measure it with probe.py).
- With LibreOffice, a 1–3 px vertical gap can come from the renderer, not the slide: do not chase it. Without any renderer, at least compare the image and your spec visually.

**10. Deliver.** Save the .pptx where your platform hands files to the user (claude.ai: `/mnt/user-data/outputs/`; ChatGPT: `/mnt/data/`; others: the platform's created-files mechanism). Attach `side_by_side.png` when possible. Summary of three lines at most: fonts used (and substituted), elements kept as images, remaining differences. Do not describe the method.

## Languages and scripts

Every script works: Latin (incl. Vietnamese), Cyrillic, Greek, Arabic, Persian, Urdu, Hebrew, Chinese, Japanese, Korean, Hindi and the other Indic scripts, Thai. The scripts handle the details; you write the text, the fonts and `lang`.

| Script | Office font (default) | Notes |
|---|---|---|
| Arabic, Persian, Urdu | Segoe UI (also Dubai, Arial, Tahoma) | right to left; never letter-spaced |
| Hebrew | Segoe UI, Arial | right to left |
| Chinese | Microsoft YaHei (simplified), Microsoft JhengHei (traditional) | `lang` `zh-CN` / `zh-TW` decides |
| Japanese | Yu Gothic (Yu Mincho for serif) | kana means Japanese |
| Korean | Malgun Gothic | |
| Hindi, Marathi, Nepali, Bengali, Tamil… | Nirmala UI | never letter-spaced |
| Thai, Lao | Leelawadee UI | |

- **Mixed text**: `font` is the Latin font; PowerPoint draws CJK with `font_ea` and Arabic, Hebrew, Thai and Indic with `font_cs`. Both default to the table above (or to `font` when it can draw the script, like Segoe UI for Arabic). Set them only to match a different look.
- **Right to left**: `align` is what you see (an Arabic title is `"right"`), `x` is that edge. Bullets sit on the right: `x` = right edge of the bullet dot, `text_x` = right edge of the text. A mirrored roadmap: `"flip": "h"` on the arrows.
- **Numbers inside right-to-left text** follow the image: Arabic-Indic digits (٠-٩) as shown. With Persian digits (۰-۹) before a percent sign, browsers draw ٪ on the left and PowerPoint (fa/ar run) on the right: if the image has it on the left, put the number in its own run with `"lang": "en-US"`.
- **Vertical CJK text** (top to bottom): keep it as an `image`.

## Fidelity rules

- **Verbatim text**: do not correct, translate or rephrase anything, not even a typo; mention it in the summary. Keep the image's line breaks (`lines`, and for a bullet on two lines, an item given as a list).
- **Everything editable**: texts in text boxes, lists as real bullets (`bullets`), frames, bars, arrows, pills and lines as native shapes. An `image` element only for icons, logos, photos, illustrations, complex charts.
- **Measured colours** (palette, probe), never guessed. Light text on dark fills keeps its measured colour.
- **Nothing invented, nothing left out**: every visible element of the image is in the spec, and nothing else.

## Known pitfalls (handled by the scripts if the spec follows these rules)

- PowerPoint puts the first baseline 0.75 × the line spacing below the top of a text box when the spacing is at least 1.25 × the font size (measured for Latin, CJK, Indic, Thai, Arabic and Hebrew Office fonts; Dubai 0.725). The builder relies on this: a block with tighter lines (often a two-line title) is split into one text box per line, grouped. Always give `baseline` (measured) and `pitch` (baseline to baseline), never a "box top". For CJK and Indic text fit.py moves the analysis baseline to the real one.
- Bullets: `x` = left edge of the bullet dot (mark `M#`), `text_x` = start of the text. A bullet whose text wraps is written `["first line", "continuation"]`: the continuation stays aligned with the text.
- Round bullets larger than a "•": use `"bullet": "●"` with `bullet_size` around 100–130. Scaling a small "•" above 100 % pushes it up off the text line.
- Same-size texts in the source (three KPI figures, all card titles) share a `role`: one size for all, positions corrected individually.
- Chevron bars: `"type": "arrow"` (pointed, flat left) or `"notch": true` (notched left); `tip` = measured tip depth. Probe the row at mid-height: the run of each colour ends exactly at the tip.
- Icons: a native shape for the tile behind (rounded rect), then the icon as an `image` cropped from the source with `"transparent": "auto"` and `"upscale": 4`.
- A white card on a near-white page: probe its colour (`probe.py color`), the palette may merge the two whites.
- Low-resolution images (< 1200 px wide) give ±1 px measurements: aim at line centres and one size per role.
- A text reported "not measurable" by check.py: verify its `x`, `baseline` and the background around it in the spec.
