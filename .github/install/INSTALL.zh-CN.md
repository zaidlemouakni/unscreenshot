# 安装

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · **简体中文** · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

技能本身就是 [`skills/unscreenshot/`](../../skills/unscreenshot) 文件夹。聊天应用以 zip 形式导入；编程智能体直接使用该文件夹（或指向它的插件/扩展）。从[最新版本](https://github.com/zaidlemouakni/unscreenshot/releases/latest)下载 zip：`unscreenshot.zip`（zip 根目录是该文件夹）。`unscreenshot-flat.zip` 则把 `SKILL.md` 放在根目录，供不接受前者的平台使用。

所有平台的共同前提：助手必须能够**运行 Python**（代码执行 / 代码解释器）。脚本需要 Pillow 和 numpy，主流沙箱都已自带。

菜单名称按英文界面标注，你的界面可能显示为翻译后的名称。如果路径与屏幕不符，请在设置或侧边栏中查找“Skills”。

## 聊天应用

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities：开启 **Code execution and file creation**。
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`。
3. 在对话中：附上图片，请它重建这页幻灯片。

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. 你的工作区必须启用 Skills（企业版套餐中由管理员设置）。
2. 打开 **Skills**，创建/上传技能，然后上传 `unscreenshot.zip`。
3. 在对话中：附上图片。生成的文件会出现在对话中供下载。

### Gemini (app)
1. 打开 **Skills**（自 2026 年 9 月起取代 Gems）。
2. 从文件创建技能并上传 `unscreenshot.zip`。

### Microsoft Copilot Studio
1. 管理员前提：允许你要使用的模型提供商（使用 Claude 模型时：Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic，并在 Power Platform admin center 中允许外部模型）。
2. 使用 **new experience**（GitHub Copilot 运行环境）创建智能体：它能在沙箱中运行 Python 并返回 PowerPoint 文件。运行环境之后无法更改。
3. **Build** 选项卡 > Model：选择能力强的视觉模型（例如 Claude Opus 或 GPT-5.5）。
4. **Build** > Instructions：粘贴下方的文本块。
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`。
6. 在 **Preview** 中用一张图片测试，然后 **Publish** 到 Teams + Microsoft 365 并 **Share**。

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## 编程智能体和命令行工具

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
或者复制文件夹：`cp -R skills/unscreenshot ~/.codex/skills/`。

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
如果只在某个项目中使用：`.vibe/skills/` 或 `.agents/skills/`（仅限受信任的文件夹）。

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
或者：`git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
或者把 `skills/unscreenshot` 复制到 `~/.cursor/skills/`。

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### 其他兼容技能的智能体
```bash
npx skills add zaidlemouakni/unscreenshot
```
或者把 `skills/unscreenshot` 复制到该智能体的技能文件夹（通常是 `~/.agents/skills/`）。

## 确认安装成功

在克隆的仓库中运行演示：
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
