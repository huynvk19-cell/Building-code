# Building Code — Kho tra cứu văn bản pháp luật xây dựng

Kho dữ liệu dạng **RAG** (Retrieval-Augmented Generation): AI không cần "nhớ"
văn bản luật, mà tra cứu trực tiếp vào kho này. Git giữ lịch sử phiên bản —
khi một nghị định được sửa đổi, bạn commit bản mới và bản cũ vẫn còn nguyên.

Hiện có **16 văn bản · 1 303 chunk · 241 ảnh** cắt từ bản in gốc.

## Đang có gì

### Văn bản quy phạm pháp luật — đã số hóa đầy đủ

| Văn bản | Nội dung | Hiệu lực | Chunk |
|---|---|---|---|
| **QCVN 06:2022/BXD** | An toàn cháy cho nhà và công trình — bậc chịu lửa, khoang cháy, thoát nạn, ngăn cháy lan, cấp nước chữa cháy. Mục 1–7 + Phụ lục A–I, 64 bảng tra, 13 hình vẽ | 16/01/2023 | 445 |
| **Sửa đổi 1:2023 QCVN 06:2022/BXD** | Sửa khoảng 120 điểm của bản gốc. **Không thay thế** — phải đọc kèm | 01/12/2023 | 146 |
| **QCVN 01:2021/BXD** | Quy hoạch xây dựng — đất dân dụng, mật độ xây dựng, khoảng lùi, hạ tầng kỹ thuật. 5 phần, 164 mục, 32 bảng | 05/7/2021 | 168 |
| **QCVN 04:2021/BXD** | Nhà chung cư | 05/7/2021 | 134 |
| **QCVN 10:2024/BXD** | Tiếp cận sử dụng cho người khuyết tật. 19 mục + 2 Phụ lục, 26 hình vẽ | CHƯA XÁC ĐỊNH | 22 |
| **QCVN 10:2025/BCA** | Trang bị, bố trí phương tiện phòng cháy chữa cháy, cứu nạn cứu hộ | CHƯA XÁC ĐỊNH | 39 |
| **Thông tư 06/2021/TT-BXD** | Phân cấp công trình xây dựng. 5 Điều + 3 Phụ lục, 6 bảng phân cấp | 15/8/2021 | 69 |
| **Thông tư 02/2025/TT-BXD** | Sửa 17 chỗ của Thông tư 06/2021. **Không thay thế** — phải đọc kèm | 20/5/2025 | 20 |
| **Nghị định 212/2026/NĐ-CP** | Điều kiện năng lực hoạt động xây dựng; cơ sở dữ liệu quốc gia. 58 Điều + 4 Phụ lục | 01/7/2026 | 76 |
| **Nghị định 347/2026/NĐ-CP** | Sửa 4 nghị định về phòng cháy chữa cháy. 42 Điều + 3 Phụ lục | 15/9/2026 | 46 |

### Tài liệu tham khảo — KHÔNG phải căn cứ pháp lý

| Tài liệu | Nội dung | Chunk |
|---|---|---|
| **Hỏi đáp C07** | 132 giải đáp của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ. Cho biết cơ quan thẩm duyệt **thực tế hiểu quy định thế nào** — nhưng không bao giờ được trích làm căn cứ. Không mục nào có ngày trả lời | 133 |

### Khung rỗng — mới có tên, chưa có nội dung

`105/2025/NĐ-CP` · `106/2025/NĐ-CP` · `169/2025/NĐ-CP` · `282/2025/NĐ-CP` ·
`217/2026/NĐ-CP`. Tra tới chúng thì kho trả về một dòng nói thẳng *chưa có nội
dung*, thay vì trả về rỗng khiến người đọc tưởng là "pháp luật không quy định".

**Cần bổ sung nhất là Nghị định 105/2025/NĐ-CP** — 72 trên 132 giải đáp của C07
viện dẫn văn bản này.

## Ba cái bẫy phải biết trước khi tra

