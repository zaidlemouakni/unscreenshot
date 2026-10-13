# Installation

[English](../../INSTALL.md) · **Français** · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

La skill, c'est le dossier [`skills/unscreenshot/`](../../skills/unscreenshot). Les applications de chat la prennent sous forme de zip ; les agents de code prennent le dossier (ou un plugin/une extension qui pointe dessus). Récupère le zip dans la [dernière version](https://github.com/zaidlemouakni/unscreenshot/releases/latest) : `unscreenshot.zip` (dossier à la racine du zip). `unscreenshot-flat.zip` a `SKILL.md` à la racine, pour les plateformes qui refusent le premier.

Prérequis partout : l'assistant doit pouvoir **exécuter du Python** (exécution de code / interpréteur de code). Les scripts ont besoin de Pillow et numpy, présents dans tous les bacs à sable courants.

Les noms de menus sont donnés en anglais, comme dans l'interface anglaise ; la tienne peut les afficher traduits. Si un chemin ne correspond pas à ton écran, cherche « Skills » dans les paramètres ou la barre latérale.

## Applications de chat

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities : active **Code execution and file creation**.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. Dans une conversation : joins l'image et demande de refaire la slide.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. Ton espace de travail doit avoir les Skills activées (réglage administrateur sur les offres entreprise).
2. Ouvre **Skills**, crée/importe une skill, puis importe `unscreenshot.zip`.
3. Dans une conversation : joins l'image. Les fichiers générés apparaissent dans la conversation, prêts à télécharger.

### Gemini (app)
1. Ouvre **Skills** (elles remplacent les Gems depuis septembre 2026).
2. Crée une skill à partir d'un fichier et importe `unscreenshot.zip`.

### Microsoft Copilot Studio
1. Prérequis administrateur : autoriser le fournisseur de modèles voulu (pour les modèles Claude : Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic, et les modèles externes dans le Power Platform admin center).
2. Crée un agent avec la **new experience** (harnais GitHub Copilot) : il exécute du Python dans un bac à sable et rend des fichiers PowerPoint. Le harnais ne peut plus être changé ensuite.
3. Onglet **Build** > Model : un modèle de vision performant (par ex. Claude Opus ou GPT-5.5).
4. **Build** > Instructions : colle le bloc ci-dessous.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. Teste dans **Preview** avec une image, puis **Publish** vers Teams + Microsoft 365 et **Share**.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## Agents de code et lignes de commande

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
Ou copie le dossier : `cp -R skills/unscreenshot ~/.codex/skills/`.

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
Dans un projet : `.vibe/skills/` ou `.agents/skills/` (dossiers de confiance uniquement).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
Ou : `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
Ou copie `skills/unscreenshot` dans `~/.cursor/skills/`.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### Tout autre agent compatible avec les skills
```bash
npx skills add zaidlemouakni/unscreenshot
```
Ou copie `skills/unscreenshot` dans le dossier de skills de l'agent (souvent `~/.agents/skills/`).

## Vérifier que tout marche

Lance la démo depuis un clone :
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
