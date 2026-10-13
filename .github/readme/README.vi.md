<p align="center"><img src="../../docs/logo.png" width="120" alt=""></p>

<h1 align="center">unscreenshot</h1>

<p align="center"><b>Hoàn tác ảnh chụp màn hình. Lấy lại slide.</b><br>
Đưa vào ảnh chụp màn hình, nhận về PowerPoint chỉnh sửa được, chính xác đến từng điểm ảnh, với mọi ngôn ngữ.</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.fr.md" title="Français">🇫🇷</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a> ·
  <b title="Tiếng Việt">🇻🇳</b> ·
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

![Ảnh chụp một slide trở thành PowerPoint chỉnh sửa được: mọi chữ, thẻ và màu sắc đều được đo và dựng lại](../../docs/demo.gif)

Bạn chỉ có hình ảnh của một slide: ảnh chụp màn hình trong cuộc họp, một slide do AI tạo ra dưới dạng ảnh, một trang PDF, hay bộ slide ai đó gửi bằng hình. Bạn cần file PowerPoint. Nó đã mất, hoặc chưa từng tồn tại.

`unscreenshot` là một **kỹ năng (skill) cho tác tử AI**: đưa hình ảnh cho trợ lý AI, bạn nhận lại một file `.pptx` trong đó mọi hộp văn bản, gạch đầu dòng, thẻ, đường kẻ và màu sắc đều được đo trên ảnh và dựng lại thành đối tượng PowerPoint gốc, chỉnh sửa được.

## Cài đặt trong 30 giây

Dán đoạn sau vào bất kỳ tác tử nào có thể cài skill (Claude Code, Codex, Gemini CLI, Cursor, Copilot…):

```text
Hãy cài skill unscreenshot từ https://github.com/zaidlemouakni/unscreenshot, làm theo file AGENTS.md của kho mã.
```

Hoặc chọn nền tảng của bạn:

