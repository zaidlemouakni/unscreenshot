# التثبيت

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · **العربية**

<div dir="rtl">

المهارة هي المجلد [`skills/unscreenshot/`](../../skills/unscreenshot). تأخذها تطبيقات الدردشة كملف zip، ويأخذ وكلاء البرمجة المجلد نفسه (أو إضافة تشير إليه). نزّل ملف zip من [أحدث إصدار](https://github.com/zaidlemouakni/unscreenshot/releases/latest): `unscreenshot.zip` (المجلد في جذر ملف zip). أما `unscreenshot-flat.zip` فيضع `SKILL.md` في الجذر، للمنصات التي ترفض الأول.

شرط في كل مكان: يجب أن يستطيع المساعد **تشغيل Python** (تنفيذ الشيفرة / مفسّر الشيفرة). تحتاج السكربتات إلى Pillow وnumpy، وهما متوفران في كل البيئات المعزولة الشائعة.

أسماء القوائم مكتوبة كما تظهر في الواجهة الإنجليزية، وقد تظهر في واجهتك مترجمة. إذا لم يطابق مسارٌ ما شاشتك، فابحث عن «Skills» في الإعدادات أو الشريط الجانبي.

## تطبيقات الدردشة

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: فعّل **Code execution and file creation**.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. في المحادثة: أرفق الصورة واطلب إعادة بناء الشريحة.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. يجب تفعيل Skills في مساحة عملك (إعداد يملكه المسؤول في خطط الشركات).
2. افتح **Skills**، وأنشئ مهارة أو ارفعها، ثم ارفع `unscreenshot.zip`.
3. في المحادثة: أرفق الصورة. تظهر الملفات المُنشأة في المحادثة للتنزيل.

### Gemini (app)
1. افتح **Skills** (حلّت محل Gems منذ سبتمبر 2026).
2. أنشئ مهارة من ملف وارفع `unscreenshot.zip`.

### Microsoft Copilot Studio
1. متطلبات المسؤول: اسمح بمزوّد النماذج الذي تريده (لنماذج Claude: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic، والسماح بالنماذج الخارجية في Power Platform admin center).
2. أنشئ وكيلًا باستخدام **new experience** (بيئة GitHub Copilot): يشغّل Python في بيئة معزولة ويعيد ملفات PowerPoint. لا يمكن تغيير البيئة لاحقًا.
3. تبويب **Build** > Model: نموذج رؤية قوي (مثل Claude Opus أو GPT-5.5).
4. **Build** > Instructions: الصق النص أدناه.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. اختبر في **Preview** بصورة، ثم انشر عبر **Publish** إلى Teams + Microsoft 365 وشارك عبر **Share**.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## وكلاء البرمجة وسطر الأوامر

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
أو انسخ المجلد: `cp -R skills/unscreenshot ~/.codex/skills/`.

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
داخل مشروع فقط: `.vibe/skills/` أو `.agents/skills/` (المجلدات الموثوقة فقط).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
أو: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
أو انسخ `skills/unscreenshot` إلى `~/.cursor/skills/`.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### أي وكيل آخر يدعم المهارات
```bash
npx skills add zaidlemouakni/unscreenshot
```
أو انسخ `skills/unscreenshot` إلى مجلد مهارات الوكيل (غالبًا `~/.agents/skills/`).

## التحقق من أن كل شيء يعمل

شغّل العرض التوضيحي من نسخة مستنسخة من المستودع:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```

</div>
