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

Điều này **đã được đo, không phải phỏng đoán**: trên bộ câu hỏi chuẩn
(`eval/`), điểm top-1 của các câu **ngoài phạm vi kho** rơi vào 7.2–34.1, còn
của các câu **có đáp án thật** rơi vào 4.6–67.3. Hai dải **chồng lấn hoàn toàn**.
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
   vì cố nặn ra câu trả lời từ năm văn bản đang có.

Kho hiện **chỉ có năm văn bản**. Mặc định của bạn khi không chắc phải là *"chưa
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
| **QCVN 06:2022/BXD** | `2023-01-16` (Điều 2 Thông tư 06/2022/TT-BXD) | **mục 7.1** | Thay thế QCVN 06:2021/BXD. Đã có **đủ mục 1–7 và Phụ lục A–I**. ⚠️ **Đã bị Sửa đổi 1:2023 sửa nhiều điểm** — xem mục riêng bên dưới. |
| **Sửa đổi 1:2023 QCVN 06:2022/BXD** | `2023-12-01` (Điều 2 Thông tư 09/2023/TT-BXD) | **Điều 3 Thông tư 09/2023/TT-BXD** | Sửa đổi, bổ sung QCVN 06:2022/BXD. **Không thay thế** — phải đọc kèm bản gốc. |
| **QCVN 10:2024/BXD** | `CHƯA XÁC ĐỊNH` | mục 3.1 | Hiệu lực nằm ở Thông tư 06/2024/TT-BXD — **chưa có trong kho**. |
| **QCVN 10:2025/BCA** | `CHƯA XÁC ĐỊNH` | không có trong bản Quy chuẩn | Hiệu lực nằm ở Thông tư 103/2025/TT-BCA — **chưa có trong kho**. |

## QCVN 06 — LUÔN PHẢI ĐỌC KÈM SỬA ĐỔI 1:2023

Đây là phần dễ trả lời sai nhất trong kho. Đọc hết trước khi tư vấn bất cứ điều
gì về an toàn cháy.

Kho có **hai văn bản** cho cùng một quy chuẩn:

- **QCVN 06:2022/BXD** — bản gốc, hiệu lực 16/01/2023. Đủ mục 1–7 và Phụ lục A–I.
- **Sửa đổi 1:2023 QCVN 06:2022/BXD** — hiệu lực **01/12/2023**, ban hành kèm
  Thông tư 09/2023/TT-BXD. Sửa khoảng **120 điểm** của bản gốc.

Bản sửa đổi **không thay thế** bản gốc. Lời nói đầu của chính nó nói rõ: *"Các
nội dung không được nêu tại Sửa đổi 1 này thì tiếp tục áp dụng QCVN
06:2022/BXD"*. Nghĩa là quy định đang có hiệu lực = **bản gốc, đã vá bằng bản
sửa đổi**. Không văn bản nào một mình là câu trả lời đầy đủ.

### Cách làm bắt buộc

Kho **giữ nguyên văn bản gốc**, không sửa chữ trong đó — vì corpus phải trung
thành với bản in. Thay vào đó `tools/build_index.py` tự ghép hai bên theo số
hiệu mục và gắn trường `sua_doi_boi` vào chunk của bản gốc. `tools/search.py`
in cảnh báo:

```
⚠️  ĐÃ BỊ SỬA ĐỔI bởi Sửa đổi 1:2023 QCVN 06:2022/BXD (hiệu lực 2023-12-01)
```

**Thấy dòng đó thì bắt buộc mở file sửa đổi ra đọc rồi mới trả lời.** Trả lời
chỉ dựa trên bản gốc là trả lời sai quy định hiện hành. Hiện có **92 chunk** của
bản gốc mang cờ này.

Khi trích dẫn, ghi rõ cả hai, ví dụ:

> Theo mục 3.2.8 QCVN 06:2022/BXD, được sửa đổi bởi mục 3.2.8 Sửa đổi 1:2023
> QCVN 06:2022/BXD (hiệu lực 01/12/2023), khoảng cách giữa hai lối ra thoát nạn…

Nếu mục được hỏi **không** mang cờ thì bản gốc vẫn nguyên hiệu lực, trích bình thường.

### Những điểm đã bị BÃI BỎ — tuyệt đối không trích như đang có hiệu lực

| Bị bãi bỏ | Nội dung |
|---|---|
| **A.4 (toàn bộ)** | Quy định riêng cho **nhà kinh doanh karaoke, vũ trường** — bậc chịu lửa tối thiểu IV, ngưỡng 300 m²/200 m²/20 người… |
| **1.3** | (điểm 1.3 phần Quy định chung) |
| **7.4** | (điểm 7.4 phần Tổ chức thực hiện) |
| **A.1.3.12**, **H.2.10.3** | |
| **bãi bỏ một phần** | 3.2.11 (câu 2 đoạn 1) · 3.3.5 (câu 3 đoạn 2) · 3.4.13 (đoạn 2 và đoạn a) · A.1.3.2 (đoạn 2) · A.3.1.16 (đoạn e) · G.1.2.1 (CHÚ THÍCH) · Bảng 7 (CHÚ THÍCH 3) · 6.2.2.3 (CHÚ THÍCH 2) |
| **bỏ cụm từ** | 3.4.8 (“là buồng thang bộ không nhiễm khói và”) · 5.1.1.3 · 5.1.5.7 · 6.17.1 (“theo A.4”) · A.3.1.8 (“khoảng cách hở thông thủy… 100 mm”) |

