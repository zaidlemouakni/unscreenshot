# نصب

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · **فارسی** · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

<div dir="rtl">

مهارت همان پوشهٔ [`skills/unscreenshot/`](../../skills/unscreenshot) است. اپلیکیشن‌های گفت‌وگو آن را به‌صورت فایل zip می‌گیرند و عامل‌های برنامه‌نویسی خود پوشه را (یا افزونه‌ای که به آن اشاره می‌کند). فایل zip را از [آخرین انتشار](https://github.com/zaidlemouakni/unscreenshot/releases/latest) بگیرید: `unscreenshot.zip` (پوشه در ریشهٔ zip). در `unscreenshot-flat.zip` فایل `SKILL.md` در ریشه است، برای پلتفرم‌هایی که اولی را نمی‌پذیرند.

پیش‌نیاز همه‌جا: دستیار باید بتواند **Python اجرا کند** (اجرای کد / مفسر کد). اسکریپت‌ها به Pillow و numpy نیاز دارند که در همهٔ محیط‌های ایزولهٔ رایج وجود دارند.

نام منوها مطابق رابط انگلیسی نوشته شده است؛ رابط شما ممکن است آن‌ها را ترجمه‌شده نشان دهد. اگر مسیری با صفحهٔ شما جور نبود، در تنظیمات یا نوار کناری دنبال «Skills» بگردید.

## اپلیکیشن‌های گفت‌وگو

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: گزینهٔ **Code execution and file creation** را روشن کنید.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. در گفت‌وگو: تصویر را پیوست کنید و بخواهید اسلاید را دوباره بسازد.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. Skills باید در فضای کاری شما فعال باشد (تنظیمی مدیریتی در طرح‌های سازمانی).
2. **Skills** را باز کنید، مهارتی بسازید/بارگذاری کنید و `unscreenshot.zip` را بارگذاری کنید.
3. در گفت‌وگو: تصویر را پیوست کنید. فایل‌های ساخته‌شده برای دانلود در گفت‌وگو ظاهر می‌شوند.

### Gemini (app)
1. **Skills** را باز کنید (از سپتامبر ۲۰۲۶ جای Gems را گرفته‌اند).
2. از یک فایل مهارت بسازید و `unscreenshot.zip` را بارگذاری کنید.

### Microsoft Copilot Studio
1. پیش‌نیاز مدیریتی: ارائه‌دهندهٔ مدل مورد نظر را مجاز کنید (برای مدل‌های Claude: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic، و مدل‌های خارجی در Power Platform admin center).
2. یک عامل با **new experience** (محیط GitHub Copilot) بسازید: Python را در محیط ایزوله اجرا می‌کند و فایل پاورپوینت برمی‌گرداند. این محیط بعداً قابل تغییر نیست.
3. زبانهٔ **Build** > Model: یک مدل بینایی قوی (مثلاً Claude Opus یا GPT-5.5).
4. **Build** > Instructions: متن زیر را بچسبانید.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. در **Preview** با یک تصویر آزمایش کنید، سپس در Teams + Microsoft 365 **Publish** و **Share** کنید.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## عامل‌های برنامه‌نویسی و خط فرمان

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
یا پوشه را کپی کنید: `cp -R skills/unscreenshot ~/.codex/skills/`.

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
فقط برای یک پروژه: `.vibe/skills/` یا `.agents/skills/` (فقط پوشه‌های مورد اعتماد).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
یا: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
یا `skills/unscreenshot` را در `~/.cursor/skills/` کپی کنید.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### هر عامل دیگری که از مهارت‌ها پشتیبانی می‌کند
```bash
npx skills add zaidlemouakni/unscreenshot
```
یا `skills/unscreenshot` را در پوشهٔ مهارت‌های عامل (اغلب `~/.agents/skills/`) کپی کنید.

## بررسی درستی کار

نسخهٔ نمایشی را از یک کلون مخزن اجرا کنید:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```

</div>
