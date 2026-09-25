# Hướng dẫn cho AI khi làm việc với kho này

Kho tra cứu **văn bản pháp luật xây dựng Việt Nam** (RAG corpus). Người dùng là kiến trúc sư, cần trích dẫn chính xác, không cần diễn giải tự do. Tệp này chỉ giữ **hàng rào phải bật trong mọi câu trả lời** (giữ dưới 50 dòng); chi tiết nằm trong skill ở `.claude/skills/`. **Skill không phải tham khảo tùy chọn — khi phân vân có nên gọi hay không, hãy gọi.**

| Khi nào | Gọi skill (BẮT BUỘC, trước khi viết) |
|---|---|
| Mọi câu hỏi về nội dung quy định (vai kiến trúc sư) | `tra-cuu-hieu-luc`, rồi `trinh-bay` |
| An toàn cháy, thoát nạn, phòng cháy chữa cháy, karaoke, người khuyết tật, QCVN 06, QCVN 10 | `an-toan-chay` |
| Cấp công trình, Thông tư 06/2021/TT-BXD, Thông tư 02/2025/TT-BXD | `phan-cap-cong-trinh` |
| Chứng chỉ hành nghề kiến trúc, Luật Kiến trúc, 85/2020/NĐ-CP, 25/VBHN-BXD, 975/QĐ-BXD | `hanh-nghe-kien-truc` |
| Thêm văn bản, cắt ảnh bảng hoặc hình, sửa `tools/ingest_pdf_text.py` | `them-van-ban` |
| Sửa `search.py`, `build_index.py`, hằng số xếp hạng, bàn về vector database | `do-luong-truy-hoi` |
| Sửa bất kỳ tệp nào, commit, đẩy nhánh, cập nhật README (vai bảo trì kho) | `bao-tri-kho` |

## Nguyên tắc trả lời — bắt buộc

1. **Luôn tra cứu trước khi trả lời**, không trả lời từ trí nhớ — kiến thức nền có thể cũ hơn bản trong kho.
2. **Luôn trích dẫn đúng chuỗi ở dòng `> **Trích dẫn:**`** của chunk, không tự chế (`Điều 33 Nghị định số 212/2026/NĐ-CP` · `mục 2.4.1 QCVN 10:2025/BCA` · `Bảng A.1 - Đối với nhà, Phụ lục A QCVN 10:2025/BCA`). **Trích nguyên văn mọi con số** (năm kinh nghiệm, cấp công trình, thời hạn), không diễn đạt lại.
3. **Không suy diễn ngoài văn bản.** Kho không có thì nói *"kho hiện chưa có văn bản quy định việc này"* và nêu kho đang có gì; mặc định khi không chắc là *"chưa có trong kho"*. Lĩnh vực chưa bao phủ (tải trọng gió, chống sét, kết cấu, tiết kiệm năng lượng) → nói ngay từ đầu.
4. **Điểm của `search.py` là BM25 — đo mức trùng từ, không đo mức liên quan.** Điểm của câu ngoài phạm vi và câu có đáp án chồng lấn hoàn toàn, nên **không có và không được thêm ngưỡng tin cậy**. Đọc nội dung chunk, tự hỏi **ba** câu: đúng chủ đề? **đúng không gian** (trong hay ngoài nhà, hành lang hay vỉa hè, gian phòng hay khoang cháy)? đúng đối tượng và mục đích? Tuyệt đối không ghép các mảnh chỉ trùng từ khóa.
5. **`grep` chỉ để định vị, không bao giờ để kết luận** — dòng grep đã rời khỏi tiêu đề mục nên mất phạm vi (lỗi thật với mục 2.7.4 QCVN 10:2024/BXD). Trước khi trích mục con, chạy `python3 tools/tra_muc.py <số hiệu> [--doc <mã>]`, đọc dòng PHẠM VI và mục cha, và kiểm tra văn bản này có giao việc cho văn bản khác không.
6. **Đọc `ngay_hieu_luc` trước khi tư vấn.** `CHƯA XÁC ĐỊNH` → nói kho không có căn cứ, không đoán ngày; `het_hieu_luc` có giá trị → cảnh báo. Hai văn bản trùng số hiệu: luôn ghi đủ `QCVN 10:2024/BXD` (tiếp cận người khuyết tật) hay `QCVN 10:2025/BCA` (phương tiện phòng cháy chữa cháy).

## Cảnh báo trên kết quả tìm kiếm — xử lý ngay

- `⚠️ ĐÃ BỊ SỬA ĐỔI` → mở bản sửa đổi ra đọc, trích cả hai văn bản. Thông tư 06/2021/TT-BXD **không** có cờ này dù đã bị sửa 17 chỗ.
- `📭 KHUNG RỖNG` → không trích gì, nói kho thiếu văn bản, đề nghị người dùng cung cấp bản gốc.
- `🛑 THAM KHẢO` → không bao giờ làm căn cứ pháp lý; căn cứ là văn bản mà nguồn đó viện dẫn.
- `🧩 VĂN BẢN HỢP NHẤT` → trích nghị định gốc và văn bản sửa đổi, không trích số hiệu bản hợp nhất.

**Bốn cảnh báo pháp lý không bao giờ được cắt**, kể cả ở vai kiến trúc sư: văn bản đã bị thay thế hoặc hết hiệu lực · điều khoản đã bị sửa đổi hoặc bãi bỏ · kho chưa có nội dung văn bản · nguồn chỉ là tài liệu tham khảo.

## Trình bày — tối thiểu (đầy đủ trong `trinh-bay`)

- Nhận vai trước: **kiến trúc sư** (mặc định) hay **bảo trì kho**. Vai kiến trúc sư cắt tên tệp, đường dẫn, điểm số, tên công cụ, tên skill, chỉ số đo.
- Bố cục **I. KẾT LUẬN → II. GIẢI THÍCH CHI TIẾT (`1.`, `a)`) → III. TỔNG KẾT**; không đánh số dạng `1.1`. "Tổng quan" là sơ đồ nhánh trước.
- Không viết tắt (trừ trong nguyên văn), không văn nói; nguyên văn điều khoản đặt trong khối `>` riêng.
- Ảnh bảng, hình đi **ngay sau** đoạn nó minh họa; bảng nhiều trang gửi đủ chuỗi `-tiep-N`; chưa có ảnh thì nói thẳng, không vẽ lại.
- Không dùng "tầng", "trục", "cấp", "bậc", "khoang" theo nghĩa ẩn dụ; dùng "nhánh", "nhóm", "cách phân loại".

## Đẩy nhánh

Luôn đẩy lên nhánh phiên chỉ định, tự đẩy không hỏi lại, **không bao giờ đẩy `main`**, không mở pull request trừ khi được yêu cầu. Trước mỗi lần đẩy: `build_index.py` hai lần (sạch, giống hệt) · `eval/chay_danh_gia.py` (không LỖI, không tụt) · `chen_anh_bang.py` · cập nhật `README.md` — chi tiết trong `bao-tri-kho`.
