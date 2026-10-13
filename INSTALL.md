# Install

[Français](.github/install/INSTALL.fr.md) · [简体中文](.github/install/INSTALL.zh-CN.md) · [Español](.github/install/INSTALL.es.md) · [Português](.github/install/INSTALL.pt-BR.md) · [日本語](.github/install/INSTALL.ja.md) · [Tiếng Việt](.github/install/INSTALL.vi.md) · [한국어](.github/install/INSTALL.ko.md) · [فارسی](.github/install/INSTALL.fa.md) · [ไทย](.github/install/INSTALL.th.md) · [العربية](.github/install/INSTALL.ar.md)

The skill is the folder [`skills/unscreenshot/`](skills/unscreenshot). Chat apps take it as a zip; coding agents take the folder (or a plugin/extension that points at it). Get the zip from the [latest release](https://github.com/zaidlemouakni/unscreenshot/releases/latest): `unscreenshot.zip` (folder at the root of the zip). `unscreenshot-flat.zip` has `SKILL.md` at the root instead, for platforms that refuse the first one.

Requirement everywhere: the assistant must be able to **run Python** (code execution / code interpreter). The scripts need Pillow and numpy, which every mainstream sandbox has.

Menu names change often, and your interface may show them in your language; if a path below doesn't match your screen, look for "Skills" in the settings or the sidebar. Slides can be in any language: see *Works in your language* in the README.

## Chat apps

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: turn on **Code execution and file creation**.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. In a chat: attach the image and ask to rebuild the slide.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. Your workspace must have Skills enabled (an admin setting on business plans).
2. Open **Skills**, create/upload a skill, and upload `unscreenshot.zip`.
3. In a chat: attach the image. Generated files appear in the chat to download.

### Gemini (app)
1. Open **Skills** (they replace Gems from autumn 2026).
2. Create a skill from a file and upload `unscreenshot.zip`.

### Microsoft Copilot Studio
1. Admin prerequisites: allow the model provider you want (for Claude models: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic, and external models in the Power Platform admin center).
2. Create an agent with the **new experience** (GitHub Copilot harness): it runs Python in a sandbox and returns PowerPoint files. The harness can't be changed later.
3. **Build** tab > Model: a strong vision model (e.g. Claude Opus or GPT-5.5).
4. **Build** > Instructions: paste the block below.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. Test in **Preview** with an image, then **Publish** to Teams + Microsoft 365 and **Share**.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## Coding agents and CLIs

### Claude Code
```bash
claude plugin marketplace add zaidlemouakni/unscreenshot
claude plugin install unscreenshot@unscreenshot
```

### Codex
```bash
codex plugin marketplace add zaidlemouakni/unscreenshot --ref main
codex plugin add unscreenshot@unscreenshot
```
Or copy the folder: `cp -R skills/unscreenshot ~/.codex/skills/`.

### Gemini CLI
```bash
gemini extensions install https://github.com/zaidlemouakni/unscreenshot
```

### Mistral Vibe (CLI)
```bash
git clone https://github.com/zaidlemouakni/unscreenshot
mkdir -p ~/.vibe/skills
cp -R unscreenshot/skills/unscreenshot ~/.vibe/skills/
```
In a project instead: `.vibe/skills/` or `.agents/skills/` (trusted folders only).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
Or: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
Or copy `skills/unscreenshot` into `~/.cursor/skills/`.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### Any other skills-compatible agent
```bash
npx skills add zaidlemouakni/unscreenshot
```
Or copy `skills/unscreenshot` into the agent's skills folder (often `~/.agents/skills/`).

## Check that it works

Run the demo from a clone:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
