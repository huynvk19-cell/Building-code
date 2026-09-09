# Building Code — Kho tra cứu văn bản pháp luật xây dựng

Kho dữ liệu dạng **RAG** (Retrieval-Augmented Generation): AI không cần "nhớ"
văn bản luật, mà tra cứu trực tiếp vào kho này. Git giữ lịch sử phiên bản —
khi một nghị định được sửa đổi, bạn commit bản mới và bản cũ vẫn còn nguyên.

## Đang có gì

| Văn bản | Nội dung | Trạng thái |
|---|---|---|
| **Nghị định 212/2026/NĐ-CP** (17/6/2026) | Điều kiện năng lực hoạt động xây dựng; Hệ thống thông tin, Cơ sở dữ liệu quốc gia về hoạt động xây dựng | 58 Điều + 4 Phụ lục — đã số hóa đầy đủ |
| **QCVN 10:2024/BXD** (01/8/2024) | Xây dựng công trình đảm bảo tiếp cận sử dụng cho người khuyết tật | 19 mục + 2 Phụ lục, **26 hình vẽ** — đã số hóa đầy đủ |
| **QCVN 10:2025/BCA** (04/11/2025) | Trang bị, bố trí phương tiện phòng cháy, chữa cháy, cứu nạn, cứu hộ cho nhà và công trình | 20 mục + 8 Phụ lục (A–H) — đã số hóa đầy đủ |

> ⚠️ **Hai văn bản cùng mang số hiệu "QCVN 10"** nhưng khác cơ quan và khác nội
> dung hoàn toàn. Khi trích dẫn phải ghi đủ đuôi `/BXD` (Bộ Xây dựng — tiếp cận
> người khuyết tật) hay `/BCA` (Bộ Công an — phòng cháy chữa cháy).

**Hiệu lực** — mỗi chunk mang sẵn trường `ngay_hieu_luc`, và kho chỉ ghi những gì
văn bản tự nói, không suy đoán:

- **NĐ 212/2026/NĐ-CP** — hiệu lực **01/7/2026** (Điều 57 khoản 1), thay thế Nghị
  định 111/2024/NĐ-CP. Điều khoản chuyển tiếp ở **Điều 55**: hồ sơ nộp trước thời
  điểm đó xử lý theo quy định cũ, nên đọc Điều 55 trước khi tư vấn.
- **QCVN 10:2024/BXD** — thay thế QCVN 10:2014/BXD, chuyển tiếp ở mục 3.1. Ngày
  hiệu lực **chưa xác định trong kho**: nó nằm ở Thông tư 06/2024/TT-BXD, văn bản
  này chưa được số hóa.
- **QCVN 10:2025/BCA** — ban hành kèm Thông tư 103/2025/TT-BCA. Bản Quy chuẩn
  không chứa điều khoản hiệu lực lẫn chuyển tiếp; cả hai nằm trong Thông tư 103,
  **chưa có trong kho**.

## Tra cứu nhanh

```bash
python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề thiết kế hạng I"
python3 tools/search.py --k 3 "hồ sơ đề nghị cấp giấy phép nhà thầu nước ngoài"
python3 tools/search.py --gon "nhà trẻ mẫu giáo trang bị chữa cháy tự động"  # chỉ tiêu đề
python3 tools/search.py --doc qcvn-10-2025-bca "bình chữa cháy"  # khoanh một văn bản
python3 tools/search.py --khong-dau "chung chi hanh nghe"        # gõ không dấu
python3 tools/search.py --json "mã định danh công trình"         # cho script/agent
```

Mặc định in **đầy đủ nội dung** chunk; thêm `--gon` nếu chỉ muốn xem tiêu đề.
Không cần cài gì thêm — chỉ dùng thư viện chuẩn của Python 3.

### Đọc điểm số cho đúng

Con số in cạnh mỗi kết quả là **điểm BM25 — nó đo mức trùng từ khóa, không đo
mức liên quan**. Công cụ luôn trả về kết quả kể cả khi kho không hề có quy định
về chủ đề bạn hỏi.

Chuyện này đã được đo chứ không phải phỏng đoán: trên bộ 101 câu hỏi chuẩn,
điểm cao nhất của những câu **ngoài phạm vi kho** nằm trong dải 5.9–20.8, còn của
những câu **có đáp án thật** nằm trong dải 4.2–44.9 — hai dải chồng lên nhau, nên
không có ngưỡng nào tách được chúng. Vì vậy kho cố tình **không** gắn nhãn "độ tin
cậy": một nhãn sai còn nguy hiểm hơn không có nhãn.

Cách dùng đúng là **đọc nội dung trả về** và tự hỏi *đoạn này có thật sự nói về
điều mình hỏi không*. Nếu không, câu trả lời đúng là "kho chưa có văn bản quy định
việc này" — kho mới chỉ có ba văn bản.

## Cấu trúc