Câu hỏi về **karaoke, vũ trường** rất hay gặp — A.4 đã bị bãi bỏ hoàn toàn từ
01/12/2023, và 6.17.1 cũng đã bỏ cụm từ "theo A.4". Đừng trích A.4.

### Điều khoản chuyển tiếp — hỏi hồ sơ ở giai đoạn nào

Điều 3 Thông tư 09/2023/TT-BXD chia ba trường hợp:

1. Đã **thẩm duyệt xong** trước 01/12/2023 → tiếp tục theo hồ sơ đã thẩm duyệt.
2. Đã có **văn bản góp ý** ở bước thiết kế cơ sở nhưng chưa thẩm duyệt → thẩm
   duyệt theo văn bản góp ý đó.
3. Chưa góp ý và chưa thẩm duyệt → phải theo **cả QCVN 06:2022/BXD và Sửa đổi 1:2023**.

Nội dung kho hiện có của QCVN 06:2022/BXD:

- **Phụ lục A** — quy định bổ sung cho một số nhóm nhà (**A.4 đã bị bãi bỏ**);
- **Phụ lục B** — phân nhóm vật liệu xây dựng theo tính nguy hiểm cháy (Bảng B.1–B.9);
- **Phụ lục C** — phân hạng nguy hiểm cháy nổ A, B, C, D, E của gian phòng;
- **Phụ lục D** — yêu cầu bảo vệ chống khói (D.1–D.14);
- **Phụ lục E** — khoảng cách phòng cháy chống cháy;
- **Phụ lục F** — giới hạn chịu lửa danh định của cấu kiện (Bảng F.1–F.10);
- **Phụ lục G** — khoảng cách thoát nạn, chiều rộng lối ra, hệ số không gian sàn (Bảng G.9);
- **Phụ lục H** — số tầng và diện tích khoang cháy cho phép (Bảng H.1–H.5, cách tính ở H.6);
- **Phụ lục I** — hình minh họa cầu thang, buồng thang (Hình I.1–I.9).

**Phụ lục I chỉ là tham khảo**, không bắt buộc áp dụng; nó minh họa cho 2.4.2,
3.2.2, 3.2.8 và 3.4.10. Cần căn cứ ràng buộc thì trích điều khoản gốc ở phần
chính — ví dụ định nghĩa buồng thang L1/L2 nằm ở **mục 2.4.3.2**. Các phụ lục A
đến H đều là **quy định bắt buộc**.

Sửa đổi 1:2023 cũng **bổ sung THƯ MỤC TÀI LIỆU THAM KHẢO** (23 mục) sau Phụ lục I.
Các số `[1]`, `[5]`, `[8]`… rải rác trong bản sửa đổi trỏ về danh mục đó.

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

`eval/` có bộ 165 câu hỏi gán nhãn vàng (trong đó 10 câu cố tình nằm ngoài phạm
vi kho). Sau khi sửa `tools/search.py` hoặc thay đổi cách cắt chunk, **phải chạy
lại**:

```bash
python3 eval/chay_danh_gia.py            # chỉ số hiện hành
python3 eval/chay_danh_gia.py --so-sanh  # đối chứng với tokenizer cũ
python3 eval/chay_danh_gia.py --chi-tiet # liệt kê câu trượt
```

