# Cài đặt

[English](../../INSTALL.md) · [Français](INSTALL.fr.md) · [简体中文](INSTALL.zh-CN.md) · [Español](INSTALL.es.md) · [Português](INSTALL.pt-BR.md) · [日本語](INSTALL.ja.md) · **Tiếng Việt** · [한국어](INSTALL.ko.md) · [فارسی](INSTALL.fa.md) · [ไทย](INSTALL.th.md) · [العربية](INSTALL.ar.md)

Skill chính là thư mục [`skills/unscreenshot/`](../../skills/unscreenshot). Ứng dụng chat nhận nó dưới dạng file zip; tác tử lập trình nhận thư mục (hoặc plugin/tiện ích mở rộng trỏ tới thư mục đó). Tải file zip từ [bản phát hành mới nhất](https://github.com/zaidlemouakni/unscreenshot/releases/latest): `unscreenshot.zip` (thư mục nằm ở gốc file zip). `unscreenshot-flat.zip` đặt `SKILL.md` ở gốc, dành cho các nền tảng không nhận bản đầu.

Yêu cầu chung: trợ lý phải **chạy được Python** (thực thi mã / trình thông dịch mã). Các script cần Pillow và numpy, vốn có sẵn trong mọi môi trường cô lập phổ biến.

Tên menu được ghi bằng tiếng Anh như trên giao diện tiếng Anh; giao diện của bạn có thể hiển thị bản dịch. Nếu đường dẫn không khớp với màn hình, hãy tìm "Skills" trong phần cài đặt hoặc thanh bên.

## Ứng dụng chat

### Claude (claude.ai, desktop, mobile)
1. Settings > Capabilities: bật **Code execution and file creation**.
2. Settings > Capabilities > **Skills** > Upload skill > `unscreenshot.zip`.
3. Trong cuộc trò chuyện: đính kèm hình ảnh và yêu cầu dựng lại slide.

### ChatGPT (Business, Enterprise, Edu, Healthcare)
1. Không gian làm việc của bạn phải bật Skills (một thiết lập của quản trị viên trong các gói doanh nghiệp).
2. Mở **Skills**, tạo/tải lên một skill rồi tải lên `unscreenshot.zip`.
3. Trong cuộc trò chuyện: đính kèm hình ảnh. Các file được tạo sẽ xuất hiện trong cuộc trò chuyện để tải về.

### Gemini (app)
1. Mở **Skills** (thay thế Gems từ tháng 9 năm 2026).
2. Tạo skill từ một file và tải lên `unscreenshot.zip`.

### Microsoft Copilot Studio
1. Điều kiện từ quản trị viên: cho phép nhà cung cấp mô hình bạn muốn dùng (với mô hình Claude: Microsoft 365 admin center > Copilot > Settings > *AI providers operating as Microsoft subprocessors* > Anthropic, và cho phép mô hình bên ngoài trong Power Platform admin center).
2. Tạo tác tử bằng **new experience** (môi trường GitHub Copilot): nó chạy Python trong môi trường cô lập và trả về file PowerPoint. Không thể đổi môi trường này về sau.
3. Thẻ **Build** > Model: chọn một mô hình thị giác mạnh (ví dụ Claude Opus hoặc GPT-5.5).
4. **Build** > Instructions: dán khối văn bản bên dưới.
5. **Build** > Skills > Add skill > **Upload a skill** > `unscreenshot.zip`.
6. Thử trong **Preview** với một hình ảnh, sau đó **Publish** lên Teams + Microsoft 365 và **Share**.

```text
You rebuild slides. The user attaches an image of a slide (screenshot, PNG, JPG, PDF page); you return an
editable PowerPoint (.pptx) identical to it. Always use the unscreenshot skill and follow its SKILL.md
exactly. Keep every text verbatim. Deliver the .pptx, the side-by-side comparison image and a three-line
summary (fonts used, elements kept as images, remaining differences), in the user's language. If the user
asks for anything else, say you only rebuild slides from images.
```

## Tác tử lập trình và dòng lệnh

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
Hoặc sao chép thư mục: `cp -R skills/unscreenshot ~/.codex/skills/`.

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
Chỉ trong một dự án: `.vibe/skills/` hoặc `.agents/skills/` (chỉ với thư mục tin cậy).

### Qwen Code
```bash
qwen extensions install zaidlemouakni/unscreenshot
```

### GitHub Copilot (VS Code, Copilot CLI)
```bash
npx skills add zaidlemouakni/unscreenshot -a github-copilot -g
```
Hoặc: `git clone https://github.com/zaidlemouakni/unscreenshot && mkdir -p ~/.copilot/skills && cp -R unscreenshot/skills/unscreenshot ~/.copilot/skills/`

### Cursor
```bash
npx skills add zaidlemouakni/unscreenshot -a cursor -y
```
Hoặc sao chép `skills/unscreenshot` vào `~/.cursor/skills/`.

### OpenCode
```bash
npx skills add zaidlemouakni/unscreenshot -a opencode -y
```

### Mọi tác tử khác hỗ trợ skill
```bash
npx skills add zaidlemouakni/unscreenshot
```
Hoặc sao chép `skills/unscreenshot` vào thư mục skill của tác tử (thường là `~/.agents/skills/`).

## Kiểm tra hoạt động

Chạy bản demo từ một bản sao (clone) của kho mã:
```bash
python skills/unscreenshot/scripts/analyze.py examples/demo/source.png --out examples/demo/work
python skills/unscreenshot/scripts/fit.py examples/demo/spec.json
python skills/unscreenshot/scripts/build_pptx.py examples/demo/spec.fitted.json --out examples/demo/out/demo.pptx
python skills/unscreenshot/scripts/check.py examples/demo/out/demo.pptx examples/demo/spec.fitted.json
```
