---
name: unscreenshot
description: Rebuild a slide from an image (screenshot, PNG/JPG/WebP, PDF page) as an editable PowerPoint (.pptx) that matches it pixel for pixel - positions, sizes, colours, fonts and every word, in any language or script. Use when someone shares a picture of a slide and wants it recreated, made editable, converted to PowerPoint, or "the PPTX back".
license: MIT
metadata:
  version: 1.1.0
---

# unscreenshot: screenshot in, editable PowerPoint out

The scripts measure the image and build the whole slide: shapes, colours, fonts, sizes, positions, bullets. **Your only job is to read the text exactly.** Follow the steps in order. Do not write the slide yourself and do not edit the files the scripts write.

- `$SKILL` = the folder of this file. Work in `/tmp/us` (any writable folder works).
- Needs Python 3 with Pillow and numpy. If they are missing, run `pip install pillow numpy`.
- Talk to the user in their language.

## Steps

**1. Start.** `python $SKILL/scripts/run.py start <the attached image or PDF> --out /tmp/us`
It prints the number of text lines on each slide and the files to read. A PDF gives one slide per page: `p01`, `p02`…

**2. Read.** Open every `/tmp/us/p01/read_*.png` (and `p02`… if there are more slides). Each row is one text line of the slide, enlarged, with its id (`T1`, `T2`…) in red on the left. Then write `/tmp/us/p01/texts.txt`: keep its lines and their order, and after each id write the exact text of that row, like `T7: Faster deliveries, lower cost per parcel:`
- Character for character: case, accents, punctuation and symbols (’ “ ” – — → • %), digits as shown (١٢٪, ۱۲٪ and 12% are different texts).
- Right-to-left text (Arabic, Persian, Hebrew): type it as it is read, not as it is displayed.
- Never translate, correct or complete anything. Keep a typo as it is.
- If a row is not text (part of a logo, a drawing), leave the text after its id empty: `T9:`

**3. Finish.** `python $SKILL/scripts/run.py finish --out /tmp/us --pptx /tmp/us/slide.pptx`
It builds the slide, renders it, compares it with the image and corrects it, by itself. If it reports a problem in texts.txt (a missing or unknown id), fix texts.txt and run step 3 again.

**4. Re-read if asked.** If finish lists lines to re-read, open each crop it names (`reread/T7.png`). Correct the text in texts.txt only if it is wrong, then run step 3 again. Do this twice at most, then go on.

**5. Deliver.** Copy the .pptx where your platform gives files to the user (claude.ai: `/mnt/user-data/outputs/`; ChatGPT: `/mnt/data/`; others: the platform's file mechanism), and show `/tmp/us/p01/side_by_side.png` (the image above, the rebuild below) when it exists. Then write two or three lines: the fonts used (and those approximated), anything kept as a picture, any difference you can see. Do not describe the method.

## If something goes wrong

- A script fails: show its last error lines to the user and stop; do not rebuild the slide another way.
- To refine a slide by hand (only if the user asks), see `reference/expert.md`.
- Everything stays on this machine: the scripts make no network calls.
