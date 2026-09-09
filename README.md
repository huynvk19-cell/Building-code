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

- **NĐ 212/2026** hiệu lực từ **01/7/2026**, thay thế Nghị định 111/2024/NĐ-CP.
> ⚠️ **Hai văn bản cùng mang số hiệu "QCVN 10"** nhưng khác cơ quan và khác nội
> dung hoàn toàn. Khi trích dẫn phải ghi đủ đuôi `/BXD` (Bộ Xây dựng — tiếp cận
> người khuyết tật) hay `/BCA` (Bộ Công an — phòng cháy chữa cháy).

- **QCVN 10:2024/BXD** thay thế QCVN 10:2014/BXD; điều khoản chuyển tiếp ở mục 3.1.
- **QCVN 10:2025/BCA** ban hành kèm Thông tư 103/2025/TT-BCA. Bản Quy chuẩn không
  chứa điều khoản hiệu lực — nội dung đó nằm trong Thông tư 103, **chưa có trong kho**.

## Tra cứu nhanh

```bash
python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề thiết kế hạng I"
python3 tools/search.py --full "nhà trẻ mẫu giáo trang bị chữa cháy tự động"
python3 tools/search.py --k 3 --full "hồ sơ đề nghị cấp giấy phép nhà thầu nước ngoài"
python3 tools/search.py --khong-dau "chung chi hanh nghe"      # gõ không dấu
python3 tools/search.py --json "mã định danh công trình"       # cho script/agent
```

Không cần cài gì thêm — chỉ dùng thư viện chuẩn của Python 3.

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