> ⚠️ **Hai văn bản cùng số hiệu "QCVN 10"**, khác cơ quan và khác hẳn nội dung.
> Trích phải ghi đủ đuôi `/BXD` (Bộ Xây dựng — tiếp cận người khuyết tật) hay
> `/BCA` (Bộ Công an — phòng cháy chữa cháy).

> ⚠️ **QCVN 06 phải đọc kèm Sửa đổi 1:2023.** Quy định đang có hiệu lực = bản gốc
> **đã vá bằng** bản sửa đổi. Kho giữ nguyên văn cả hai và tự nối: **95 chunk**
> của bản gốc mang cờ `sua_doi_boi`, `search.py` in cảnh báo `⚠️ ĐÃ BỊ SỬA ĐỔI`
> ngay trên kết quả.
>
> Đáng chú ý: **toàn bộ Phụ lục A.4 (nhà kinh doanh karaoke, vũ trường) đã bị bãi
> bỏ** từ 01/12/2023, cùng các điểm 1.3, 7.4, A.1.3.12, H.2.10.3.

> ⚠️ **Thông tư 06/2021 phải đọc kèm Thông tư 02/2025.** Cặp này **không** có
> cảnh báo tự động trên từng chunk (lý do kỹ thuật ghi trong `CLAUDE.md`), nên
> danh sách đủ 17 chỗ đã sửa nằm trong `CLAUDE.md`. Trong đó **mục 1.2.1.3 Bảng
> 1.2 đã bị bãi bỏ**.

**Ngày hiệu lực** — kho chỉ ghi những gì văn bản tự nói, không suy đoán. Hai quy
chuẩn mang `CHƯA XÁC ĐỊNH` vì ngày hiệu lực của chúng nằm ở Thông tư ban hành
(06/2024/TT-BXD và 103/2025/TT-BCA), mà hai Thông tư đó chưa có trong kho.

## Tra cứu nhanh

```bash
# Tra một điều khoản đã biết số hiệu, KÈM PHẠM VI ÁP DỤNG — chạy trước khi trích
python3 tools/tra_muc.py 3.3.6
python3 tools/tra_muc.py 2.7.4 --doc qcvn-10-2024-bxd
python3 tools/tra_muc.py G.9                    # tra bảng

# Tìm theo từ khóa
python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề thiết kế hạng I"
python3 tools/search.py --gon "trường tiểu học cấp công trình"   # chỉ tiêu đề
python3 tools/search.py --doc qcvn-10-2025-bca "bình chữa cháy"  # khoanh một văn bản
python3 tools/search.py --khong-dau "chung chi hanh nghe"        # gõ không dấu
python3 tools/search.py --json "mã định danh công trình"         # cho script
```

### Đọc điểm số cho đúng

Điểm in ra là **điểm BM25 — đo mức trùng từ khóa, chứ không đo mức liên quan**.
Một câu hỏi hoàn toàn ngoài phạm vi kho vẫn nhận được 5 kết quả trông có vẻ hợp lý.

Đã đo trên bộ câu hỏi chuẩn: điểm top-1 của câu **ngoài phạm vi** rơi vào
17,3–33,6, của câu **có đáp án thật** rơi vào 6,1–76,2 — **hai dải chồng lấn hoàn
toàn**. Vì vậy công cụ **cố ý không có ngưỡng tin cậy**: một nhãn tin cậy sai
nguy hiểm hơn không có nhãn. Luôn đọc nội dung chunk trước khi kết luận.

## Cấu trúc

