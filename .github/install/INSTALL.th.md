# การติดตั้ง

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · [Tiếng Việt](INSTALL.vi.md) · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · **ไทย** · [العربية](INSTALL.ar.md)

สกิลคือโฟลเดอร์ [`skills/unscreenshot/`](../../skills/unscreenshot) แอปแชตรับสกิลเป็นไฟล์ zip ส่วนเอเจนต์เขียนโค้ดรับเป็นโฟลเดอร์ (หรือปลั๊กอิน/ส่วนขยายที่ชี้ไปยังโฟลเดอร์นั้น) ดาวน์โหลด zip ได้จาก[รุ่นล่าสุด](https://github.com/zaidlemouakni/unscreenshot/releases/latest): `unscreenshot.zip` (โฟลเดอร์อยู่ที่รากของ zip) ส่วน `unscreenshot-flat.zip` จะวาง `SKILL.md` ไว้ที่ราก สำหรับแพลตฟอร์มที่ไม่รับแบบแรก

ข้อกำหนดทุกแพลตฟอร์ม: ผู้ช่วยต้อง**รัน Python ได้** (การรันโค้ด / ตัวแปลโค้ด) สคริปต์ต้องใช้ Pillow และ numpy ซึ่งมีอยู่แล้วในแซนด์บ็อกซ์หลักทุกตัว

ชื่อเมนูเขียนตามหน้าจอภาษาอังกฤษ หน้าจอของคุณอาจแสดงเป็นคำแปล หากเส้นทางไม่ตรงกับหน้าจอ ให้มองหา "Skills" ในการตั้งค่าหรือแถบด้านข้าง

## แอปแชต

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: เปิด **Code execution and file creation**
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`
3. ในแชต: แนบภาพแล้วขอให้สร้างสไลด์ใหม่

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. เวิร์กสเปซของคุณต้องเปิดใช้ Skills (เป็นการตั้งค่าของผู้ดูแลในแผนธุรกิจ)
2. เปิด **Skills** สร้าง/อัปโหลดสกิล แล้วอัปโหลด `unscreenshot.zip`
3. ในแชต: แนบภาพ ไฟล์ที่สร้างขึ้นจะแสดงในแชตให้ดาวน์โหลด

### Gemini (app)
1. เปิด **Skills** (ใช้แทน Gems ตั้งแต่เดือนกันยายน 2026)
2. สร้างสกิลจากไฟล์และอัปโหลด `unscreenshot.zip`

### Microsoft Copilot Studio
1. สิ่งที่ผู้ดูแลต้องตั้งค่า: อนุญาตผู้ให้บริการโมเดลที่ต้องการ (สำหรับโมเดล Claude: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic และอนุญาตโมเดลภายนอกใน Power Platform admin center)
2. สร้างเอเจนต์ด้วย **new experience** (สภาพแวดล้อม GitHub Copilot) ซึ่งรัน Python ในแซนด์บ็อกซ์และส่งไฟล์ PowerPoint กลับมาได้ เปลี่ยนสภาพแวดล้อมภายหลังไม่ได้
3. แท็บ **Build** > Model: เลือกโมเดลด้านภาพที่มีความสามารถสูง (เช่น Claude Opus หรือ GPT-5.5)
4. **Build** > Instructions: วางข้อความด้านล่าง
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`
6. ทดสอบใน **Preview** ด้วยภาพหนึ่งภาพ จากนั้น **Publish** ไปยัง Teams + Microsoft 365 แล้ว **Share**

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## เอเจนต์เขียนโค้ดและบรรทัดคำสั่ง

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
หรือคัดลอกโฟลเดอร์: `cp -R skills/unscreenshot ~/.codex/skills/`

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
เฉพาะโปรเจกต์: `.vibe/skills/` หรือ `.agents/skills/` (เฉพาะโฟลเดอร์ที่เชื่อถือแล้ว)

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
หรือ: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
หรือคัดลอก `skills/unscreenshot` ไปไว้ใน `~/.cursor/skills/`

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### เอเจนต์อื่น ๆ ที่รองรับสกิล
```bash
npx skills add zaidlemouakni/unscreenshot
```
หรือคัดลอก `skills/unscreenshot` ไปไว้ในโฟลเดอร์สกิลของเอเจนต์ (มักเป็น `~/.agents/skills/`)

## ตรวจสอบว่าใช้งานได้

รันเดโมจากรีโพที่โคลนมา:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