```
corpus/                       Bản gốc (nguồn sự thật duy nhất)
  nghi-dinh/212-2026-nd-cp/
    toan-van.md               Toàn văn 58 Điều
    muc-luc.md                Mục lục (sinh tự động)
    phu-luc/                  Phụ lục I–IV
  quy-chuan/qcvn-10-2024-bxd/
    toan-van.md               Phần 1–3
    phu-luc/hinh/             26 hình vẽ cắt từ PDF gốc
  quy-chuan/qcvn-10-2025-bca/
    toan-van.md               Phần 1–4 (mục 1.1, 2.3.1…)
    phu-luc/                  Phụ lục A–H (các bảng tra cứu)
    phu-luc/hinh/             Hình vẽ cắt từ bản gốc
chunks/                       Mỗi Điều / mục / bảng một file (sinh tự động)
index/
  chunks.jsonl                Chỉ mục truy hồi kèm metadata
  documents.json              Sổ đăng ký văn bản
eval/
  bo_cau_hoi.jsonl            101 câu hỏi gán nhãn vàng để đo truy hồi
  chay_danh_gia.py            Đo Recall@k và MRR
tools/
  ingest_pdf.py               PDF → ảnh trang + OCR nháp
  cat_hinh.py                 Cắt hình vẽ từ PDF gốc vào corpus/
  build_index.py              corpus/ → chunks/ + index/
  search.py                   Tìm kiếm BM25
docs/
  huong-dan-su-dung.md        Hướng dẫn dùng hằng ngày
  ket-noi-ai.md               3 cách cho AI "ngồi lên" kho này
CLAUDE.md                     Chỉ dẫn cho AI (quy tắc trích dẫn)
```

## Thêm văn bản mới

```bash
python3 tools/ingest_pdf.py vanban-moi.pdf --ten 213-2026-nd-cp
# → đọc ảnh trang bằng Claude, chép thành corpus/.../toan-van.md
python3 tools/build_index.py
git add -A && git commit -m "Thêm Nghị định 213/2026/NĐ-CP"
```

Chi tiết ở [`docs/huong-dan-su-dung.md`](docs/huong-dan-su-dung.md).

## Đo chất lượng tra cứu

Kho có bộ **101 câu hỏi gán nhãn vàng** (`eval/bo_cau_hoi.jsonl`), trong đó 10 câu
cố tình hỏi những thứ **không** có trong kho, để kiểm tra xem công cụ có bịa ra
câu trả lời không.

```bash
python3 eval/chay_danh_gia.py            # chỉ số hiện hành
python3 eval/chay_danh_gia.py --so-sanh  # đối chứng với cấu hình cũ
python3 eval/chay_danh_gia.py --chi-tiet # xem những câu bị trượt
```

Mức hiện tại — đúng chunk nằm trong 5 kết quả đầu ở **84%** số câu, trong 10 kết
quả đầu ở **92%**:

| | Cấu hình cũ | Hiện tại |
|---|---|---|
| Recall@1 | 0.480 | **0.549** |
| Recall@3 | 0.681 | **0.733** |
| Recall@5 | 0.786 | **0.844** |
| Recall@10 | 0.857 | **0.916** |
| MRR | 0.648 | **0.713** |

Mức tăng đến từ hai chỗ: tokenizer không còn cắt nát số liệu ("1 200 m²", "0,45 m"
trước đây bị vỡ thành mảnh vô nghĩa), và câu hỏi gọi đích danh số Điều/mục/Bảng
được cộng điểm. Riêng loại câu hỏi tra cứu trực tiếp tăng từ 0.42 lên 0.92.

Còn yếu ở câu hỏi bắc cầu hai văn bản (0.33) và câu hỏi mơ hồ (0.25). Giới hạn
của phép đo được ghi thẳng trong [`eval/README.md`](eval/README.md) — nên đọc
trước khi trích dẫn mấy con số này.

Sau khi sửa `tools/search.py` hoặc đổi cách cắt chunk, chạy lại bộ đo trước khi commit.

## Về độ chính xác

Cả ba file PDF gốc đều là **bản scan** (ảnh, không có lớp text). Quy trình số hóa:

1. OCR bằng Tesseract tiếng Việt → **bản nháp**
2. Đọc lại từng trang bằng **thị giác máy (Claude vision)** và hiệu đính

Bước 2 là bắt buộc: OCR đánh rơi dấu tiếng Việt ("thẩm quyền" → "thâm quyên",
"dữ liệu" → "đữ liệu"). Với văn bản pháp luật, sai một dấu là sai nghĩa.

**Với hình vẽ** thì làm hai lớp: chép chú dẫn thành chữ để tìm kiếm được, đồng
thời cắt giữ lại chính hình vẽ trong `phu-luc/hinh/` để nhìn được. Hình vẽ không
bao giờ được vẽ lại — vẽ lại là diễn giải lại.

> Kho này là **công cụ tra cứu**, không thay thế bản công báo chính thức.
> Với hồ sơ pháp lý, hãy đối chiếu lại bản gốc trên Cổng thông tin điện tử Chính phủ.