```
corpus/                       Bản gốc — nguồn sự thật duy nhất, CHỈ sửa ở đây
  quy-chuan/<mã>/
    toan-van.md               Toàn văn
    phu-luc/                  Phụ lục, mỗi tệp khai chia_theo riêng
    phu-luc/hinh/             Hình vẽ cắt từ PDF gốc
    phu-luc/bang/  bang/      Ảnh bảng cắt từ PDF gốc
  nghi-dinh/<mã>/             Nghị định, Luật, Thông tư — cùng cấu trúc
  huong-dan/hoi-dap-c07/      Tài liệu THAM KHẢO, không có giá trị pháp lý
chunks/                       Mỗi Điều / mục / bảng một tệp (sinh tự động)
index/chunks.jsonl            Chỉ mục truy hồi kèm metadata
index/documents.json          Sổ đăng ký văn bản
eval/bo_cau_hoi.jsonl         225 câu hỏi gán nhãn vàng
.claude/skills/               Ba skill nạp theo yêu cầu, không thường trực
docs/                         Hướng dẫn cho người dùng
CLAUDE.md                     Hàng rào chống trả lời sai, dành cho AI
```

### Công cụ

| Tệp | Việc |
|---|---|
| `search.py` | Tìm kiếm BM25 kèm xếp hạng lại theo vị trí gần nhau |
| `tra_muc.py` | Tra một mục kèm **phạm vi áp dụng**, mục cha, cờ sửa đổi, ảnh kèm |
| `build_index.py` | `corpus/` → `chunks/` + `index/`, idempotent |
| `ingest_pdf_text.py` | PDF **có lớp văn bản** → Markdown, không qua OCR |
| `ingest_bang_pdf.py` | **Bảng tra** → Markdown giữ đúng quan hệ hàng cột, xử lý được trang in xoay ngang |
| `ingest_pdf.py` | PDF **bản quét** → ảnh trang để chép bằng thị giác máy |
| `ingest_hoi_dap.py` | Tệp hỏi đáp nghiệp vụ → corpus |
| `cat_bang.py` · `cat_hinh.py` | Cắt ảnh bảng, ảnh hình từ PDF gốc |
| `chen_anh_bang.py` | Chèn liên kết ảnh vào corpus, kiểm sót |
| `tao_khung_van_ban.py` | Tạo khung rỗng cho văn bản chưa có nội dung |

## Thêm văn bản mới

Bước đầu tiên quyết định toàn bộ cách làm — **PDF có lớp văn bản thật không**:

```bash
python3 -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); \
  print(sum(1 for p in d if p.get_text().strip()), '/', len(d))" vanban-moi.pdf
```

Có lớp văn bản thì trích thẳng bằng `ingest_pdf_text.py` (chính xác tuyệt đối);
là bản quét thì phải chép từng trang bằng thị giác máy. **Không bao giờ dán
thẳng kết quả OCR vào corpus** — Tesseract đánh rơi dấu tiếng Việt ("thẩm quyền"
→ "thâm quyên"), với văn bản pháp luật là sai nghĩa.

Quy trình đầy đủ, kèm **năm cái bẫy đã mắc thật**, nằm trong skill
`.claude/skills/them-van-ban/`. Hướng dẫn dùng hằng ngày ở
[`docs/huong-dan-su-dung.md`](docs/huong-dan-su-dung.md).

Sau mỗi thay đổi trong `corpus/`, bốn bước sau là bắt buộc:

```bash
python3 tools/build_index.py     # 1. dựng lại chỉ mục, phải chạy sạch
python3 tools/build_index.py     # 2. chạy lần hai, kết quả phải giống hệt
python3 eval/chay_danh_gia.py    # 3. không có dòng LỖI, chỉ số không tụt
python3 tools/chen_anh_bang.py   # 4. không còn liên kết ảnh nào bị sót
```

## Đo chất lượng tra cứu

Bộ **225 câu hỏi gán nhãn vàng** (`eval/bo_cau_hoi.jsonl`), trong đó 10 câu cố
tình hỏi những thứ **không** có trong kho, để kiểm tra công cụ có bịa hay không.

```bash
python3 eval/chay_danh_gia.py            # chỉ số hiện hành
python3 eval/chay_danh_gia.py --chi-tiet # xem những câu bị trượt
```

Mức hiện tại trên 16 văn bản, 1 303 chunk:

| | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR |
|---|---|---|---|---|---|
| 225 câu | 0,555 | 0,796 | **0,845** | 0,891 | 0,701 |

