# Example: twelve scripts on one slide

The same three lines ("Quarterly report", "Revenue +12%", "Product launch in Q3") in twelve languages: Arabic, Persian, Hebrew, Chinese, Japanese, Korean, Hindi, Thai, Vietnamese, Russian, Greek and Spanish. Each card uses the Office font Windows uses for its script (Dubai, Segoe UI, Microsoft YaHei, Yu Gothic, Malgun Gothic, Nirmala UI, Leelawadee UI, Arial, Calibri). Built in HTML (`mock.html`), screenshotted to `source.png`.

| File | What |
|---|---|
| `source.png` | The input image (1920 × 1080) |
| `spec.json` | One `lang` per card, right-aligned right-to-left cards, one size per role (eyebrow, heading, body) |
| `languages.pptx` | The rebuilt, editable slide |
| `comparison.png` | Source above, PowerPoint render of the rebuild below |

What each script exercises: Arabic and Persian joining and right-to-left paragraphs, Hebrew right-to-left, CJK in the East Asian font slot, Hindi without a shaping engine (sized and placed from its headline), Thai and Vietnamese stacked marks. Every text lands within 1 px of the source after one correction round (PowerPoint render).

One detail: browsers draw the Persian "۱۲٪" with the percent sign on the left, PowerPoint (Persian or Arabic run) on the right. The spec puts that number in its own run with `"lang": "en-US"`, which makes PowerPoint match the image.

## Reproduce

From the repository root:

```bash
python skills/unscreenshot/scripts/analyze.py examples/languages/source.png --out examples/languages/work
python skills/unscreenshot/scripts/fit.py examples/languages/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/languages/spec.fitted.json --out examples/languages/out/languages.pptx
python skills/unscreenshot/scripts/check.py examples/languages/out/languages.pptx examples/languages/spec.fitted.json
```