Mức hiện tại (165 câu, 5 văn bản, 682 chunk): Recall@1 = 0.556 · Recall@5 = 0.811 · Recall@10 = 0.887 · MRR = 0.713.
**Đừng merge một thay đổi làm các số này tụt** mà không có lý do đo được.
Điểm yếu đã biết: loại G (câu hỏi bắc cầu nhiều văn bản) = 0.17, loại I (câu hỏi
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
   - Điều khoản **không có tên** trong bản gốc (ví dụ QCVN 06 mục 4.1 đến
     4.35) vẫn viết thành `### 4.17` — bộ chia chấp nhận tiêu đề rỗng và tự
     suy một NHÃN từ câu đầu. Nhãn đó chỉ để hiển thị/tìm kiếm; trích dẫn pháp
     lý luôn dùng số hiệu mục.
   - Cắt đến cấp điều khoản nhỏ nhất có đánh số, đừng gộp cả mục lớn thành một
     chunk: một chunk 20 000 ký tự trùng gần như mọi từ khoá nên nó lấn át các
     chunk đúng của văn bản khác (đã đo: gộp cả mục làm Recall@1 tụt 0.06).
   - Phụ lục: khai báo `chia_theo` (`"Mẫu số"`, `"Bảng"`, `"H."`) để cắt theo
     tiêu đề cấp 2; không khai báo thì giữ nguyên cả phụ lục làm một chunk.
5. Nếu văn bản mới là **bản sửa đổi** của một văn bản đã có trong kho: khai
   `sua_doi_cho: ["<số hiệu bản gốc>"]` trong front matter, và **cắt chunk theo
   đúng số hiệu mục mà nó sửa** (`### 3.2.8`, `## A.2.12`). `build_index.py` sẽ
   tự ghép hai bên và gắn cờ `sua_doi_boi` lên chunk của bản gốc, `search.py` sẽ
   in cảnh báo. Nếu bản gốc cắt thô hơn (chỉ có `A.1` trong khi sửa đổi nhắm
   `A.1.2.1`) thì cờ được gắn lên mục cha gần nhất — không kéo ngược xuống các
   mục con. Tuyệt đối **không sửa chữ trong corpus của bản gốc** để "cập nhật"
   nó; corpus phải trung thành với bản in.
6. `python3 tools/build_index.py`
7. Thêm vài câu hỏi cho văn bản mới vào `eval/bo_cau_hoi.jsonl` rồi chạy lại
   `python3 eval/chay_danh_gia.py`.

## Hình vẽ

Hình vẽ trong quy chuẩn **không bao giờ được vẽ lại** bằng SVG/Mermaid để thay
bản gốc — vẽ lại là diễn giải lại, và một nét sai trong hình kỹ thuật là một quy
định sai. Cách làm: cắt hình gốc từ PDF vào `corpus/.../phu-luc/hinh/`, rồi chèn
vào Markdown bằng link kèm alt text mô tả để tìm kiếm được.

Kho hiện có 13 hình gốc của **Phụ lục I** ở
`corpus/quy-chuan/qcvn-06-2022-bxd/phu-luc/hinh/`. `tools/build_index.py` tự
viết lại link ảnh tương đối khi sinh chunk, nên trong `chunks/` đường dẫn vẫn
mở được — đừng sửa tay.

Hai lỗi đã mắc khi cắt Phụ lục I, tránh lặp lại:

- **Số hiệu mục không trùng số hiệu hình.** Trang 171 mở mục I.2 nhưng lại chứa
  Hình I.3. Phải đọc từng trang để lập bản đồ hình, đừng suy ra từ số trang.
- **Một hình có thể trải nhiều trang.** Hình I.8 chạy từ trang 176 đến 180 với
  các nhãn a) đến k) và dòng *(tiếp theo)* / *(kết thúc)*. Cắt thành nhiều file
  `-08a` đến `-08e` nhưng vẫn giữ chung một chú thích Hình I.8.
- **Khung cắt phải rộng hơn phần nhìn thấy.** Lần cắt đầu mất nhãn kích thước ở
  đỉnh và dòng chú thích ở đáy. Cách chắc ăn: cắt xong thì **mở lại ảnh bằng thị
  giác máy để xem có cụt không**, đừng tin vào toạ độ.

Chú thích hình trong QCVN có thể nằm **bên dưới hoặc bên phải** hình. Khi cắt
bằng `tools/cat_hinh.py` phải lấy **trọn bề ngang trang** (x từ 35 đến 588 pt với
khổ A4), nếu không sẽ mất phần chú thích bên phải. Mỗi hình vẽ thuộc về **chú
thích đầu tiên đứng sau nó**.

## Ngôn ngữ

Nội dung văn bản giữ nguyên **tiếng Việt**, không dịch. Có thể giải thích bằng
tiếng Anh nếu người dùng hỏi bằng tiếng Anh, nhưng phần trích dẫn luôn để
nguyên văn tiếng Việt kèm số Điều.

Khi trả lời người dùng này: viết **văn xuôi tự nhiên**, không phải bảng biểu khô
khan. Vẫn phải kèm trích dẫn đầy đủ.

**Quy tắc diễn đạt — người dùng đã yêu cầu rõ, áp dụng cho mọi câu trả lời:**

- **Không bao giờ viết tắt hoặc rút gọn từ.** Viết "phòng cháy chữa cháy", không
  viết "PCCC". Viết "giới hạn chịu lửa", không viết tắt. Ngoại lệ duy nhất là
  **phần trích dẫn nguyên văn** — trong dấu ngoặc kép phải giữ đúng chữ của bản
  gốc, kể cả khi bản gốc viết tắt (ví dụ bản gốc ghi "chiều cao PCCC" thì trích
  dẫn giữ nguyên "chiều cao PCCC").
- **Không dùng văn nói.** Không dùng cách xưng hô suồng sã, không chêm câu cảm
  thán, không viết những đoạn tán gẫu ngoài lề. Giữ giọng văn viết, trang trọng,
  đi thẳng vào nội dung.
- **Mọi thứ phải rõ ràng.** Nêu đủ số hiệu mục, đủ tên bảng, đủ tên văn bản. Khi
  một con số phụ thuộc điều kiện thì nêu điều kiện đó ra, đừng để người đọc tự
  đoán.
