<p align="center"><img src="../../docs/logo.png" width="120" alt=""></p>

<h1 align="center">unscreenshot</h1>

<p align="center"><b>스크린샷을 되돌려 슬라이드를 되찾으세요.</b><br>
스크린샷을 넣으면 편집 가능한 PowerPoint가 나옵니다. 픽셀 단위로, 어떤 언어든.</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.fr.md" title="Français">🇫🇷</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a> ·
  <a href="README.vi.md" title="Tiếng Việt">🇻🇳</a> ·
  <b title="한국어">🇰🇷</b> ·
  <a href="README.fa.md" title="فارسی">🇮🇷</a> ·
  <a href="README.th.md" title="ไทย">🇹🇭</a> ·
  <a href="README.ar.md" title="العربية">🇸🇦</a>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <a href="https://github.com/zaidlemouakni/unscreenshot/actions/workflows/ci.yml"><img src="https://github.com/zaidlemouakni/unscreenshot/actions/workflows/ci.yml/badge.svg" alt="tests"></a>
  <img src="https://img.shields.io/badge/works%20with-Claude%20%C2%B7%20ChatGPT%20%C2%B7%20Gemini%20%C2%B7%20Copilot%20%C2%B7%20Codex%20%C2%B7%20Cursor-1B2340.svg" alt="Claude · ChatGPT · Gemini · Copilot · Codex · Cursor">
</p>

![슬라이드 스크린샷이 편집 가능한 PowerPoint로: 모든 텍스트, 카드, 색상을 측정해 다시 만듭니다](../../docs/demo.gif)

손에 있는 건 슬라이드 이미지뿐입니다. 회의 중에 찍은 스크린샷, AI가 이미지로 만든 슬라이드, PDF의 한 페이지, 이미지로 받은 발표 자료. 필요한 건 PowerPoint 파일인데, 이미 사라졌거나 처음부터 없었습니다.

`unscreenshot`은 **에이전트용 스킬**입니다. AI 어시스턴트에 이미지를 주면 `.pptx`를 돌려받습니다. 텍스트 상자, 글머리 기호, 카드, 선, 색상 하나하나를 이미지에서 측정해 편집 가능한 PowerPoint 기본 개체로 다시 만듭니다.

## 30초 설치

스킬을 설치할 수 있는 에이전트(Claude Code, Codex, Gemini CLI, Cursor, Copilot 등)에 다음을 붙여 넣으세요:

```text
https://github.com/zaidlemouakni/unscreenshot 에서 unscreenshot 스킬을 설치해 줘. 저장소의 AGENTS.md를 따라 줘.
```

또는 사용하는 플랫폼을 고르세요:

