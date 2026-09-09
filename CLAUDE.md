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

## Quy trình kiểm chứng bắt buộc — đọc kỹ phần này

`tools/search.py` **luôn trả về kết quả** miễn là câu hỏi có một từ nào đó trùng
với kho. Điểm số in ra là **điểm BM25 — chỉ đo mức trùng từ khóa, không đo mức
liên quan**. Một câu hỏi hoàn toàn ngoài phạm vi kho vẫn nhận được 5 kết quả với
điểm nhìn có vẻ "cao".

Điều này **đã được đo, không phải phỏng đoán**: trên 101 câu hỏi chuẩn
(`eval/`), điểm top-1 của các câu **ngoài phạm vi kho** rơi vào 5.9–20.8, còn
của các câu **có đáp án thật** rơi vào 4.2–44.9. Hai dải **chồng lấn hoàn toàn**.
Thử nghiệm thứ hai — đo tỉ lệ phủ từ hiếm — còn tệ hơn. Vì vậy **không có ngưỡng
tin cậy nào trong công cụ này**, và đừng thêm vào: một nhãn tin cậy sai nguy hiểm
hơn không có nhãn, vì nó tạo cảm giác an toàn giả.

Trách nhiệm phân biệt "có đáp án" với "ngoài phạm vi" **thuộc về bạn**, và quy
trình là:

1. **Đọc nội dung chunk trả về**, không chỉ nhìn tiêu đề và điểm số.
2. **Tự hỏi: đoạn văn này có thật sự chứa quy định về đúng chủ đề được hỏi
   không?** Trùng vài từ khóa không phải là trả lời.
3. Nếu **có** → trích dẫn nguyên văn kèm số Điều/mục.
4. Nếu **không** → nói thẳng: *"kho hiện chưa có văn bản quy định việc này"*, và
   nêu kho đang có những văn bản nào. **Tuyệt đối không** ghép các mảnh chỉ trùng
   từ khóa lại thành một câu trả lời nghe có vẻ hợp lý.
5. Khi câu hỏi thuộc lĩnh vực kho chưa bao phủ (tải trọng gió, chống sét, kết
   cấu, tiết kiệm năng lượng, quy hoạch chi tiết…), hãy nói rõ ngay từ đầu thay
   vì cố nặn ra câu trả lời từ ba văn bản đang có.

Kho hiện **chỉ có ba văn bản**. Mặc định của bạn khi không chắc phải là *"chưa
có trong kho"*, không phải *"có lẽ là…"*.

## Kiểm tra hiệu lực

Mỗi chunk mang sẵn ba trường: `ngay_ban_hanh`, `ngay_hieu_luc`, `het_hieu_luc`.
`index/documents.json` mang thêm `can_cu_hieu_luc`, `thay_the`, `sua_doi_boi`,
`dieu_khoan_chuyen_tiep`. **Luôn đọc `ngay_hieu_luc` trước khi tư vấn.**

- Nếu `ngay_hieu_luc` là **`CHƯA XÁC ĐỊNH`** → kho **không** có căn cứ về ngày
  hiệu lực. Phải nói rõ điều đó, tuyệt đối không suy đoán một ngày cụ thể.
- Nếu `het_hieu_luc` có giá trị → văn bản đã hết hiệu lực, phải cảnh báo.

Tình trạng hiện tại:

| Văn bản | `ngay_hieu_luc` | Chuyển tiếp | Ghi chú |
|---|---|---|---|
| **212/2026/NĐ-CP** | `2026-07-01` (Điều 57 khoản 1) | **Điều 55** | Thay thế NĐ 111/2024/NĐ-CP. Đọc Điều 55 trước khi tư vấn cho hồ sơ nộp trước 01/7/2026. |
| **QCVN 10:2024/BXD** | `CHƯA XÁC ĐỊNH` | mục 3.1 | Hiệu lực nằm ở Thông tư 06/2024/TT-BXD — **chưa có trong kho**. |
| **QCVN 10:2025/BCA** | `CHƯA XÁC ĐỊNH` | không có trong bản Quy chuẩn | Hiệu lực nằm ở Thông tư 103/2025/TT-BCA — **chưa có trong kho**. |

