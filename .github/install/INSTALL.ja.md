# インストール

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · **日本語** · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

スキルの実体は [`skills/unscreenshot/`](../../skills/unscreenshot) フォルダーです。チャットアプリには zip で読み込み、コーディングエージェントにはフォルダー（またはそれを指すプラグイン／拡張機能）を渡します。zip は[最新リリース](https://github.com/zaidlemouakni/unscreenshot/releases/latest)から入手できます：`unscreenshot.zip`（zip の直下にフォルダー）。`unscreenshot-flat.zip` は `SKILL.md` を直下に置いたもので、前者を受け付けないプラットフォーム向けです。

どの環境でも必要な条件：アシスタントが **Python を実行**できること（コード実行／コードインタープリター）。スクリプトに必要な Pillow と numpy は、主要なサンドボックスにはすべて入っています。

メニュー名は英語版の画面どおりに記載しています。お使いの画面では翻訳されて表示される場合があります。手順が画面と合わないときは、設定やサイドバーで「Skills」を探してください。

## チャットアプリ

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities：**Code execution and file creation** をオンにします。
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`。
3. チャットで画像を添付し、スライドの作り直しを頼みます。

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. ワークスペースで Skills が有効になっている必要があります（法人向けプランでは管理者の設定）。
2. **Skills** を開いてスキルを作成／アップロードし、`unscreenshot.zip` をアップロードします。
3. チャットで画像を添付します。生成されたファイルはチャット内に表示され、ダウンロードできます。

### Gemini (app)
1. **Skills** を開きます（2026 年 9 月から Gems に代わる機能です）。
2. ファイルからスキルを作成し、`unscreenshot.zip` をアップロードします。

### Microsoft Copilot Studio
1. 管理者による準備：使いたいモデルプロバイダーを許可します（Claude モデルの場合：Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic、さらに Power Platform admin center で外部モデルを許可）。
2. **new experience**（GitHub Copilot ハーネス）でエージェントを作成します。サンドボックスで Python を実行し、PowerPoint ファイルを返せます。ハーネスは後から変更できません。
3. **Build** タブ > Model：高性能なビジョンモデル（例：Claude Opus や GPT-5.5）を選びます。
4. **Build** > Instructions：下のブロックを貼り付けます。
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`。
6. **Preview** で画像を使ってテストし、Teams + Microsoft 365 に **Publish** して **Share** します。

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## コーディングエージェントと CLI

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
またはフォルダーをコピー：`cp -R skills/unscreenshot ~/.codex/skills/`。

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
プロジェクト単位なら `.vibe/skills/` または `.agents/skills/`（信頼済みフォルダーのみ）。

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
または：`git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
または `skills/unscreenshot` を `~/.cursor/skills/` にコピーします。

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### その他のスキル対応エージェント
```bash
npx skills add zaidlemouakni/unscreenshot
```
または `skills/unscreenshot` をエージェントのスキルフォルダー（多くは `~/.agents/skills/`）にコピーします。

## 動作確認

クローンしたリポジトリでデモを実行します：
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