| AI를 쓰는 곳 | 방법 |
|---|---|
| **Claude** (claude.ai) | Settings > Capabilities에서 코드 실행을 켠 다음 Skills > [`unscreenshot.zip`](https://github.com/zaidlemouakni/unscreenshot/releases/latest) 업로드 |
| **ChatGPT** (Business, Enterprise, Edu) | Skills > 같은 zip 업로드 |
| **Gemini** (app) | Skills > 같은 zip 업로드 |
| **Microsoft Copilot Studio** | Agent > Build > Skills > Upload a skill > zip 선택 |
| **Claude Code** | `claude plugin marketplace add zaidlemouakni/unscreenshot` 다음에 `claude plugin install unscreenshot@unscreenshot` |
| **Codex** | `codex plugin marketplace add zaidlemouakni/unscreenshot --ref main` 다음에 `codex plugin add unscreenshot@unscreenshot` |
| **Gemini CLI** | `gemini extensions install https://github.com/zaidlemouakni/unscreenshot` |
| **Mistral Vibe** | `skills/unscreenshot`을(를) `~/.vibe/skills/`에 복사 |
| **GitHub Copilot, Cursor, OpenCode…** | `npx skills add zaidlemouakni/unscreenshot` |

플랫폼별 메뉴, 폴더, 단계별 안내: [INSTALL](../install/INSTALL.ko.md) (메뉴 이름은 영어로 표기했습니다).

## 60초 만에 써 보기

1. 사용하는 플랫폼에 스킬을 설치합니다(위 참고).
2. [샘플 스크린샷](../../examples/demo/source.png)을 저장하거나, 가지고 있는 슬라이드 이미지를 아무거나 사용합니다.
3. 이미지를 첨부하고 평소 쓰는 언어로 요청합니다:
   > 이 슬라이드를 편집 가능한 PowerPoint로 똑같이 다시 만들어 줘.
4. `.pptx`를 열고 제목을 클릭해 보세요. 그림이 아니라 진짜 텍스트 상자입니다.

비교용 이전/이후 이미지도 함께 받습니다. 이미지가 여러 장이거나 여러 페이지의 PDF라면, 한 파일 안에 각각 한 장씩 슬라이드가 됩니다.

## 당신의 언어로 작동합니다

![슬라이드 한 장에 12가지 문자, 모두 재구성](../../docs/japanese-before-after.png)

아랍어, 페르시아어, 히브리어(오른쪽에서 왼쪽으로 쓰는 언어), 중국어, 일본어, 한국어, 힌디어, 태국어, 베트남어, 러시아어, 그리스어, 그리고 라틴 문자로 쓰는 모든 언어.

- 텍스트는 원래 문자 그대로, 한 글자도 바꾸지 않습니다. 번역은 하지 않습니다.
- 오른쪽에서 왼쪽으로 쓰는 슬라이드는 좌우가 뒤집힌 레이아웃을 그대로 유지합니다. 글머리 기호는 오른쪽에, 로드맵은 왼쪽을 향합니다.
- 문자마다 PowerPoint가 그 문자에 쓰는 글꼴을 지정하고, 크기는 그 문자가 그려지는 방식에 맞춰 측정합니다.

전체 예시: [아랍어](../../examples/arabic) · [일본어](../../examples/japanese) · [슬라이드 한 장에 12가지 문자](../../examples/languages).

## 결과물

![이전: 스크린샷. 이후: 같은 슬라이드를 편집 가능한 PowerPoint로](../../docs/languages-before-after.png)

- **편집 가능한 기본 개체**: 실제 텍스트가 든 텍스트 상자, 진짜 글머리 기호, 사각형, 둥근 카드, 알약 모양, 원, 셰브론 화살표, 선, 그룹. 단어를 바꾸고, 카드 색을 바꾸고, 블록을 옮기세요. 평범한 슬라이드입니다.
- **추측이 아닌 측정**: 위치, 크기, 색상은 픽셀 단위 측정에서 나옵니다. 글꼴 크기는 각 줄의 너비가 이미지와 같아지도록 계산합니다.
- **확인 자료**: 원본 이미지와 재구성한 슬라이드를 나란히 놓은 이미지와, 둘을 겹친 이미지.

## OCR, PDF 변환기, AI 슬라이드 생성기와 무엇이 다른가요?

OCR은 글자를 줄 뿐 슬라이드를 주지는 않습니다. 변환기는 원본 PDF가 있어야 합니다. 생성기는 새 슬라이드를 만듭니다. unscreenshot은 지금 가진 바로 그 슬라이드를 되돌려 줍니다.

| | OCR | PDF 변환기 | AI 슬라이드 생성기 | **unscreenshot** |
|---|:-:|:-:|:-:|:-:|
| 스크린샷이나 사진에서 바로 시작 | ✅ | ❌ | ❌ | ✅ |
| 모든 단어를 그대로 유지 | ✅ | ✅ | ❌ | ✅ |
| 같은 레이아웃, 위치, 크기 | ❌ | ⚠️ | ❌ | ✅ |
| 기본 도형, 카드, 진짜 글머리 기호 | ❌ | ⚠️ | ✅ | ✅ |
| 오른쪽에서 왼쪽 쓰기와 비라틴 문자 | ⚠️ | ⚠️ | ⚠️ | ✅ |

⚠️ 도구와 파일에 따라 다릅니다.

## 작동 방식

어시스턴트(이미지를 볼 수 있는 모든 모델)는 텍스트만 읽습니다. 나머지는 모두 테스트된 작은 Python 스크립트가 처리하므로, 작은 모델이든 큰 모델이든 결과가 같습니다.

1. **분석**: 모든 텍스트 줄, 채워진 도형, 선, 글머리 점, 아이콘을 찾고 기준선, 잉크 너비, 색상을 측정합니다.
2. **읽기**: 모델이 확대된 이미지에서 각 텍스트 줄을 입력하고, 읽은 내용이 이미지와 맞지 않는 줄은 스크립트가 표시합니다.
3. **명세**: 스크립트가 측정값으로 슬라이드 설명을 작성합니다. 도형, 셰브런, 글머리 기호, 글꼴, 크기, 정렬까지 포함합니다.
4. **맞춤**: 문자 체계별로 각 텍스트의 잉크 너비가 이미지와 같아지도록 글꼴 크기를 구합니다.
5. **생성**: 외부 의존성이 없는 생성기가 `.pptx`를 만듭니다(Pillow와 numpy만 필요).
6. **검사**: 슬라이드를 렌더링(LibreOffice 또는 PowerPoint)해 이미지와 비교하고, 최대 세 번까지 수정합니다.

이 저장소의 예시 네 개에서는 한 번 수정한 뒤 모든 텍스트가 원본과 1픽셀 이내로 맞습니다.

## 한계

- **글꼴**: 이미지에 Office에 없는 글꼴(Poppins, Inter, Noto 등)이 쓰였다면, 가장 비슷한 Office 글꼴을 사용합니다. 위치, 크기, 줄 너비는 맞지만 글자 모양은 조금 다릅니다.
- **아이콘, 로고, 사진**은 이미지에서 잘라 내며(배경은 투명하게) 다시 그리지 않습니다.
- **세로쓰기 일본어·중국어**는 이미지로 남겨 둡니다.
- 어시스턴트가 **Python을 실행**(코드 실행)할 수 있어야 합니다. 그렇지 않다면 v2에서 계획 중인 MCP 서버가 필요합니다.

## 자주 묻는 질문

**무료인가요?**\
네. MIT 라이선스이고, 계정도 API 키도 필요 없습니다. 이미 쓰고 있는 어시스턴트 안에서 실행됩니다.

**슬라이드가 내 컴퓨터 밖으로 나가나요?**\
스킬 자체는 네트워크 요청을 전혀 보내지 않습니다. 스크립트는 어시스턴트의 샌드박스나 사용자의 컴퓨터에서 실행됩니다. 이미지는 어시스턴트가 보게 되며, 어시스턴트에게 건네는 다른 파일과 같습니다.

**어떤 어시스턴트에서 쓸 수 있나요?**\
이미지를 볼 수 있고 Python을 실행할 수 있는 어시스턴트라면 됩니다. 설치 표에 있는 것들과, `SKILL.md` 형식을 읽는 다른 어시스턴트도 해당됩니다. 작은 글씨를 읽는 능력은 모델의 시각 성능에 달려 있어, 강한 모델일수록 더 정확히 읽습니다.

**세부 사항이 어긋나면요?**\
스킬이 결과를 렌더링해 원본 이미지와 비교하고 최대 세 번까지 수정합니다. 그런 다음 아직 다른 부분을 알려 줍니다. 모든 요소를 편집할 수 있으므로 마지막 손질은 몇 초면 끝납니다.

**그냥 이미지를 PowerPoint에 붙여 넣으면 안 되나요?**\
그러면 그림일 뿐입니다. 단어 하나 바꿀 수 없고, 숫자를 고치거나 카드를 재사용할 수도 없습니다.

**슬라이드를 다듬거나 번역해 주나요?**\
스스로는 하지 않습니다. 의도된 설계입니다. 이미지에 보이는 그대로, 오타까지 한 글자씩 다시 만듭니다. 진짜 PowerPoint를 얻은 다음에 어시스턴트에게 원하는 변경을 요청하세요.

코드, 테스트, 예시는 영어 README의 [저장소 구성](../../README.md#repository)을 참고하세요. 번역 개선 제안도 환영합니다: [CONTRIBUTING.md](../../CONTRIBUTING.md).

## 라이선스

MIT.

*슬라이드를 손으로 다시 만들 일을 덜어 줬다면 Star를 눌러 주세요.*