Nghĩa là đúng chunk nằm trong 5 kết quả đầu ở **84%** số câu, trong 10 kết quả
đầu ở **89%**.

**Các con số qua từng đợt mở rộng không so sánh trực tiếp được** — mỗi lần đo
trên một bộ câu hỏi khác và một kho khác (176 → 682 → 1 303 chunk). Thêm văn bản
thì cạnh tranh tăng nên vài câu cũ bị đẩy xuống; đó là cái giá của kho rộng hơn,
đã đo chứ không giấu. Ba lần đánh đổi lớn đều được tách riêng và ghi lại bằng
phép đo trong skill `do-luong-truy-hoi`:

- **133 chunk hỏi đáp nghiệp vụ** làm Recall@3 tụt 0,774 → 0,762 trên đúng bộ
  câu cũ; hạ trọng số tài liệu tham khảo xuống 0,90 kéo lại được phần lớn.
- **168 chunk QCVN 01:2021/BXD** và việc giữ lại các mục cha chỉ có tên làm
  Recall@1 tụt 0,570 → 0,550. Riêng phần giữ mục cha tốn 0,005 — đổi lại **phạm
  vi áp dụng của mục cha quay lại chỉ mục**, thứ mà thiếu nó đã gây một lỗi có thật.
- **Thông tư phân cấp công trình** thì nhích lên: 0,550 → 0,555.

Còn yếu ở câu hỏi bắc cầu nhiều văn bản (0,17) và câu hỏi mơ hồ (0,25). Giới hạn
của phép đo ghi thẳng trong [`eval/README.md`](eval/README.md) — nên đọc trước
khi trích dẫn mấy con số này.

**Vì sao không dùng cơ sở dữ liệu vector:** đã đo, không phải quan điểm. Không
một câu nào trong bộ đánh giá thất bại vì BM25 tìm không ra chunk vàng —
Recall@50 đạt 0,938 và Recall@100 đạt 0,972, mọi chunk vàng đều được tìm thấy, chỉ bị xếp hạng thấp. Việc
cần làm là **xếp hạng lại**, không phải đổi cách tìm. Thêm nữa, tra cứu pháp luật
cần khớp định danh chính xác ("QCVN 10:2024/BXD" so với "QCVN 10:2025/BCA" khác
đúng một ký tự), mà véc-tơ nhúng làm mờ đúng thứ đó. Lập luận đầy đủ kèm ngưỡng
nên xem lại quyết định nằm trong skill `do-luong-truy-hoi`.

## Về độ chính xác

Kho có hai loại bản gốc, xử lý khác hẳn nhau:

**PDF có lớp văn bản** (bản ký số, bản Công báo) — trích thẳng, chính xác tuyệt
đối. Vẫn phải mở vài trang bằng thị giác máy để đối chiếu, và **luôn đối chiếu số
mục trích được với bản gốc**: lệch là có mục bị nuốt.

**PDF bản quét** — OCR chỉ để định vị, nội dung phải chép lại bằng thị giác máy
từng trang.

**Bảng tra** thì không dùng lớp văn bản phẳng: với một bảng, lớp văn bản chỉ cho
ra chuỗi ô và **mất thông tin ô đó thuộc cột nào**. Chuỗi phẳng của Bảng 1.1
Thông tư 06/2021 đọc là "Trường tiểu học · Tổng số học sinh toàn trường · ≥ 700 ·
< 700", không cách nào biết ≥ 700 là cấp II còn < 700 là cấp III. `ingest_bang_pdf.py`
dựng lại lưới từ **chính đường kẻ in trong PDF** nên quan hệ hàng cột là đọc ra
được, không phải suy đoán.

**Hình vẽ và bảng không bao giờ được vẽ lại** — vẽ lại là diễn giải lại, và một
nét sai trong hình kỹ thuật là một quy định sai. Kho cắt giữ ảnh gốc (200 ảnh
bảng, 41 hình) và chèn liên kết ngay dưới tiêu đề, nên kết quả tra cứu đã mang
sẵn đường dẫn ảnh.
