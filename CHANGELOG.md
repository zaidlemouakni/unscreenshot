# Changelog

## 1.0.0 (2026-10-13)

First public release.

- Skill `unscreenshot` in the open Agent Skills format: works in Claude, ChatGPT, Gemini, Microsoft Copilot Studio, Claude Code, Codex, Gemini CLI, Qwen Code, Mistral Vibe, GitHub Copilot, Cursor and OpenCode.
- **Every script**: Latin (incl. Vietnamese), Cyrillic, Greek, Arabic, Persian, Hebrew, Chinese, Japanese, Korean, Hindi and the other Indic scripts, Thai.
  - Each run gets its three PowerPoint font slots (Latin, East Asian, complex script) and its language.
  - Right-to-left paragraphs and bullets; mirrored arrows (`flip`).
  - No letter-spacing on joined scripts.
  - Arabic widths measured with a built-in joiner when Pillow has no shaping engine.
  - Indic scripts sized and placed from their headline, CJK from their ink box.
  - A simplified Unicode bidi algorithm puts numbers in right-to-left text in display order.
  - All measured in PowerPoint (first-baseline rule per font, alignment and bullets in right-to-left paragraphs, font slots per script).
- `analyze.py`: text lines, filled regions (cards, pills, containers), rules, bullet marks and graphics, with baselines, cap and x-heights, letter-body and headline bands, ink widths and colours.
  - Dots and accents drawn apart from their letters are attached to their line.
  - An annotated overview and enlarged line sheets help transcription.
- `fit.py`: resolves `from` references (pieces of one line joined with `+`).
  - Fits the font size on the measured ink width (real ink, not Pillow's layout box) with the font PowerPoint will use for that script.
  - One size per role.
- `build_pptx.py` on `pptx_writer.py`: a dependency-free .pptx writer (text boxes with exact line spacing, bullets, preset shapes with adjustments, polygons, connectors, pictures, groups).
- `check.py`: renders with LibreOffice or PowerPoint and writes side-by-side and overlay images, a per-text report and a corrected spec.
  - Errors are measured on the anchored edge.
  - Same-role texts are scaled together.
  - `--slide N` handles decks with several slides.
- `prepare.py`, `probe.py`, `crop.py`, `env_check.py` helpers.
- Examples: a Latin demo, a right-to-left Arabic slide, a Japanese slide and twelve scripts on one slide. Each comes with its spec and rebuilt .pptx; every text is within 1 px of the source.
- README and install guide in 11 languages; unit, round-trip and docs tests; CI; release zips.