| Nơi bạn dùng AI | Cách cài |
|---|---|
| **Claude** (claude.ai) | Settings > Capabilities: bật thực thi mã, rồi Skills > tải lên [`unscreenshot.zip`](https://github.com/zaidlemouakni/unscreenshot/releases/latest) |
| **ChatGPT** (Business, Enterprise, Edu) | Skills > tải lên cùng file zip |
| **Gemini** (app) | Skills > tải lên cùng file zip |
| **Microsoft Copilot Studio** | Agent > Build > Skills > Upload a skill > chọn file zip |
| **Claude Code** | `claude plugin marketplace add zaidlemouakni/unscreenshot` rồi `claude plugin install unscreenshot@unscreenshot` |
| **Codex** | `codex plugin marketplace add zaidlemouakni/unscreenshot --ref main` rồi `codex plugin add unscreenshot@unscreenshot` |
| **Gemini CLI** | `gemini extensions install https://github.com/zaidlemouakni/unscreenshot` |
| **Mistral Vibe** | sao chép `skills/unscreenshot` vào `~/.vibe/skills/` |
| **GitHub Copilot, Cursor, OpenCode…** | `npx skills add zaidlemouakni/unscreenshot` |

Menu, thư mục và từng nền tảng theo từng bước: [INSTALL](../install/INSTALL.vi.md) (tên menu ghi bằng tiếng Anh).

## Dùng thử trong 60 giây

1. Cài kỹ năng cho nền tảng của bạn (ở trên).
2. Lưu [ảnh chụp mẫu](../../examples/demo/source.png), hoặc dùng bất kỳ ảnh slide nào bạn có.
3. Đính kèm ảnh và yêu cầu, bằng ngôn ngữ của bạn:
   > Hãy dựng lại slide này thành PowerPoint chỉnh sửa được, giống hệt bản gốc.
4. Mở file `.pptx` và nhấp vào tiêu đề: đó là một hộp văn bản thật, không phải ảnh.

Bạn cũng nhận được một ảnh so sánh trước/sau. Nhiều hình ảnh, hoặc một file PDF nhiều trang, sẽ thành mỗi trang một slide trong cùng một file.

## Dùng được với ngôn ngữ của bạn

![Mười hai hệ chữ trên một slide, đều được dựng lại](../../docs/languages-before-after.png)

Tiếng Ả Rập, tiếng Ba Tư và tiếng Do Thái (viết từ phải sang trái), tiếng Trung, tiếng Nhật, tiếng Hàn, tiếng Hindi, tiếng Thái, tiếng Việt, tiếng Nga, tiếng Hy Lạp và mọi ngôn ngữ dùng chữ Latinh.

- Văn bản được giữ nguyên từng chữ, trong hệ chữ gốc. Không dịch gì cả.
- Slide viết từ phải sang trái giữ nguyên bố cục đối xứng: gạch đầu dòng ở bên phải, lộ trình hướng sang trái.
- Mỗi hệ chữ dùng đúng phông chữ mà PowerPoint dùng cho nó, và cỡ chữ được đo theo cách hệ chữ đó được vẽ.

Ví dụ đầy đủ: [tiếng Ả Rập](../../examples/arabic) · [tiếng Nhật](../../examples/japanese) · [mười hai hệ chữ trên một slide](../../examples/languages).

## Bạn nhận được gì

![Trước: ảnh chụp màn hình. Sau: cùng slide đó dưới dạng PowerPoint chỉnh sửa được](../../docs/demo-before-after.png)

- **Đối tượng gốc, chỉnh sửa được**: hộp văn bản chứa chữ thật, gạch đầu dòng thật, hình chữ nhật, thẻ bo góc, hình viên thuốc, hình tròn, mũi tên chevron, đường kẻ, nhóm. Đổi một từ, đổi màu một thẻ, di chuyển một khối: đó là một slide bình thường.
- **Đo đạc, không phỏng đoán**: vị trí, kích thước và màu sắc đến từ phép đo từng điểm ảnh. Cỡ chữ được tính để mỗi dòng có cùng độ rộng như trên ảnh.
- **Có bằng chứng**: hình ảnh gốc và slide dựng lại đặt cạnh nhau, cùng ảnh chồng lớp của hai bản.

## Sao không dùng OCR, công cụ chuyển PDF hay công cụ tạo slide bằng AI?

OCR cho bạn chữ, không phải slide. Công cụ chuyển đổi cần file PDF gốc. Công cụ tạo slide làm ra một slide mới. unscreenshot trả lại cho bạn chính slide bạn đang có.

| | OCR | Công cụ chuyển PDF | Công cụ tạo slide bằng AI | **unscreenshot** |
|---|:-:|:-:|:-:|:-:|
| Bắt đầu từ ảnh chụp màn hình hoặc ảnh chụp | ✅ | ❌ | ❌ | ✅ |
| Giữ nguyên từng chữ | ✅ | ✅ | ❌ | ✅ |
| Cùng bố cục, vị trí và kích thước | ❌ | ⚠️ | ❌ | ✅ |
| Hình khối gốc, thẻ và gạch đầu dòng thật | ❌ | ⚠️ | ✅ | ✅ |
| Chữ viết từ phải sang trái và chữ không phải Latinh | ⚠️ | ⚠️ | ⚠️ | ✅ |

⚠️ tùy công cụ và tùy file.

## Cách hoạt động

Trợ lý (bất kỳ mô hình nào xem được ảnh) chỉ đọc chữ. Mọi việc còn lại do các script Python nhỏ, đã được kiểm thử, đảm nhận, nên kết quả như nhau dù dùng mô hình nhỏ hay lớn.

1. **Phân tích**: tìm mọi dòng chữ, hình tô màu, đường kẻ, chấm đầu dòng và biểu tượng; đo đường cơ sở, độ rộng nét mực và màu sắc.
2. **Đọc**: mô hình gõ lại từng dòng chữ từ ảnh phóng to; các script đánh dấu dòng nào đọc không khớp với ảnh.
3. **Mô tả**: các script viết mô tả slide từ số đo: hình khối, mũi tên chevron, gạch đầu dòng, phông chữ, cỡ chữ, căn lề.
4. **Khớp cỡ chữ**: cỡ chữ được tính sao cho độ rộng nét mực của mỗi đoạn văn bản khớp với ảnh, theo từng hệ chữ.
5. **Dựng**: một bộ tạo không phụ thuộc thư viện ngoài xuất ra file `.pptx` (chỉ cần Pillow và numpy).
6. **Kiểm tra**: slide được kết xuất (LibreOffice hoặc PowerPoint), so sánh với ảnh và sửa lại, tối đa ba vòng.

Trên bốn ví dụ của kho mã này, sau một lần sửa, mọi đoạn văn bản đều lệch không quá 1 điểm ảnh so với bản gốc.

## Giới hạn

- **Phông chữ**: nếu ảnh dùng phông không có trong Office (Poppins, Inter, Noto…), phông Office gần giống nhất sẽ được dùng. Vị trí, cỡ chữ và độ rộng dòng vẫn khớp; hình dáng chữ hơi khác một chút.
- **Biểu tượng, logo, ảnh chụp** được cắt từ ảnh gốc (nền được làm trong suốt), không vẽ lại.
- **Chữ Nhật hoặc chữ Trung viết dọc** được giữ dưới dạng ảnh.
- Trợ lý của bạn cần **chạy được Python** (thực thi mã). Nếu không, sẽ cần đến máy chủ MCP dự kiến trong phiên bản v2.

## Câu hỏi thường gặp

**Có miễn phí không?**\
Có: giấy phép MIT, không cần tài khoản hay khóa API. Kỹ năng chạy ngay trong trợ lý AI bạn đang dùng.

**Slide của tôi có rời khỏi máy không?**\
Bản thân kỹ năng không thực hiện bất kỳ kết nối mạng nào: các script chạy trong môi trường cô lập của trợ lý hoặc trên máy của bạn. Trợ lý sẽ thấy ảnh, giống như mọi file bạn gửi cho nó.

**Dùng được với những trợ lý nào?**\
Mọi trợ lý xem được ảnh và chạy được Python: các trợ lý trong bảng cài đặt, và những trợ lý khác đọc được định dạng `SKILL.md`. Việc đọc chữ nhỏ phụ thuộc vào khả năng thị giác của mô hình: mô hình càng mạnh thì đọc càng chuẩn.

**Nếu có chi tiết bị lệch thì sao?**\
Kỹ năng kết xuất kết quả, so sánh với ảnh của bạn và sửa lại, tối đa ba lượt. Sau đó nó cho bạn biết những gì vẫn còn khác. Mọi thứ đều chỉnh sửa được, nên lần chỉnh cuối chỉ mất vài giây.

**Sao không dán ảnh thẳng vào PowerPoint?**\
Khi đó nó chỉ là một bức ảnh: bạn không sửa được một chữ, một con số, cũng không dùng lại được một thẻ nào.

**Kỹ năng có làm đẹp hay dịch slide không?**\
Không tự làm, và đó là chủ ý: kỹ năng dựng lại đúng những gì có trong ảnh, từng chữ một, kể cả lỗi chính tả. Khi đã có PowerPoint thật, bạn cứ nhờ trợ lý chỉnh sửa theo ý mình.

Mã nguồn, kiểm thử và ví dụ: xem [bảng cấu trúc kho mã](../../README.md#repository) trong README tiếng Anh. Rất hoan nghênh góp ý cho bản dịch: [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Giấy phép

MIT.

*Hãy tặng một ngôi sao nếu nó giúp bạn khỏi phải làm lại slide bằng tay.*
