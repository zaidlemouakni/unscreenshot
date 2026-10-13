# Example: a Japanese slide

A fictional Japanese slide (さくら物流, "2027年度 事業計画") with the layout of [the demo](../demo): Japanese text mixed with Latin runs and digits (EV バン, 2.1日), full-width punctuation (、：（）), a letter-spaced eyebrow, KPI cards, bullets and a chevron roadmap. Built in HTML (`mock.html`) with Yu Gothic, screenshotted to `source.png`.

| File | What |
|---|---|
| `source.png` | The input image (1920 × 1080) |
| `spec.json` | The spec an assistant writes: text verbatim, `"lang": "ja-JP"`, lines split by CJK punctuation joined with `+` (`"T4+T6+T5+M1+M2"`) |
| `japanese.pptx` | The rebuilt, editable slide (East Asian font slot set to Yu Gothic) |
| `comparison.png` | Source above, PowerPoint render of the rebuild below |

Every text lands within 1 px of the source on the first build (PowerPoint render, mean luminance difference about 1.5/255).

## Reproduce

From the repository root:

```bash
python skills/unscreenshot/scripts/analyze.py examples/japanese/source.png --out examples/japanese/work
python skills/unscreenshot/scripts/fit.py examples/japanese/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/japanese/spec.fitted.json --out examples/japanese/out/japanese.pptx
python skills/unscreenshot/scripts/check.py examples/japanese/out/japanese.pptx examples/japanese/spec.fitted.json
```
