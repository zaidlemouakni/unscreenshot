# Instalação

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · **Português** · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

A skill é a pasta [`skills/unscreenshot/`](../../skills/unscreenshot). Os apps de chat a recebem como zip; os agentes de código recebem a pasta (ou um plugin/extensão que aponta para ela). Baixe o zip da [versão mais recente](https://github.com/zaidlemouakni/unscreenshot/releases/latest): `unscreenshot.zip` (pasta na raiz do zip). `unscreenshot-flat.zip` tem o `SKILL.md` na raiz, para as plataformas que recusam o primeiro.

Requisito em todo lugar: o assistente precisa conseguir **executar Python** (execução de código / interpretador de código). Os scripts precisam de Pillow e numpy, que todos os ambientes isolados comuns já têm.

Os nomes dos menus estão em inglês, como na interface em inglês; a sua pode mostrá-los traduzidos. Se um caminho não bater com a sua tela, procure "Skills" nas configurações ou na barra lateral.

## Apps de chat

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: ative **Code execution and file creation**.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. Em uma conversa: anexe a imagem e peça para refazer o slide.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. Seu workspace precisa ter as Skills ativadas (uma configuração de administrador nos planos empresariais).
2. Abra **Skills**, crie/envie uma skill e envie `unscreenshot.zip`.
3. Em uma conversa: anexe a imagem. Os arquivos gerados aparecem na conversa para baixar.

### Gemini (app)
1. Abra **Skills** (elas substituem os Gems desde setembro de 2026).
2. Crie uma skill a partir de um arquivo e envie `unscreenshot.zip`.

### Microsoft Copilot Studio
1. Pré-requisitos de administração: permita o provedor de modelos desejado (para os modelos Claude: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic, e os modelos externos no Power Platform admin center).
2. Crie um agente com a **new experience** (ambiente do GitHub Copilot): ele executa Python em um ambiente isolado e devolve arquivos do PowerPoint. O ambiente não pode ser trocado depois.
3. Aba **Build** > Model: um modelo de visão forte (por exemplo, Claude Opus ou GPT-5.5).
4. **Build** > Instructions: cole o bloco abaixo.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. Teste em **Preview** com uma imagem e depois **Publish** no Teams + Microsoft 365 e **Share**.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## Agentes de código e linha de comando

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
Ou copie a pasta: `cp -R skills/unscreenshot ~/.codex/skills/`.

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
Em um projeto: `.vibe/skills/` ou `.agents/skills/` (somente pastas confiáveis).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
Ou: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
Ou copie `skills/unscreenshot` para `~/.cursor/skills/`.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### Qualquer outro agente compatível com skills
```bash
npx skills add zaidlemouakni/unscreenshot
```
Ou copie `skills/unscreenshot` para a pasta de skills do agente (geralmente `~/.agents/skills/`).

## Verifique se funciona

Rode a demo a partir de um clone:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