## Hai văn bản trùng số hiệu "QCVN 10"

Kho có **hai** văn bản cùng mang số hiệu QCVN 10 nhưng khác cơ quan ban hành và
khác hoàn toàn về nội dung:

- **QCVN 10:2024/BXD** (Bộ Xây dựng) — tiếp cận sử dụng cho người khuyết tật.
- **QCVN 10:2025/BCA** (Bộ Công an) — trang bị phương tiện phòng cháy chữa cháy.

Khi trích dẫn **phải ghi đủ đuôi `/BXD` hoặc `/BCA`**. `search.py` sẽ in cảnh báo
`⚠ Kết quả chỉ đến từ QCVN 10:.../...` khi truy vấn nhắc "QCVN 10" mà kết quả chỉ
rơi vào một trong hai — gặp cảnh báo đó thì hỏi lại người dùng đang cần văn bản nào.

## Tra đúng bảng khi hỏi về PCCC

Theo mục 1.5.9 QCVN 10:2025/BCA, xác định yêu cầu trang bị theo thứ tự:
**Bảng A.1** (toàn nhà) → **Bảng A.2** (hạng mục/khu vực) → **Bảng A.3**
(gian phòng) → **Bảng A.4** (thiết bị).
Luôn kiểm tra thêm mục 1.5.11 về các khu vực **không** phải trang bị.

## Cách tra cứu

Ưu tiên theo thứ tự:

```bash
# 1. Tìm theo từ khóa (nhanh nhất, đã đủ cho hầu hết câu hỏi)
#    Mặc định IN ĐẦY ĐỦ NỘI DUNG — vì bạn buộc phải đọc mới kết luận được.
python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề hạng II"

python3 tools/search.py --gon "thu hồi giấy phép"     # chỉ tiêu đề, để duyệt nhanh
python3 tools/search.py --json "mã định danh"         # cho script
python3 tools/search.py --doc qcvn-10-2025-bca "bình chữa cháy"   # khoanh một văn bản
python3 tools/search.py --khong-dau "chung chi hanh nghe"         # gõ không dấu

# 2. Đọc thẳng một Điều / mục / bảng đã biết
cat chunks/212-2026-nd-cp/dieu-33-*.md
cat chunks/qcvn-10-2025-bca/muc-2-4-*.md
cat chunks/qcvn-10-2025-bca/phu-luc-a-01-*.md      # Bảng A.1

# 3. Duyệt mục lục
cat corpus/nghi-dinh/212-2026-nd-cp/muc-luc.md
```

`index/chunks.jsonl` chứa toàn bộ chunk kèm metadata — dùng khi cần lọc/duyệt
bằng script. `index/documents.json` là sổ đăng ký văn bản.

**Lưu ý về `--gon`**: chỉ dùng khi bạn đang duyệt để chọn chunk nào đáng đọc.
Không bao giờ kết luận từ tiêu đề — bước 1 của quy trình kiểm chứng ở trên đòi
bạn đọc nội dung thật.

## Đo chất lượng truy hồi

`eval/` có bộ 101 câu hỏi gán nhãn vàng (trong đó 10 câu cố tình nằm ngoài phạm
vi kho). Sau khi sửa `tools/search.py` hoặc thay đổi cách cắt chunk, **phải chạy
lại**:

```bash
python3 eval/chay_danh_gia.py            # chỉ số hiện hành
python3 eval/chay_danh_gia.py --so-sanh  # đối chứng với tokenizer cũ
python3 eval/chay_danh_gia.py --chi-tiet # liệt kê câu trượt
```

Mức hiện tại: Recall@1 = 0.549 · Recall@5 = 0.844 · Recall@10 = 0.916 · MRR = 0.713.
**Đừng merge một thay đổi làm các số này tụt** mà không có lý do đo được.
Điểm yếu đã biết: loại G (câu hỏi bắc cầu hai văn bản) = 0.33, loại I (câu hỏi
mơ hồ) = 0.25. Giới hạn của bộ đo được ghi ở `eval/README.md` — đọc trước khi
trích dẫn con số.

