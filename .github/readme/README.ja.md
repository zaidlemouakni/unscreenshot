<p align="center"><img src="../../docs/logo.png" width="120" alt=""></p>

<h1 align="center">unscreenshot</h1>

<p align="center"><b>スクショを元に戻して、スライドを取り戻す。</b><br>
スクリーンショットを入れると、編集できる PowerPoint が出てきます。ピクセル単位で、どの言語でも。</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.fr.md" title="Français">🇫🇷</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <b title="日本語">🇯🇵</b> ·
  <a href="README.vi.md" title="Tiếng Việt">🇻🇳</a> ·
  <a href="README.ko.md" title="한국어">🇰🇷</a> ·
  <a href="README.fa.md" title="فارسی">🇮🇷</a> ·
  <a href="README.th.md" title="ไทย">🇹🇭</a> ·
  <a href="README.ar.md" title="العربية">🇸🇦</a>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <a href="https://github.com/zaidlemouakni/unscreenshot/actions/workflows/ci.yml"><img src="https://github.com/zaidlemouakni/unscreenshot/actions/workflows/ci.yml/badge.svg" alt="tests"></a>
  <img src="https://img.shields.io/badge/works%20with-Claude%20%C2%B7%20ChatGPT%20%C2%B7%20Gemini%20%C2%B7%20Copilot%20%C2%B7%20Codex%20%C2%B7%20Cursor-1B2340.svg" alt="Claude · ChatGPT · Gemini · Copilot · Codex · Cursor">
</p>

![スライドのスクリーンショットが編集可能な PowerPoint に：すべてのテキスト、カード、色を計測して再構築](../../docs/demo.gif)

手元にあるのはスライドの画像だけ。会議中に撮ったスクリーンショット、AI が画像として生成したスライド、PDF の 1 ページ、画像で送られてきた資料。必要なのは PowerPoint ファイルなのに、もう見つからないか、最初から存在しない。

`unscreenshot` は**エージェント用のスキル**です。AI アシスタントに画像を渡すと `.pptx` が返ってきます。テキストボックス、箇条書き、カード、線、色のすべてを画像上で計測し、編集可能な PowerPoint のネイティブオブジェクトとして再構築します。

## 30 秒でインストール

スキルをインストールできるエージェント（Claude Code、Codex、Gemini CLI、Cursor、Copilot など）に、次の文を貼り付けてください：

```text
https://github.com/zaidlemouakni/unscreenshot から unscreenshot スキルをインストールしてください。リポジトリの AGENTS.md に従ってください。
```

または、お使いのプラットフォームを選んでください：

