# Instalación

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · **Español** · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

La skill es la carpeta [`skills/unscreenshot/`](../../skills/unscreenshot). Las aplicaciones de chat la reciben como zip; los agentes de código reciben la carpeta (o un plugin/extensión que apunta a ella). Descarga el zip de la [última versión](https://github.com/zaidlemouakni/unscreenshot/releases/latest): `unscreenshot.zip` (la carpeta en la raíz del zip). `unscreenshot-flat.zip` tiene `SKILL.md` en la raíz, para las plataformas que rechazan el primero.

Requisito en todas partes: el asistente debe poder **ejecutar Python** (ejecución de código / intérprete de código). Los scripts necesitan Pillow y numpy, que ya tienen todos los entornos aislados habituales.

Los nombres de los menús están en inglés, como en la interfaz en inglés; la tuya puede mostrarlos traducidos. Si una ruta no coincide con tu pantalla, busca «Skills» en la configuración o en la barra lateral.

## Aplicaciones de chat

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: activa **Code execution and file creation**.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. En un chat: adjunta la imagen y pide que se rehaga la diapositiva.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. Tu espacio de trabajo debe tener las Skills activadas (un ajuste de administrador en los planes empresariales).
2. Abre **Skills**, crea/sube una skill y sube `unscreenshot.zip`.
3. En un chat: adjunta la imagen. Los archivos generados aparecen en el chat para descargarlos.

### Gemini (app)
1. Abre **Skills** (sustituyen a las Gems desde septiembre de 2026).
2. Crea una skill a partir de un archivo y sube `unscreenshot.zip`.

### Microsoft Copilot Studio
1. Requisitos de administración: permite el proveedor de modelos que quieras (para los modelos Claude: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic, y los modelos externos en el Power Platform admin center).
2. Crea un agente con la **new experience** (entorno de GitHub Copilot): ejecuta Python en un entorno aislado y devuelve archivos de PowerPoint. El entorno no se puede cambiar después.
3. Pestaña **Build** > Model: un modelo de visión potente (por ejemplo, Claude Opus o GPT-5.5).
4. **Build** > Instructions: pega el bloque de abajo.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. Prueba en **Preview** con una imagen y luego **Publish** en Teams + Microsoft 365 y **Share**.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## Agentes de código y línea de comandos

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
O copia la carpeta: `cp -R skills/unscreenshot ~/.codex/skills/`.

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
En un proyecto: `.vibe/skills/` o `.agents/skills/` (solo carpetas de confianza).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
O bien: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
O copia `skills/unscreenshot` en `~/.cursor/skills/`.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### Cualquier otro agente compatible con skills
```bash
npx skills add zaidlemouakni/unscreenshot
```
O copia `skills/unscreenshot` en la carpeta de skills del agente (a menudo `~/.agents/skills/`).

## Comprobar que funciona

Ejecuta la demo desde un clon:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