## Cấu trúc kho

```
corpus/     Bản gốc do người dùng sở hữu — CHỈ sửa ở đây
chunks/     Sinh tự động từ corpus/ — KHÔNG sửa tay
index/      Sinh tự động — KHÔNG sửa tay
eval/       Bộ câu hỏi chuẩn + script đo
tools/      Script xử lý
docs/       Hướng dẫn cho người dùng
```

Sau **bất kỳ** thay đổi nào trong `corpus/`, phải chạy lại:

```bash
python3 tools/build_index.py
```

Lệnh này idempotent — chạy hai lần cho kết quả giống hệt nhau.

## Khi thêm văn bản mới

1. `python3 tools/ingest_pdf.py <file.pdf> --ten <ma-van-ban>`
2. Đọc từng ảnh trang bằng **thị giác máy** và chép lại thành Markdown.
   **Không** dán thẳng kết quả OCR vào corpus — Tesseract đánh rơi dấu tiếng
   Việt ("thẩm quyền" → "thâm quyên"), với văn bản pháp luật là sai nghĩa.
   OCR chỉ dùng để đối chiếu.
3. Lưu vào `corpus/<loại>/<mã>/toan-van.md` với front matter đầy đủ
   (xem `corpus/nghi-dinh/212-2026-nd-cp/toan-van.md` làm mẫu). Bắt buộc khai
   `ngay_hieu_luc` — nếu văn bản không tự nói ngày hiệu lực thì ghi
   `"CHƯA XÁC ĐỊNH"` kèm `can_cu_hieu_luc` chỉ ra văn bản chứa nó.
   **Không được tự điền một ngày phỏng đoán.**
4. Giữ đúng quy ước tiêu đề để bộ chia chunk nhận diện được. Khai báo
   `cau_truc` trong front matter để chọn kiểu cắt:
   - `cau_truc: "dieu"` (mặc định — Nghị định, Luật, Thông tư):
     `## Chương I. TÊN` · `### Mục 1. TÊN` · `### Điều 1. Tên điều`
   - `cau_truc: "muc"` (Quy chuẩn, Tiêu chuẩn):
     `## 1 TÊN PHẦN` · `### 1.1 Tên mục`
   - Phụ lục: khai báo `chia_theo` (`"Mẫu số"`, `"Bảng"`, `"H."`) để cắt theo
     tiêu đề cấp 2; không khai báo thì giữ nguyên cả phụ lục làm một chunk.
5. `python3 tools/build_index.py`
6. Thêm vài câu hỏi cho văn bản mới vào `eval/bo_cau_hoi.jsonl` rồi chạy lại
   `python3 eval/chay_danh_gia.py`.

## Hình vẽ

Hình vẽ trong quy chuẩn **không bao giờ được vẽ lại** bằng SVG/Mermaid để thay
bản gốc — vẽ lại là diễn giải lại, và một nét sai trong hình kỹ thuật là một quy
định sai. Cách làm: cắt hình gốc từ PDF vào `corpus/.../phu-luc/hinh/`, rồi chèn
vào Markdown bằng link kèm alt text mô tả để tìm kiếm được.

Chú thích hình trong QCVN có thể nằm **bên dưới hoặc bên phải** hình. Khi cắt
bằng `tools/cat_hinh.py` phải lấy **trọn bề ngang trang** (x từ 35 đến 588 pt với
khổ A4), nếu không sẽ mất phần chú thích bên phải. Mỗi hình vẽ thuộc về **chú
thích đầu tiên đứng sau nó**.

## Ngôn ngữ

Nội dung văn bản giữ nguyên **tiếng Việt**, không dịch. Có thể giải thích bằng
tiếng Anh nếu người dùng hỏi bằng tiếng Anh, nhưng phần trích dẫn luôn để
nguyên văn tiếng Việt kèm số Điều.

Khi trả lời người dùng này: viết **văn xuôi tự nhiên, gần gũi như một trợ lý con
người**, không phải bảng biểu khô khan. Vẫn phải kèm trích dẫn đầy đủ — chỉ khác
ở giọng văn, không khác ở độ chính xác.