| AI を使う場所 | 方法 |
|---|---|
| **Claude** (claude.ai) | Settings > Capabilities でコード実行をオンにし、Skills > [`unscreenshot.zip`](https://github.com/zaidlemouakni/unscreenshot/releases/latest) をアップロード |
| **ChatGPT** (Business, Enterprise, Edu) | Skills > 同じ zip をアップロード |
| **Gemini** (app) | Skills > 同じ zip をアップロード |
| **Microsoft Copilot Studio** | Agent > Build > Skills > Upload a skill > zip を選択 |
| **Claude Code** | `claude plugin marketplace add zaidlemouakni/unscreenshot` の後に `claude plugin install unscreenshot@unscreenshot` |
| **Codex** | `codex plugin marketplace add zaidlemouakni/unscreenshot --ref main` の後に `codex plugin add unscreenshot@unscreenshot` |
| **Gemini CLI** | `gemini extensions install https://github.com/zaidlemouakni/unscreenshot` |
| **Mistral Vibe** | `skills/unscreenshot` を `~/.vibe/skills/` にコピー |
| **GitHub Copilot, Cursor, OpenCode…** | `npx skills add zaidlemouakni/unscreenshot` |

各プラットフォームのメニュー、フォルダー、手順の詳細：[INSTALL](../install/INSTALL.ja.md)（メニュー名は英語で表記しています）。

## 60 秒で試す

1. お使いのプラットフォームにスキルをインストールします（上記）。
2. [サンプルのスクリーンショット](../../examples/demo/source.png)を保存するか、手元のスライド画像を用意します。
3. 画像を添付し、普段の言語でこう頼みます：
   > このスライドを、編集できる PowerPoint でそっくりそのまま作り直して。
4. `.pptx` を開いてタイトルをクリックしてみてください。画像ではなく、本物のテキストボックスです。

比較用のビフォー／アフター画像も届きます。複数の画像や複数ページの PDF は、同じファイルの中で 1 枚ずつスライドになります。

## あなたの言語で使えます

![1 枚のスライドに 12 種類の文字、すべて再構築](../../docs/languages-before-after.png)

アラビア語・ペルシア語・ヘブライ語（右から左へ書く言語）、中国語、日本語、韓国語、ヒンディー語、タイ語、ベトナム語、ロシア語、ギリシャ語、そしてラテン文字で書くすべての言語。

- テキストは一字一句そのまま、元の文字体系で再現します。翻訳は一切しません。
- 右から左へのスライドは、左右反転したレイアウトを保ちます。箇条書きは右側に、ロードマップは左向きに。
- 文字体系ごとに PowerPoint が使うフォントを割り当て、その文字の描かれ方に合わせてサイズを計測します。

完全な作例：[アラビア語](../../examples/arabic) · [日本語](../../examples/japanese) · [1 枚に 12 種類の文字](../../examples/languages)。

## 得られるもの

![変換前：スクリーンショット。変換後：同じスライドを編集可能な PowerPoint で](../../docs/japanese-before-after.png)

- **ネイティブで編集できるオブジェクト**：本物のテキストが入ったテキストボックス、本物の箇条書き、四角形、角丸カード、ピル形、円、シェブロン、線、グループ。言葉を変える、カードの色を変える、ブロックを動かす。普通のスライドとして扱えます。
- **推測ではなく計測**：位置、サイズ、色はピクセル単位の計測から得ています。フォントサイズは、各行の幅が画像と同じになるように計算します。
- **確認できる証拠**：元画像と再構築したスライドを並べた画像と、両者を重ねた画像。

## OCR、PDF 変換ツール、AI スライド生成ツールとの違いは？

OCR が返すのは文字で、スライドではありません。変換ツールには元の PDF が必要です。生成ツールは新しいスライドを作ります。unscreenshot は、手元にあるそのスライドを取り戻します。

| | OCR | PDF 変換ツール | AI スライド生成ツール | **unscreenshot** |
|---|:-:|:-:|:-:|:-:|
| スクリーンショットや写真から始められる | ✅ | ❌ | ❌ | ✅ |
| すべての語句をそのまま保持 | ✅ | ✅ | ❌ | ✅ |
| レイアウト、位置、サイズが同じ | ❌ | ⚠️ | ❌ | ✅ |
| ネイティブの図形、カード、本物の箇条書き | ❌ | ⚠️ | ✅ | ✅ |
| 右から左への書字と非ラテン文字 | ⚠️ | ⚠️ | ⚠️ | ✅ |

⚠️ ツールとファイルによります。

## 仕組み

アシスタント（画像を読めるモデルなら何でも）は文字を読むだけです。それ以外はすべてテスト済みの小さな Python スクリプトが行うので、小さなモデルでも大きなモデルでも結果は同じです。

1. **解析**：テキスト行、塗りつぶし図形、罫線、箇条書きの点、アイコンをすべて見つけ、ベースライン、インクの幅、色を計測します。
2. **読み取り**：モデルが拡大画像から各行の文字を入力します。読み取りが画像と合わない行はスクリプトが指摘します。
3. **仕様**：スクリプトが計測結果からスライドの記述を書き出します。図形、シェブロン、箇条書き、フォント、サイズ、配置まで含みます。
4. **フィッティング**：文字体系ごとに、各テキストのインク幅が画像と一致するようフォントサイズを求めます。
5. **構築**：依存関係のない生成器が `.pptx` を出力します（必要なのは Pillow と numpy だけ）。
6. **チェック**：スライドをレンダリング（LibreOffice または PowerPoint）して画像と比較し、最大 3 回まで修正します。

このリポジトリの 4 つの作例では、1 回の修正ですべてのテキストが元画像から 1 ピクセル以内に収まります。

## 制限事項

- **フォント**：画像で Office 以外のフォント（Poppins、Inter、Noto など）が使われている場合は、最も近い Office フォントを使います。位置、サイズ、行の幅は一致しますが、字形は少し異なります。
- **アイコン、ロゴ、写真**は画像から切り抜いて（背景を透明にして）使い、描き直しはしません。
- **縦書きの日本語・中国語**は画像のまま残します。
- アシスタントが **Python を実行**（コード実行）できる必要があります。できない場合は、v2 で予定している MCP サーバーが必要です。

## よくある質問

**無料ですか？**\
はい。MIT ライセンスで、アカウントも API キーも不要です。いつも使っているアシスタントの中で動きます。

**スライドがパソコンの外に出ることはありますか？**\
スキル自体はネットワーク通信を一切行いません。スクリプトはアシスタントのサンドボックスか、お使いのマシン上で動きます。画像はアシスタントが見ます。アシスタントに渡すほかのファイルと同じです。

**どのアシスタントで使えますか？**\
画像を読めて Python を実行できるアシスタントなら使えます。インストール表にあるもののほか、`SKILL.md` 形式を読めるアシスタントにも対応します。小さな文字の読み取りはモデルの視覚性能次第で、強いモデルほど正確に読めます。

**細部がずれていたら？**\
スキルは結果をレンダリングして元の画像と比較し、最大 3 回まで修正します。そのうえで、まだ違う点を伝えます。すべて編集できるので、最後の手直しは数秒で済みます。

**画像を PowerPoint に貼るだけではだめですか？**\
それでは画像のままです。言葉ひとつ変えられず、数字も直せず、カードも再利用できません。

**スライドを改善したり翻訳したりできますか？**\
自分からはしません。意図的な設計です。画像に写っているものを、誤字も含めて一字一句そのまま再構築します。本物の PowerPoint を手に入れたら、あとはアシスタントに好きな変更を頼んでください。

コード、テスト、作例については、英語版 README の[リポジトリ構成](../../README.md#repository)をご覧ください。翻訳の改善も歓迎します：[CONTRIBUTING.md](../../CONTRIBUTING.md)。

## ライセンス

MIT.

*スライドを手作業で作り直さずに済んだら、ぜひスターを。*
