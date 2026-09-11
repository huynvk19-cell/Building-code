# Thêm văn bản mới vào kho

Tệp này tách khỏi `CLAUDE.md` để `CLAUDE.md` chỉ còn những hàng rào phải bật
lên trong MỌI câu trả lời. Nội dung ở đây chỉ cần đọc khi bạn thật sự bắt tay
vào một trong ba việc: **số hóa một văn bản mới**, **cắt ảnh bảng hoặc hình**,
hoặc **sửa `tools/ingest_pdf_text.py`**.

**Đọc trọn tệp này trước khi làm, đừng đọc lướt.** Mọi mục dưới đây đều sinh ra
từ một lỗi có thật đã mắc, không phải lý thuyết phòng xa.

---

## Khi thêm văn bản mới

1. **Kiểm tra PDF có lớp văn bản thật không** — quyết định toàn bộ cách làm:

   ```bash
   python3 -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); \
     print(sum(1 for p in d if p.get_text().strip()), '/', len(d))" <file.pdf>
   ```

   - **Có lớp văn bản** (bản ký số, bản Công báo): dùng
     `python3 tools/ingest_pdf_text.py <file.pdf>` — trích thẳng, chính xác
     tuyệt đối, không qua OCR. Vẫn phải mở vài trang bằng thị giác máy để đối
     chiếu. Ba chế độ:
     - mặc định — nghị định, thông tư: nhận `Chương I` và `Điều 12. Tên điều`;
     - `--muc` — quy chuẩn, tiêu chuẩn: nhận `1. TÊN PHẦN`, `1.1 Tên mục`,
       `1.1.1 nội dung`;
     - `--phu-luc` — phụ lục: chỉ làm sạch đoạn, không tách tiêu đề.

     **Luôn đối chiếu số mục nhận được với số mục trong bản gốc** trước khi tin:

     ```bash
     grep -cE '^[0-9]+(\.[0-9]+)+ ' <bản trích thô>     # có trong PDF
     grep -c '^### ' <bản đã định dạng>                 # đã nhận
     ```

     Lệch là có mục bị nuốt. Đã gặp thật: phần "Giải thích từ ngữ" của
     QCVN 04:2021 đặt số hiệu **đứng một mình trên dòng** rồi mới tới thuật ngữ
     ở dòng sau, làm mất trọn 30 mục 1.4.1 đến 1.4.30 trước khi sửa.

     **Năm bẫy đã gặp thật khi trích quy chuẩn bằng `--muc`**, đều đã có hàng
     rào trong `tools/ingest_pdf_text.py`; đọc trước khi sửa các hàm đó:

     1. **Dải ký tự `[a-zà-ỹ]` nuốt cả CHỮ HOA tiếng Việt.** "Đ" là U+0110,
        "Ư" là U+01AF, "Ấ" là U+1EA4 — đều nằm giữa "à" (U+00E0) và "ỹ"
        (U+1EF9). Dùng dải đó để đoán "dòng nối tiếp" thì tiêu đề
        "1.2 Đối tượng áp dụng" bị coi là phần nối tiếp và mất tên mục. Phải
        dùng `str.islower()`, không dùng dải ký tự.
     2. **Tiêu đề mục là MỘT DÒNG RIÊNG trong bản in.** Nối dòng trước rồi mới
        tách thì không còn ranh giới để tách, mọi mục mất tên. Ràng buộc này y
        hệt ràng buộc đã phải đặt cho tên Điều của nghị định.
     3. **Một ô bảng có thể trông giống số hiệu mục.** Bảng chiều rộng đường
        của QCVN 01:2021/BXD có ô "2.400 - 4 000"; quy tắc "số hiệu phải tăng
        dần" đã nhận nó thành mục 2.400 rồi chặn mất 67 mục còn lại. Hàng rào
        đúng là `hop_le_tiep()`: chỉ cho **xuống một cấp bắt đầu từ 1**
        (2.9.3 → 2.9.3.1) hoặc **tăng 1 ở một cấp rồi dừng** (2.9.3.4 → 2.9.4).
     4. **Dòng thân bị ngắt trang có thể mở đầu bằng số hiệu.** Câu "…áp dụng
        quy định từ điểm 2.7.3 đến điểm 2.7.7 dưới đây" xuống dòng thành
        "2.7.3 đến điểm 2.7.7 dưới đây;" và sinh ra một mục 2.7.3 giả đứng ngay
        trước mục 2.7.3 thật. Chữ thường ngay sau số hiệu là dấu hiệu chắc chắn
        của phần nối tiếp.
     5. **Tiêu đề chạy của bản Công báo lọt vào giữa câu.** Sau khi nối dòng,
        corpus có những chỗ như "…đảm bảo CÔNG BÁO/Số 599 + 600/Ngày 31-5-2021
        QCVN 04:2021/BXD quy định…" — QCVN 04:2021/BXD từng dính 18 chỗ, đã gỡ.
        `RE_RAC` nay lọc trọn dòng `CÔNG BÁO/...` và dòng chỉ có số hiệu quy
        chuẩn; neo trọn dòng nên số hiệu nằm GIỮA câu văn không bị đụng tới.

     **Mục cha chỉ có tên vẫn phải thành chunk.** Mục như
     "2.6 Yêu cầu về kiến trúc cảnh quan…" không có thân riêng, nội dung nằm ở
     các mục con. `build_index.py` từng bỏ chúng vì thân rỗng — và thế là
     **phạm vi của cả nhánh biến mất khỏi chỉ mục**, đúng cơ chế đã gây ra lỗi
     trích nhầm mục 2.7.4 QCVN 10:2024/BXD. Nay tên mục được dùng làm thân
     chunk. Chi phí đo được: 0.005 Recall@1.

     **Tiêu đề bảng phải đứng riêng một dòng và in đậm** (`**Bảng 2.1: Tên**`),
     nếu không nó dính liền phần chữ trong ô bảng và `tools/chen_anh_bang.py`
     không nhận ra để gắn ảnh. Tiêu đề bảng thật luôn có dấu ngăn sau số hiệu
     (`:` hoặc `–`); câu viện dẫn "quy định tại Bảng 2.6;" thì không.
   - **Không có lớp văn bản** (bản quét): theo các bước 2 và 3 dưới đây.

