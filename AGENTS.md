# AGENTS.md

This repository ships one agent skill, **unscreenshot**: rebuild a slide image as an editable, pixel-exact PowerPoint.

## Read first
1. `README.md`: what it does.
2. `skills/unscreenshot/SKILL.md`: the source of truth for the method. Scripts are in `skills/unscreenshot/scripts/`.
3. `INSTALL.md`: install paths per platform.

## Installing the skill for a user
Pick the runtime you are running in and do the smallest thing that works:

| Runtime | Action |
|---|---|
| Claude Code | `claude plugin marketplace add zaidlemouakni/unscreenshot` then `claude plugin install unscreenshot@unscreenshot` (plugin manifest: `.claude-plugin/`) |
| Codex | `codex plugin marketplace add zaidlemouakni/unscreenshot --ref main` then `codex plugin add unscreenshot@unscreenshot` (manifests: `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`) |
| Gemini CLI | `gemini extensions install https://github.com/zaidlemouakni/unscreenshot` (manifest: `gemini-extension.json`, context: `GEMINI.md`) |
| Qwen Code | `qwen extensions install zaidlemouakni/unscreenshot` (manifest: `qwen-extension.json`) |
| GitHub Copilot, Cursor, OpenCode, others | `npx skills add zaidlemouakni/unscreenshot`, or copy `skills/unscreenshot` into the agent's skills folder |
| Mistral Vibe | copy `skills/unscreenshot` into `~/.vibe/skills/` |
| Chat apps (Claude, ChatGPT, Gemini, Copilot Studio) | The user uploads `unscreenshot.zip` from the latest release (see `INSTALL.md`); you cannot do it for them |

After installing, tell the user to attach a slide image and ask for an editable PowerPoint.

## Working on the repository
- Tests: `python -m unittest discover -s tests -v` (Pillow and numpy required; scipy optional; the round-trip test needs LibreOffice or PowerPoint and is skipped otherwise).
- Build the zips: `python scripts/package_skill.py` (writes `dist/`).
- Keep the version identical in `skills/unscreenshot/SKILL.md` (metadata), `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `gemini-extension.json` and `qwen-extension.json`; `tests/test_metadata.py` enforces it.
- The scripts must stay dependency-light (Python standard library, Pillow, numpy) and must not make network calls.
- Do not add real company slides to the repository: examples must be fictional or explicitly licensed.
