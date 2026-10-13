# Example: a right-to-left slide in Arabic

A fictional Arabic slide (Naseem Logistics, "Operations Plan 2027"), the mirror of [the demo](../demo): right-aligned titles, KPI cards with Arabic-Indic digits (١٨٪, ٢٫١ يوم), a dark panel with bullets on the right, a roadmap whose chevrons point left, a footer. Built in HTML (`mock.html`) with Dubai and Segoe UI, screenshotted to `source.png`.

| File | What |
|---|---|
| `source.png` | The input image (1920 × 1080) |
| `spec.json` | The spec an assistant writes: Arabic text verbatim, `"lang": "ar-SA"`, `"flip": "h"` on the chevrons, bullets anchored on the right, `"T7+M1"` joining a value whose zero "٠" was detected as a dot |
| `arabic.pptx` | The rebuilt, editable slide (paragraphs right-to-left, bullets on the right) |
| `comparison.png` | Source above, PowerPoint render of the rebuild below |

Every text lands within 1 px of the source after one correction round (PowerPoint render, mean luminance difference about 2/255).

## Reproduce

From the repository root:

```bash
python skills/unscreenshot/scripts/analyze.py examples/arabic/source.png --out examples/arabic/work
python skills/unscreenshot/scripts/fit.py examples/arabic/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/arabic/spec.fitted.json --out examples/arabic/out/arabic.pptx
python skills/unscreenshot/scripts/check.py examples/arabic/out/arabic.pptx examples/arabic/spec.fitted.json
```