2. `python3 tools/ingest_pdf.py <file.pdf> --ten <ma-van-ban>`
3. Đọc từng ảnh trang bằng **thị giác máy** và chép lại thành Markdown.
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
   - `cau_truc: "hoi-dap"` (tài liệu giải đáp nghiệp vụ):
     `## Nhóm 03. Tên nhóm` · `### HĐ-60 Nhãn`. Mỗi câu hỏi đáp là một chunk.
     Tài liệu loại này **bắt buộc** khai thêm `gia_tri_phap_ly` trong front
     matter — sự có mặt của trường đó là tín hiệu để `search.py` in cảnh báo
     và để `build_index.py` liệt kê các văn bản mà nó viện dẫn. Thiếu trường
     này thì tài liệu tham khảo sẽ bị đối xử như văn bản quy phạm pháp luật.
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

---

## HAI KIỂU BẢN SỬA ĐỔI — GHÉP KHÁC NHAU

Kho có hai kiểu bản sửa đổi, và cơ chế ghép phải phân biệt:

- **Kiểu quy chuẩn** (Sửa đổi 1:2023 QCVN 06:2022/BXD): chunk được đánh số theo
  **đúng số hiệu mục của bản gốc** (`### 3.2.8` sửa mục 3.2.8). Ghép thẳng theo
  `so_hieu_muc`.
- **Kiểu nghị định** (347/2026/NĐ-CP): chunk mang **số Điều của chính nó**, còn
  đích sửa nằm trong **tên điều**. Điều 10 của nó sửa Điều 1 của Nghị định
  105/2025; Điều 1 sửa khoản 5 Điều 31 của Nghị định 169/2025. Ghép theo
  `so_hieu_muc` ở đây sẽ **sai hoàn toàn**.

`build_index.py` có hàm `muc_tieu_sua_doi()` suy đích từ **tên Chương** (chứa số
hiệu văn bản bị sửa) và **tên Điều** (chứa số Điều bị sửa). Khi tên điều không
nhắm vào một Điều cụ thể ("Bãi bỏ một số quy định", "Thay thế một số cụm từ")
thì hàm trả về `None` và **bỏ qua** — thà bỏ sót còn hơn gắn cờ sai.

Một bản sửa đổi có thể nhắm **nhiều văn bản gốc cùng lúc**, nên `sua_doi_cho`
là danh sách và phải đọc trọn danh sách, đừng lấy phần tử đầu.

---

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

---

## Bảng tra — LUÔN KÈM ẢNH KHI TRÍCH DẪN

Người dùng đã yêu cầu rõ: **khi trích dẫn bảng nào thì cắt luôn ảnh bảng đó và
lưu vào kho.** Quy trình bắt buộc mỗi khi bạn trích một bảng:

1. Nêu **tên đầy đủ** của bảng, không chỉ số hiệu. Viết
   `Bảng G.2a - Khoảng cách giới hạn cho phép từ cửa ra vào của gian phòng đến
   lối ra thoát nạn gần nhất đối với nhà công cộng`, đừng viết trống không
   "Bảng G.2a".
2. Kiểm tra ảnh đã có chưa: `ls corpus/<văn bản>/phu-luc/bang/`.
3. Nếu **chưa có** thì cắt ngay bằng `tools/cat_bang.py`, mở lại ảnh bằng thị
   giác máy để chắc không bị cụt, rồi commit vào kho.
4. Gửi ảnh cho người dùng bằng công cụ gửi tệp.

