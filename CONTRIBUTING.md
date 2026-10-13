# Contributing

Thanks for helping. The most useful contributions are **hard slides**: an image where the rebuild goes wrong.

## Report a bad rebuild
Open an issue with:
1. the source image (only slides you are allowed to share; blur anything confidential),
2. the `.pptx` you got, or `out/check/side_by_side.png` and `report.txt`,
3. which assistant and model ran the skill (Claude, ChatGPT, Gemini, Copilot…).

## Change the code
- Python 3.10+, Pillow and numpy. scipy and fontTools are optional (fallbacks exist and are tested; `UNSCREENSHOT_NO_RAQM=1` runs the paths used when Pillow has no text-shaping engine).
- No network calls and no new heavy dependency in `skills/unscreenshot/scripts/`: the skill runs in locked-down sandboxes.
- Run the tests before a pull request:
  ```bash
  python -m unittest discover -s tests -v
  ```
  The round-trip test renders the demo with LibreOffice or PowerPoint when one is installed; set `UNSCREENSHOT_RENDER=0` to skip it.
- A change to the measuring or placement logic should come with a test, ideally a small synthetic image.
- If you change the method, update `SKILL.md` and `reference/spec-format.md` in the same pull request.
- Keep the version identical in `SKILL.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json`, `qwen-extension.json` and `CHANGELOG.md` (`tests/test_metadata.py` checks it).

## Add an example
Examples must be fictional or explicitly licensed for redistribution. Put the source image, the spec and the rebuilt `.pptx` in `examples/<name>/`, with a short README, and add its expectations to `tests/test_examples.py`. Slides in scripts or layouts not covered yet (Urdu, Tamil, Khmer, vertical text, dense tables) are especially welcome.

## Improve a translation
The README and the install guide exist in 11 languages (`.github/readme/`, `.github/install/`). Translations may contain mistakes: native speakers, please fix anything that reads oddly. Keep every command and code block identical to the English version (`tests/test_docs.py` checks it), and keep menu names in English.

## Release
1. Bump the version everywhere listed above and add a CHANGELOG entry.
2. Tag `vX.Y.Z` and push the tag: the release workflow attaches `unscreenshot.zip` and `unscreenshot-flat.zip` to a GitHub release.
