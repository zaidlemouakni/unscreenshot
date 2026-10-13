# Demo: Northwind Logistics, "Operations Plan 2027"

A fictional slide, built in HTML (`mock.html`) and screenshotted to `source.png` (1920 × 1080), the way AI slide generators and web decks look: Poppins headings, Open Sans body text, KPI cards, a dark panel with round bullets, a chevron roadmap.

| File | What |
|---|---|
| `source.png` | The input image |
| `spec.json` | The spec an assistant writes after reading the image: texts verbatim, fonts, roles, and `from` references to the analysis |
| `northwind.pptx` | The rebuilt, editable slide |
| `comparison.png` | Source above, PowerPoint render of the rebuild below |
| `mock.html` | The fictional slide's source, to regenerate `source.png` |

Fonts: Poppins is rebuilt with Century Gothic and Open Sans with Segoe UI (the closest Office fonts). Sizes are fitted on the measured ink widths, so lines keep their length.

## Reproduce

From the repository root:

```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/northwind.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/northwind.pptx examples/demo/spec.fitted.json
```

The check needs LibreOffice or PowerPoint. With PowerPoint, after one correction round (rebuild from `out/check/spec.corrected.json`), every text sits within 1 px of the source and the mean luminance difference is about 5/255.
