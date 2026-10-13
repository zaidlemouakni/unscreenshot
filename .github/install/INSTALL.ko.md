# 설치

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · **한국어** · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

스킬은 [`skills/unscreenshot/`](../../skills/unscreenshot) 폴더 그 자체입니다. 채팅 앱은 zip으로 받고, 코딩 에이전트는 폴더(또는 이 폴더를 가리키는 플러그인/확장)를 받습니다. zip은 [최신 릴리스](https://github.com/zaidlemouakni/unscreenshot/releases/latest)에서 받으세요: `unscreenshot.zip`(zip 최상위에 폴더). `unscreenshot-flat.zip`은 `SKILL.md`를 최상위에 둔 버전으로, 앞의 형식을 받지 않는 플랫폼용입니다.

공통 요구 사항: 어시스턴트가 **Python을 실행**할 수 있어야 합니다(코드 실행 / 코드 인터프리터). 스크립트에 필요한 Pillow와 numpy는 주요 샌드박스에 모두 들어 있습니다.

메뉴 이름은 영어 화면 기준으로 적었습니다. 사용하는 화면에서는 번역되어 보일 수 있습니다. 경로가 화면과 다르면 설정이나 사이드바에서 "Skills"를 찾아보세요.

## 채팅 앱

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: **Code execution and file creation**을 켭니다.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. 채팅에서 이미지를 첨부하고 슬라이드를 다시 만들어 달라고 요청합니다.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. 워크스페이스에서 Skills가 켜져 있어야 합니다(비즈니스 요금제에서는 관리자 설정).
2. **Skills**를 열고 스킬을 만들거나 업로드한 뒤 `unscreenshot.zip`을 업로드합니다.
3. 채팅에서 이미지를 첨부합니다. 생성된 파일은 채팅에 나타나며 내려받을 수 있습니다.

### Gemini (app)
1. **Skills**를 엽니다(2026년 9월부터 Gems를 대신합니다).
2. 파일로 스킬을 만들고 `unscreenshot.zip`을 업로드합니다.

### Microsoft Copilot Studio
1. 관리자 준비 사항: 사용할 모델 제공자를 허용합니다(Claude 모델의 경우: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic, 그리고 Power Platform admin center에서 외부 모델 허용).
2. **new experience**(GitHub Copilot 하네스)로 에이전트를 만듭니다. 샌드박스에서 Python을 실행하고 PowerPoint 파일을 돌려줍니다. 하네스는 나중에 바꿀 수 없습니다.
3. **Build** 탭 > Model: 성능 좋은 비전 모델(예: Claude Opus 또는 GPT-5.5)을 고릅니다.
4. **Build** > Instructions: 아래 블록을 붙여 넣습니다.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. **Preview**에서 이미지로 테스트한 뒤 Teams + Microsoft 365에 **Publish**하고 **Share**합니다.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## 코딩 에이전트와 CLI

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
또는 폴더를 복사합니다: `cp -R skills/unscreenshot ~/.codex/skills/`.

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
프로젝트 단위로는 `.vibe/skills/` 또는 `.agents/skills/`(신뢰할 수 있는 폴더만).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
또는: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
또는 `skills/unscreenshot`을(를) `~/.cursor/skills/`에 복사합니다.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### 스킬을 지원하는 그 밖의 에이전트
```bash
npx skills add zaidlemouakni/unscreenshot
```
또는 `skills/unscreenshot`을(를) 에이전트의 스킬 폴더(보통 `~/.agents/skills/`)에 복사합니다.

## 작동 확인

저장소를 클론한 뒤 데모를 실행합니다:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