```bash
# Tìm bảng nằm ở trang nào (in ra khung cắt gợi ý, chưa cắt)
python3 tools/cat_bang.py --pdf <goc.pdf> --tu-trang 50 --den-trang 70 \
    --dich <thu-muc> --chi-liet-ke

# Cắt cả một dải trang
python3 tools/cat_bang.py --pdf <goc.pdf> --tu-trang 56 --den-trang 65 \
    --dich corpus/quy-chuan/qcvn-06-2022-bxd/phu-luc/bang --tien-to bang

# Cắt tay một bảng khi khung tự động chưa đúng
python3 tools/cat_bang.py --pdf <goc.pdf> --trang 57 --bang G.2a \
    --y0 81 --y1 396 --dich <thu-muc> --tien-to bang
```

### Đã cắt sẵn — kiểm tra trước khi nghĩ tới việc cắt mới

Kho **đã có sẵn 160 ảnh bảng**, phủ **toàn bộ bảng của cả năm văn bản**, và
**cả 160 ảnh đều đã được chèn liên kết vào corpus** (kiểm lại bằng
`tools/chen_anh_bang.py`). Con số này từng là 122; một ảnh đã bị xoá vì bắt
nhầm câu văn xuôi thành bảng — xem phần bảng nhiều trang bên dưới:

| Văn bản | Thư mục ảnh | Số bảng |
|---|---|---|
| QCVN 06:2022/BXD phần chính | `corpus/quy-chuan/qcvn-06-2022-bxd/bang/` | 16 |
| QCVN 06:2022/BXD phụ lục | `corpus/quy-chuan/qcvn-06-2022-bxd/phu-luc/bang/` | 48 |
| QCVN 10:2025/BCA | `corpus/quy-chuan/qcvn-10-2025-bca/phu-luc/bang/` | 19 |
| QCVN 10:2024/BXD | `corpus/quy-chuan/qcvn-10-2024-bxd/phu-luc/bang/` | 2 |
| QCVN 01:2021/BXD | `corpus/quy-chuan/qcvn-01-2021-bxd/bang/` | 32 (39 ảnh, 7 bảng tràn trang) |

Mỗi ảnh đã được **chèn liên kết ngay dưới tiêu đề bảng** trong `corpus/`, nên
chunk trả về từ `search.py` đã mang sẵn đường dẫn ảnh. Chỉ việc gửi tệp đó cho
người dùng, **không cần cắt lại**.

**BẢNG NHIỀU TRANG: PHẢI GỬI ĐỦ CẢ CHUỖI.** Đây là lỗi đã mắc và bị người dùng
bắt: trích Bảng G.9 nhưng chỉ gửi `bang-g-9.png` (mục 1–6), trong khi mục 11 mà
câu trả lời đang dựa vào lại nằm ở `bang-g-9-tiep-1.png`. Trước khi gửi ảnh của
bất kỳ bảng nào, **luôn `ls` cả thư mục để xem có tệp `-tiep-N` không**, và gửi
trọn bộ theo đúng thứ tự. Ảnh cuối chuỗi phải là trang mang dòng *(kết thúc)*.

`tools/chen_anh_bang.py` giữ cho corpus không bị sót liên kết:

```bash
python3 tools/chen_anh_bang.py         # xem trước
python3 tools/chen_anh_bang.py --ghi   # chèn vào corpus
```

Công cụ này idempotent và **so sánh trọn bộ ảnh của một bảng với các liên kết đã
có**, chứ không dừng ở "đã có một ảnh thì thôi" — vì chính cách kiểm tra hời hợt
đó đã làm 48 liên kết trang tiếp theo bị thiếu mà không ai biết. Chạy lại nó sau
mỗi lần cắt thêm ảnh.

Bảng trải nhiều trang có thêm tệp hậu tố `-tiep-1`, `-tiep-2`, cũng đã được liên
kết cùng chỗ.

**RÀNG BUỘC PHẢI BIẾT:** cắt ảnh cần **bản PDF gốc**, mà PDF gốc nằm ở
`/root/.claude/uploads/<mã phiên>/` — thư mục này **thuộc về một phiên làm việc
và sẽ biến mất**. Vì vậy:

- Khi PDF gốc **còn** trong phiên: cắt ngay, càng nhiều càng tốt, và commit.
  Ảnh đã vào git thì tồn tại vĩnh viễn.
- Khi PDF gốc **không còn**: không thể cắt. Phải **nói thẳng với người dùng là
  ảnh chưa có trong kho và cần gửi lại tệp PDF gốc**, tuyệt đối không vẽ lại
  bảng rồi trình bày như ảnh chụp bản in.

Ảnh bảng lưu ở `corpus/<văn bản>/phu-luc/bang/`, đặt tên `bang-<số hiệu>.png`
(ví dụ `bang-g-2a.png`, `bang-h-7.png`). Trang nối tiếp thêm hậu tố
`-tiep-1`, `-tiep-2`. Thư mục này chỉ chứa ảnh nên `build_index.py` bỏ qua,
không làm đổi chỉ mục.

Chú thích hình trong QCVN có thể nằm **bên dưới hoặc bên phải** hình. Khi cắt
bằng `tools/cat_hinh.py` phải lấy **trọn bề ngang trang** (x từ 35 đến 588 pt với
khổ A4), nếu không sẽ mất phần chú thích bên phải. Mỗi hình vẽ thuộc về **chú
thích đầu tiên đứng sau nó**.
