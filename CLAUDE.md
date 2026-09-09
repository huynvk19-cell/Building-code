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
(`eval/`), điểm top-1 của các câu **ngoài phạm vi kho** rơi vào 7.1–32.3, còn
của các câu **có đáp án thật** rơi vào 4.6–66.2. Hai dải **chồng lấn hoàn toàn**.
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
   vì cố nặn ra câu trả lời từ bốn văn bản đang có.

Kho hiện **chỉ có bốn văn bản**. Mặc định của bạn khi không chắc phải là *"chưa
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
| **QCVN 06:2022/BXD** | `2023-01-16` (Điều 2 Thông tư 06/2022/TT-BXD) | **mục 7.1** | Thay thế QCVN 06:2021/BXD. Hồ sơ đã thẩm duyệt trước 16/01/2023 vẫn theo hồ sơ cũ. Đã có **đủ mục 1–7 và Phụ lục A–I**. |
| **QCVN 10:2024/BXD** | `CHƯA XÁC ĐỊNH` | mục 3.1 | Hiệu lực nằm ở Thông tư 06/2024/TT-BXD — **chưa có trong kho**. |
| **QCVN 10:2025/BCA** | `CHƯA XÁC ĐỊNH` | không có trong bản Quy chuẩn | Hiệu lực nằm ở Thông tư 103/2025/TT-BCA — **chưa có trong kho**. |

## QCVN 06:2022/BXD — đã đủ phần chính và toàn bộ Phụ lục A–I

Kho đã số hóa **mục 1 đến mục 7** (phần chính) và **toàn bộ Phụ lục A đến I**,
kể cả các bảng tra hay dùng nhất:

- **Phụ lục A** — quy định bổ sung cho một số nhóm nhà (A.4 là karaoke, vũ trường);
- **Phụ lục B** — phân nhóm vật liệu xây dựng theo tính nguy hiểm cháy
  (Bảng B.1 đến B.9, được viện dẫn ở 2.1, 3.3.4, 3.5.2, 3.5.3);
- **Phụ lục C** — phân hạng nguy hiểm cháy nổ A, B, C, D, E của gian phòng;
- **Phụ lục D** — yêu cầu bảo vệ chống khói (D.1 đến D.14);
- **Phụ lục E** — khoảng cách phòng cháy chống cháy giữa các nhà;
- **Phụ lục F** — giới hạn chịu lửa danh định của cấu kiện (Bảng F.1 đến F.10);
- **Phụ lục G** — khoảng cách thoát nạn, chiều rộng lối ra, hệ số không gian
  sàn (Bảng G.9);
- **Phụ lục H** — số tầng và diện tích khoang cháy cho phép theo nhóm nhà
  (Bảng H.1 đến H.5, cách tính diện tích khoang cháy ở H.6);
- **Phụ lục I** — hình minh họa cầu thang, buồng thang và khoảng đệm không
  nhiễm khói (Hình I.1 đến I.9).

Hai điều cần nhớ khi trả lời:

1. **Phụ lục I chỉ là tham khảo**, không bắt buộc áp dụng. Nó minh họa cho
   2.4.2, 3.2.2, 3.2.8 và 3.4.10. Khi cần căn cứ ràng buộc thì trích điều
   khoản gốc ở phần chính, đừng trích Phụ lục I. Ví dụ định nghĩa buồng thang
   L1/L2 nằm ở **mục 2.4.3.2**, còn Phụ lục I chỉ vẽ lại cho dễ hình dung.
   Các phụ lục A, B, C, D, E, F, G, H đều là **quy định (bắt buộc)**.
2. **Bản số hóa vẫn thiếu Sửa đổi 1:2023** (nếu có) và mọi văn bản sửa đổi sau
   ngày 30/11/2022 — kho chỉ có bản gốc QCVN 06:2022/BXD.

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

`eval/` có bộ 141 câu hỏi gán nhãn vàng (trong đó 10 câu cố tình nằm ngoài phạm
vi kho). Sau khi sửa `tools/search.py` hoặc thay đổi cách cắt chunk, **phải chạy
lại**:

```bash
python3 eval/chay_danh_gia.py            # chỉ số hiện hành
python3 eval/chay_danh_gia.py --so-sanh  # đối chứng với tokenizer cũ
python3 eval/chay_danh_gia.py --chi-tiet # liệt kê câu trượt
```

Mức hiện tại (141 câu, 4 văn bản, 536 chunk): Recall@1 = 0.550 · Recall@5 = 0.822 · Recall@10 = 0.882 · MRR = 0.708.
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
5. `python3 tools/build_index.py`
6. Thêm vài câu hỏi cho văn bản mới vào `eval/bo_cau_hoi.jsonl` rồi chạy lại
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

Khi trả lời người dùng này: viết **văn xuôi tự nhiên, gần gũi như một trợ lý con
người**, không phải bảng biểu khô khan. Vẫn phải kèm trích dẫn đầy đủ — chỉ khác
ở giọng văn, không khác ở độ chính xác.
