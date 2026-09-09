# Hướng dẫn cho AI khi làm việc với kho này

Đây là **kho tra cứu văn bản pháp luật xây dựng Việt Nam** (RAG corpus).
Người dùng là kiến trúc sư, cần trích dẫn chính xác chứ không cần diễn giải tự do.

## Nguyên tắc trả lời — bắt buộc

1. **Luôn tra cứu trước khi trả lời.** Đừng trả lời từ trí nhớ. Nội dung ở đây
   là bản chính thức của người dùng; kiến thức nền của bạn có thể đã cũ.
2. **Luôn trích dẫn.** Mỗi loại văn bản có dạng trích dẫn riêng:
   - Nghị định, Luật, Thông tư → `Điều 33 Nghị định số 212/2026/NĐ-CP`
   - Quy chuẩn, Tiêu chuẩn → `mục 2.4.1 QCVN 10:2025/BCA`
   - Bảng tra cứu → `Bảng A.1 - Đối với nhà, Phụ lục A QCVN 10:2025/BCA`

   Mỗi file chunk có sẵn dòng `> **Trích dẫn:**` — dùng đúng chuỗi đó, đừng tự chế.
3. **Không suy diễn ngoài văn bản.** Nếu kho không có câu trả lời, hãy nói
   "kho hiện chưa có văn bản quy định việc này" thay vì đoán.
4. **Trích nguyên văn khi nội dung mang tính định lượng** (số năm kinh nghiệm,
   cấp công trình, thời hạn ngày làm việc). Đừng diễn đạt lại các con số.
5. **Kiểm tra hiệu lực.** Xem `ngay_ban_hanh` và điều/mục về hiệu lực thi hành.
   - **NĐ 212/2026/NĐ-CP**: hiệu lực **01/7/2026**, thay thế NĐ 111/2024/NĐ-CP.
     Điều 55 có các điều khoản chuyển tiếp — đọc Điều 55 trước khi tư vấn cho
     hồ sơ nộp trước thời điểm đó.
   - **QCVN 10:2025/BCA**: bản Quy chuẩn **không có** điều khoản hiệu lực hay
     chuyển tiếp; nội dung đó nằm trong Thông tư 103/2025/TT-BCA — văn bản này
     **chưa có trong kho**. Khi được hỏi về ngày hiệu lực hoặc quy định chuyển
     tiếp của QCVN 10, phải nói rõ là kho chưa có, tuyệt đối không suy đoán.

6. **Tra đúng bảng khi hỏi về PCCC.** Theo mục 1.5.9 QCVN 10:2025/BCA, xác định
   yêu cầu trang bị theo thứ tự: **Bảng A.1** (toàn nhà) → **Bảng A.2**
   (hạng mục/khu vực) → **Bảng A.3** (gian phòng) → **Bảng A.4** (thiết bị).
   Luôn kiểm tra thêm mục 1.5.11 về các khu vực KHÔNG phải trang bị.

## Cách tra cứu

Ưu tiên theo thứ tự:

```bash
# 1. Tìm theo từ khóa (nhanh nhất, đã đủ cho hầu hết câu hỏi)
python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề hạng II"
python3 tools/search.py --k 3 --full --json "thu hồi giấy phép nhà thầu nước ngoài"

# 2. Đọc thẳng một Điều / mục / bảng đã biết
cat chunks/212-2026-nd-cp/dieu-33-*.md
cat chunks/qcvn-10-2025-bca/muc-2-4-*.md
cat chunks/qcvn-10-2025-bca/phu-luc-a-01-*.md      # Bảng A.1

# 3. Duyệt mục lục
cat corpus/nghi-dinh/212-2026-nd-cp/muc-luc.md
```

`index/chunks.jsonl` chứa toàn bộ chunk kèm metadata — dùng khi cần lọc/duyệt
bằng script. `index/documents.json` là sổ đăng ký văn bản.

## Cấu trúc kho

```
corpus/     Bản gốc do người dùng sở hữu — CHỈ sửa ở đây
chunks/     Sinh tự động từ corpus/ — KHÔNG sửa tay
index/      Sinh tự động — KHÔNG sửa tay
tools/      Script xử lý
docs/       Hướng dẫn cho người dùng
```

Sau **bất kỳ** thay đổi nào trong `corpus/`, phải chạy lại:

```bash
python3 tools/build_index.py
```

## Khi thêm văn bản mới

1. `python3 tools/ingest_pdf.py <file.pdf> --ten <ma-van-ban>`
2. Đọc từng ảnh trang bằng **thị giác máy** và chép lại thành Markdown.
   **Không** dán thẳng kết quả OCR vào corpus — Tesseract đánh rơi dấu tiếng
   Việt ("thẩm quyền" → "thâm quyên"), với văn bản pháp luật là sai nghĩa.
   OCR chỉ dùng để đối chiếu.
3. Lưu vào `corpus/<loại>/<mã>/toan-van.md` với front matter đầy đủ
   (xem `corpus/nghi-dinh/212-2026-nd-cp/toan-van.md` làm mẫu).
4. Giữ đúng quy ước tiêu đề để bộ chia chunk nhận diện được. Khai báo
   `cau_truc` trong front matter để chọn kiểu cắt:
   - `cau_truc: "dieu"` (mặc định — Nghị định, Luật, Thông tư):
     `## Chương I. TÊN` · `### Mục 1. TÊN` · `### Điều 1. Tên điều`
   - `cau_truc: "muc"` (Quy chuẩn, Tiêu chuẩn):
     `## 1 TÊN PHẦN` · `### 1.1 Tên mục`
   - Phụ lục: khai báo `chia_theo` (`"Mẫu số"`, `"Bảng"`, `"H."`) để cắt theo
     tiêu đề cấp 2; không khai báo thì giữ nguyên cả phụ lục làm một chunk.
5. **Nếu văn bản có hình vẽ, sơ đồ, biểu đồ** — làm cả hai việc, đừng bỏ việc nào:
   - Chép phần **CHÚ DẪN** thành chữ. Với văn bản kỹ thuật, hầu hết thông số bắt
     buộc nằm ở chú dẫn chứ không nằm trong nét vẽ. Không có chữ thì
     `tools/search.py` không tìm ra được — với công cụ tìm kiếm, một file ảnh là
     vô hình.
   - **Giữ lại chính hình vẽ**: cắt bằng `tools/cat_hinh.py` vào
     `corpus/<loại>/<mã>/phu-luc/hinh/`, rồi chèn link tương đối kèm mô tả thay
     thế (alt text) nói rõ hình thể hiện gì:

     ```markdown
     ![Hình H.1 - Mặt cắt bến lấy nước, thể hiện trụ chống trôi xe và rào chắn](hinh/hinh-h-01.png)
     ```

     `build_index.py` tự sửa đường dẫn tương đối khi sinh chunk — không chỉnh tay.

   **Không vẽ lại hình** thành SVG/Mermaid để thay cho bản gốc. Vẽ lại là diễn
   giải lại, mà văn bản pháp luật thì một nét lệch đã là sai. Sơ đồ tự vẽ chỉ
   dùng để giải thích cho người đọc, không bao giờ thay bản gốc.

6. `python3 tools/build_index.py`

## Ngôn ngữ

Nội dung văn bản giữ nguyên **tiếng Việt**, không dịch. Có thể giải thích bằng
tiếng Anh nếu người dùng hỏi bằng tiếng Anh, nhưng phần trích dẫn luôn để
nguyên văn tiếng Việt kèm số Điều.
