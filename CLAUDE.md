# Hướng dẫn cho AI khi làm việc với kho này

Kho tra cứu **văn bản pháp luật xây dựng Việt Nam** (RAG corpus). Người dùng là
kiến trúc sư, cần trích dẫn chính xác chứ không cần diễn giải tự do.

Tệp này chỉ chứa **những hàng rào phải bật lên trong mọi câu trả lời**. Ba loại
việc còn lại có tệp riêng, đọc khi bắt tay vào làm:

Phần còn lại nằm trong **ba skill**, chỉ nạp vào ngữ cảnh khi được gọi — nhờ
vậy tệp này không phải mang chúng suốt phiên làm việc:

| Khi nào | Gọi skill |
|---|---|
| Câu hỏi chạm tới **an toàn cháy, thoát nạn, phòng cháy chữa cháy, karaoke, hoặc tiếp cận cho người khuyết tật** | **`an-toan-chay`** — BẮT BUỘC, gọi trước khi viết câu trả lời |
| Thêm văn bản mới · cắt ảnh bảng, hình · sửa `tools/ingest_pdf_text.py` | **`them-van-ban`** — BẮT BUỘC, chứa 5 bẫy đã mắc thật |
| Sửa `search.py`, `build_index.py`, đổi hằng số xếp hạng, bàn về vector database | **`do-luong-truy-hoi`** |

**Ba skill này không phải tài liệu tham khảo tùy chọn.** Mỗi cái chứa những điều
khoản đã bị bãi bỏ hoặc những bẫy kỹ thuật mà nếu không đọc thì câu trả lời sẽ
sai — sai một cách nghe rất hợp lý. Khi phân vân có nên gọi hay không, hãy gọi.

Hướng dẫn dành cho người dùng cuối (không phải cho bạn) ở `docs/huong-dan-su-dung.md`.

## Nguyên tắc trả lời — bắt buộc

1. **Luôn tra cứu trước khi trả lời.** Đừng trả lời từ trí nhớ; kiến thức nền
   của bạn có thể đã cũ hơn bản chính thức trong kho.
2. **Luôn trích dẫn**, dùng đúng chuỗi ở dòng `> **Trích dẫn:**` của file chunk,
   đừng tự chế. Ba dạng: `Điều 33 Nghị định số 212/2026/NĐ-CP` ·
   `mục 2.4.1 QCVN 10:2025/BCA` · `Bảng A.1 - Đối với nhà, Phụ lục A QCVN 10:2025/BCA`.
3. **Không suy diễn ngoài văn bản.** Kho không có thì nói *"kho hiện chưa có văn
   bản quy định việc này"*, đừng đoán.
4. **Trích nguyên văn mọi nội dung định lượng** (số năm kinh nghiệm, cấp công
   trình, thời hạn ngày làm việc). Đừng diễn đạt lại các con số.

## Quy trình kiểm chứng bắt buộc

`tools/search.py` **luôn trả về kết quả** miễn câu hỏi có một từ trùng với kho.
Điểm in ra là **điểm BM25 — đo mức trùng từ khóa, không đo mức liên quan**.

Đã đo, không phải phỏng đoán: điểm top-1 của câu **ngoài phạm vi kho** rơi vào
17,3–33,6, của câu **có đáp án thật** rơi vào 6,1–76,2 — **chồng lấn hoàn toàn**.
Vì vậy **không có ngưỡng tin cậy nào trong công cụ này**, và đừng thêm vào: một
nhãn tin cậy sai nguy hiểm hơn không có nhãn.

Trách nhiệm phân biệt "có đáp án" với "ngoài phạm vi" **thuộc về bạn**:

1. **Đọc nội dung chunk trả về**, không chỉ nhìn tiêu đề và điểm số.
2. **Tự hỏi BA câu, không phải một:**
   - **Đúng chủ đề?** Đoạn văn có thật sự chứa quy định về việc được hỏi không?
   - **Đúng không gian?** Trong nhà hay ngoài nhà, hành lang thoát nạn hay vỉa
     hè, gian phòng hay khoang cháy? Câu này **bắt buộc** — bỏ qua nó đã gây ra
     một lỗi có thật, xem mục "ĐỌC PHẠM VI" bên dưới.
   - **Đúng đối tượng và mục đích?** Bảo vệ ai, chống nguy cơ gì? Quy định chống
     va đầu cho người khiếm thị và quy định thoát nạn khi cháy dùng chung rất
     nhiều từ nhưng không thay thế được nhau.
3. Có → trích nguyên văn kèm số Điều/mục. Không → nói thẳng là kho chưa có, và
   nêu kho đang có những văn bản nào. **Tuyệt đối không** ghép các mảnh chỉ
   trùng từ khóa thành một câu trả lời nghe có vẻ hợp lý.
4. Câu hỏi thuộc lĩnh vực kho chưa bao phủ (tải trọng gió, chống sét, kết cấu,
   tiết kiệm năng lượng) → nói rõ ngay từ đầu.

Kho hiện có **mười văn bản quy phạm pháp luật có nội dung**, **một tài liệu tham
khảo** (hỏi đáp nghiệp vụ) và **năm khung rỗng**. Mặc định khi không chắc là
*"chưa có trong kho"*, không phải *"có lẽ là…"*.

## Kiểm tra hiệu lực

Mỗi chunk mang `ngay_ban_hanh`, `ngay_hieu_luc`, `het_hieu_luc`;
`index/documents.json` mang thêm `can_cu_hieu_luc`, `thay_the`, `sua_doi_boi`,
`dieu_khoan_chuyen_tiep`. **Luôn đọc `ngay_hieu_luc` trước khi tư vấn.**
`CHƯA XÁC ĐỊNH` → phải nói rõ kho không có căn cứ, tuyệt đối không suy đoán một
ngày cụ thể. `het_hieu_luc` có giá trị → phải cảnh báo.

| Văn bản | `ngay_hieu_luc` | Chuyển tiếp | Ghi chú |
|---|---|---|---|
| **212/2026/NĐ-CP** | `2026-07-01` (Điều 57 khoản 1) | **Điều 55** | Thay thế NĐ 111/2024. Đọc Điều 55 trước khi tư vấn cho hồ sơ nộp trước 01/7/2026. |
| **QCVN 06:2022/BXD** | `2023-01-16` (Điều 2 TT 06/2022/TT-BXD) | **mục 7.1** | Đủ mục 1–7 và Phụ lục A–I. ⚠️ **Đã bị Sửa đổi 1:2023 sửa nhiều điểm, có phần BỊ BÃI BỎ** — gọi skill `an-toan-chay`. |
| **Sửa đổi 1:2023 QCVN 06:2022/BXD** | `2023-12-01` (Điều 2 TT 09/2023/TT-BXD) | **Điều 3 TT 09/2023/TT-BXD** | **Không thay thế** bản gốc — phải đọc kèm. |
| **06/2021/TT-BXD** | `2021-08-15` (khoản 1 Điều 5) | **Điều 4** | **Phân cấp công trình xây dựng.** 5 Điều, 3 phụ lục, 6 bảng phân cấp. Thay thế TT 03/2016/TT-BXD. ⚠️ **ĐÃ BỊ Thông tư 02/2025/TT-BXD sửa 17 chỗ** — xem mục riêng bên dưới, BẮT BUỘC đọc trước khi kết luận cấp công trình. |
| **02/2025/TT-BXD** | `2025-05-20` (khoản 1 Điều 2) | **khoản 2, 3, 4 Điều 2** | Sửa đổi, bổ sung Thông tư 06/2021/TT-BXD. **Không thay thế** — phải đọc kèm bản gốc. |
| **QCVN 01:2021/BXD** | `2021-07-05` (Điều 2 TT 01/2021/TT-BXD) | **mục 3.4** | **Quy hoạch xây dựng.** 5 phần, 164 mục, 32 bảng. ⚠️ Viện dẫn QCVN 06:2021/BXD và QCVN 10:2014/BXD — cả hai đã bị thay thế; gọi `an-toan-chay`. |
| **QCVN 04:2021/BXD** | `2021-07-05` (Điều 2 TT 03/2021/TT-BXD) | không có | **Nhà chung cư.** ⚠️ Viện dẫn QCVN 06:2021/BXD (12 chỗ) và QCVN 10:2014/BXD (7 chỗ) — cả hai đã bị thay thế; gọi `an-toan-chay`. |
| **QCVN 10:2024/BXD** | `CHƯA XÁC ĐỊNH` | mục 3.1 | Hiệu lực nằm ở Thông tư 06/2024/TT-BXD — **chưa có trong kho**. |
| **QCVN 10:2025/BCA** | `CHƯA XÁC ĐỊNH` | không có | Hiệu lực nằm ở Thông tư 103/2025/TT-BCA — **chưa có trong kho**. Hỏi đáp nói 30/12/2025, đã ghi vào `ngay_hieu_luc_theo_tham_khao` nhưng **chưa coi là đã chứng minh**. |
| **347/2026/NĐ-CP** | `2026-09-15` (Điều 41 khoản 1) | **Điều 40** | Sửa 4 nghị định: 169/2025, **105/2025**, 106/2025, 282/2025. Bãi bỏ Điều 74 NĐ 217/2026. ⚠️ Điều 41 khoản 2 có hiệu lực cùng Luật sửa đổi Luật Phòng cháy chữa cháy — ngày đó **CHƯA XÁC ĐỊNH**. |
| **105/2025 · 106/2025 · 169/2025 · 282/2025 · 217/2026** | `CHƯA XÁC ĐỊNH` | — | **KHUNG RỖNG — chưa có nội dung.** |
| **Hỏi đáp C07** | `KHÔNG ÁP DỤNG` | không có | **KHÔNG phải văn bản quy phạm pháp luật.** 132 giải đáp, không mục nào có ngày trả lời. |

## PHÂN CẤP CÔNG TRÌNH — ĐỌC KÈM THÔNG TƯ 02/2025/TT-BXD

Cấp công trình quyết định thẩm quyền thẩm định, điều kiện năng lực nhà thầu, thời
hạn bảo hành và nhiều thủ tục khác, nên trả lời sai cấp là sai cả đường đi hồ sơ.

Kho có **hai văn bản** cho cùng một chế định:

- **Thông tư 06/2021/TT-BXD** — bản gốc, hiệu lực 15/8/2021. Đủ 5 Điều, Phụ lục I
  (Bảng 1.1 đến 1.5, phân cấp theo mức độ quan trọng hoặc quy mô công suất),
  Phụ lục II (Bảng 2, phân cấp theo quy mô kết cấu), Phụ lục III (15 ví dụ).
- **Thông tư 02/2025/TT-BXD** — hiệu lực **20/5/2025**, sửa 17 chỗ. **Không thay
  thế** bản gốc; quy định đang có hiệu lực = bản gốc đã vá bằng bản sửa đổi.

### Vì sao ở đây KHÔNG có cảnh báo tự động trên từng chunk

Với QCVN 06, `search.py` in cảnh báo `⚠️ ĐÃ BỊ SỬA ĐỔI` trên từng mục vì bản sửa
đổi đánh số theo đúng số hiệu mục của bản gốc. Thông tư 02/2025/TT-BXD thì đánh
số Điều **của chính nó**, còn đích sửa nằm trong tên mục phụ lục ("Sửa đổi, bổ
sung mục 1.1.3.3 Bảng 1.1 Phụ lục I"), mà chunk phụ lục của bản gốc lại không
mang số hiệu mục để ghép. Ghép bừa theo số thứ tự đã gắn nhầm "Điều 2. Điều khoản
thi hành" của bản sửa đổi lên "Điều 2. Nguyên tắc xác định cấp công trình" của
bản gốc — `build_index.py` nay chặn việc đó. **Bảng dưới đây thay cho cảnh báo tự
động: đọc nó mỗi khi tra cấp công trình.**

### 17 chỗ đã bị sửa — tra trước khi trích Thông tư 06/2021/TT-BXD

| Đích trong Thông tư 06/2021/TT-BXD | Thông tư 02/2025/TT-BXD làm gì |
|---|---|
| khoản 1 Điều 1 · khoản 4 Điều 2 · khoản 3 Điều 3 | sửa phạm vi điều chỉnh; **bổ sung khoản 5, 6, 7 Điều 2** (kết cấu độc lập, dự án phân kỳ đầu tư) và **khoản 4, 5 Điều 3** |
| mục 1.1.3.3 Bảng 1.1 | Sân gôn — sửa |
| mục 1.2.1.2 · 1.2.1.12 Bảng 1.2 | nhà máy xi măng, vôi công nghiệp — sửa |
| **mục 1.2.1.3 Bảng 1.2** | **BÃI BỎ — tuyệt đối không trích** |
| điểm 2, 3 phần Ghi chú mục 1.2.5.3 Bảng 1.2 | tuyến năng lượng, tuyến đầu mối — sửa |
| mục 1.2.5.8 Bảng 1.2 | công trình điện rác — sửa |
| mục 1.2.6.9 Bảng 1.2 | kho chứa hóa chất nguy hiểm — **bổ sung mới** |
| mục 1.3.10 Bảng 1.3 | công trình lấn biển — **bổ sung mới** |
| mục 1.4.1.1 · 1.4.1.2 Bảng 1.4 | đường ô tô cao tốc, đường ô tô — sửa |
| mục 1.4.2.4 · 1.4.4.5 · điểm b mục 1.4.5.4 · mục 1.4.6.3 Bảng 1.4 | đường sắt chuyên dụng, đường thủy, công trình hàng hải, bảo đảm hoạt động bay — sửa |
| mục 1.5.1.4 đến 1.5.1.8 Bảng 1.5 | trạm bơm, cống đồng bằng, hệ thống dẫn nước, đường ống, bờ bao — **bổ sung mới** |
| mục 2.5 · 2.11 · 2.12 Bảng 2 Phụ lục II | cầu, cảng biển, cảng đường thủy nội địa — sửa |
| mục 3.13, 3.14, 3.15 Phụ lục III | **bổ sung 3 ví dụ mới**: ga hành khách đường sắt, khu bay hàng không, đường cao tốc phân kỳ đầu tư |

Trích một trong các mục trên mà chỉ dựa vào Thông tư 06/2021/TT-BXD là **trích
quy định đã hết hiệu lực**. Khi trích phải ghi cả hai, ví dụ:

> Theo mục 1.1.3.3 Bảng 1.1 Phụ lục I Thông tư số 06/2021/TT-BXD, được sửa đổi
> bởi Mục 1 Phụ lục Thông tư số 02/2025/TT-BXD (hiệu lực 20/5/2025), sân gôn từ
> 18 lỗ trở lên là công trình cấp II.

## KHUNG RỖNG — VĂN BẢN CHỈ CÓ TÊN, CHƯA CÓ NỘI DUNG

Năm khung rỗng ở `corpus/nghi-dinh/`: 105/2025, 106/2025, 169/2025, 282/2025,
217/2026. Chúng mang `trang_thai: "KHUNG RỖNG"`, chỉ có tên và số hiệu, không
một điều khoản nào — để khi tra thì kho nói thẳng *chưa có nội dung* thay vì trả
về rỗng khiến người trả lời tưởng là "pháp luật không quy định".

```
📭  KHUNG RỖNG — kho CHƯA CÓ NỘI DUNG của văn bản này.
```

**Thấy dòng đó thì tuyệt đối không trích gì từ chunk ấy**, phải nói kho thiếu văn
bản này và đề nghị người dùng cung cấp bản gốc. Khung rỗng **không** được tính là
"đã có trong kho".

## HỎI ĐÁP NGHIỆP VỤ — KINH NGHIỆM THỰC CHIẾN, KHÔNG PHẢI CĂN CỨ PHÁP LÝ

**132 giải đáp** của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ, tại
`corpus/huong-dan/hoi-dap-c07/`. Giá trị của nó là cho biết **cơ quan thẩm duyệt
thực tế đang hiểu và áp dụng quy định như thế nào** — thứ đọc trần quy chuẩn
không thấy được.

1. **Không bao giờ trích giải đáp làm căn cứ pháp lý.** Căn cứ luôn là văn bản
   quy phạm pháp luật mà giải đáp đó viện dẫn.
2. **Luôn nói rõ đây là tài liệu tham khảo**, dùng đúng chuỗi trích dẫn đã mang
   sẵn cảnh báo.
3. **Không mục nào có ngày trả lời**, nên không biết nó viết theo văn bản nào
   còn hiệu lực tại thời điểm nào. `search.py` in ba loại cảnh báo:
   ```
   🛑  THAM KHẢO - KHÔNG PHẢI VĂN BẢN QUY PHẠM PHÁP LUẬT — KHÔNG ĐƯỢC dùng làm căn cứ pháp lý.
   ⚠️  Viện dẫn QCVN 06:2021/BXD — kho xác định văn bản này ĐÃ BỊ THAY THẾ bởi QCVN 06:2022/BXD.
   ⚠️  Viện dẫn văn bản KHÔNG CÓ TRONG KHO: TCVN 3890:2009, TCVN 3890:2023
   ```
4. **Không suy rộng từ một trường hợp cụ thể.** Đừng biến câu trả lời cho một
   nhà ở 60 m² bán hàng ăn sáng thành quy tắc chung.

**Khoảng trống lớn nhất, đã đo:** 72 trên 132 giải đáp viện dẫn **Nghị định số
105/2025/NĐ-CP**, văn bản chưa có trong kho. Danh sách tài liệu nên đề nghị bổ
sung theo thứ tự ưu tiên: `105/2025/NĐ-CP` · `50/2024/NĐ-CP` (15 lần) ·
`136/2020/NĐ-CP` (13) · `TCVN 3890:2023` (11) · `36/2025/TT-BCA` (11) · Luật
`55/2024/QH15` (10). Phân tích đầy đủ trong skill `do-luong-truy-hoi`.

## ĐỌC PHẠM VI CỦA MỤC LỚN TRƯỚC KHI TRÍCH ĐIỀU KHOẢN CON

Số hiệu điều khoản **không cho biết nó điều chỉnh không gian nào**.

**Lỗi đã mắc, người dùng bắt được:** đặt mục 2.7.4 QCVN 10:2024/BXD cạnh mục
3.3.5 QCVN 06:2022/BXD như hai quy định song song. Thực tế 2.7.4 nằm trong **mục
2.7 "Đường và hè phố"** — quy định cho **vỉa hè ngoài nhà**, và hình minh họa nó
tên đầy đủ là *"Hình 17 – Minh họa về kích thước lắp đặt các vật cản trên lối đi
an toàn cho **người khuyết tật nhìn**"*, tức chống va đầu cho người khiếm thị,
không liên quan gì tới thoát nạn khi cháy. Nặng hơn nữa, mục 2.6.2.2 của chính
QCVN 10:2024/BXD giao trọn đường thoát nạn cho QCVN 06:2022/BXD.

**Nguyên nhân gốc:** tôi đọc bằng `grep` trên file phẳng, nơi điều khoản đã bị
cắt rời khỏi tiêu đề mục. Phạm vi "Đường và hè phố" **vốn có sẵn trong chỉ mục**;
công cụ đã có câu trả lời, tôi không hỏi.

### Cách làm bắt buộc

1. Trước khi trích một mục con, **chạy `tools/tra_muc.py <số hiệu>`** và đọc dòng
   PHẠM VI cùng dòng Mục cha. Khi tiêu đề không đủ để kết luận, công cụ nói thẳng
   *"không suy được từ tiêu đề — PHẢI TỰ ĐỌC"* thay vì đoán.
2. **Đọc đủ tên hình, tên bảng**, không cắt ngắn — cụm bị cắt thường chính là cụm
   phân biệt phạm vi.
3. Đặt hai điều khoản cạnh nhau thì **hỏi trước: chúng có cùng điều chỉnh một
   không gian và một mục đích không?**
4. Kiểm tra văn bản này có **giao việc cho văn bản kia** không. Trích chéo khi
   một quy chuẩn đã tự tuyên bố không điều chỉnh chủ đề đó luôn là sai.

## Hai văn bản trùng số hiệu "QCVN 10"

**QCVN 10:2024/BXD** (Bộ Xây dựng) là tiếp cận sử dụng cho người khuyết tật;
**QCVN 10:2025/BCA** (Bộ Công an) là trang bị phương tiện phòng cháy chữa cháy.
Nội dung khác hẳn nhau, nên khi trích **phải ghi đủ đuôi `/BXD` hoặc `/BCA`**.
Gặp cảnh báo `⚠ Kết quả chỉ đến từ QCVN 10:.../...` thì hỏi lại người dùng cần
văn bản nào. Bản đồ phạm vi trong nhà hay ngoài nhà của QCVN 10:2024/BXD nằm
trong skill `an-toan-chay`.

## Cách tra cứu

> **`grep` CHỈ ĐỂ ĐỊNH VỊ, KHÔNG BAO GIỜ ĐỂ KẾT LUẬN.** `grep` trên
> `corpus/.../toan-van.md` trả về một dòng **đã bị cắt rời khỏi tiêu đề mục**,
> tức mất luôn phạm vi áp dụng — đúng cơ chế đã gây lỗi mục 2.7.4. Định vị xong
> thì **bắt buộc** mở lại bằng `tools/tra_muc.py` hoặc đọc file chunk.

```bash
# 0. Tra một điều khoản đã biết số hiệu, KÈM PHẠM VI — chạy trước khi trích
python3 tools/tra_muc.py 2.7.4 --doc qcvn-10-2024-bxd
python3 tools/tra_muc.py 3.3.6          # in tiêu đề mục, mục cha, cờ sửa đổi, ảnh kèm
python3 tools/tra_muc.py G.9            # tra bảng

# 1. Tìm theo từ khóa — mặc định IN ĐẦY ĐỦ NỘI DUNG vì bạn buộc phải đọc mới kết luận được
python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề hạng II"
python3 tools/search.py --gon "thu hồi giấy phép"                 # chỉ tiêu đề, để duyệt nhanh
python3 tools/search.py --doc qcvn-10-2025-bca "bình chữa cháy"   # khoanh một văn bản
python3 tools/search.py --khong-dau "chung chi hanh nghe"         # gõ không dấu

# 2. Đọc thẳng một Điều / mục / bảng đã biết
cat chunks/212-2026-nd-cp/dieu-33-*.md
cat chunks/qcvn-10-2025-bca/phu-luc-a-01-*.md      # Bảng A.1
```

`--gon` chỉ dùng khi đang duyệt để chọn chunk đáng đọc; **không bao giờ kết luận
từ tiêu đề**. `index/chunks.jsonl` chứa toàn bộ chunk kèm metadata cho script;
`index/documents.json` là sổ đăng ký văn bản.

## Cấu trúc kho và quy trình đẩy lên `main`

```
corpus/quy-chuan/  corpus/nghi-dinh/   văn bản quy phạm pháp luật — CHỈ sửa ở đây
corpus/huong-dan/                      tài liệu THAM KHẢO, không có giá trị pháp lý
chunks/  index/                        sinh tự động — KHÔNG sửa tay
eval/    tools/    docs/
.claude/skills/                        ba skill nạp theo yêu cầu — xem bảng đầu tệp
```

Người dùng đã chọn rõ: **đẩy thẳng lên `main`**, không nhánh phụ, không pull
request. Vì không còn cửa kiểm tra của người dùng, **bốn bước sau là bắt buộc
trước mỗi lần đẩy**:

```bash
python3 tools/build_index.py        # 1. dựng lại chỉ mục, phải chạy sạch
python3 tools/build_index.py        # 2. chạy lần hai, kết quả phải giống hệt
python3 eval/chay_danh_gia.py       # 3. không có dòng LỖI, chỉ số không tụt
python3 tools/chen_anh_bang.py      # 4. không còn liên kết ảnh nào bị sót
```

**Bước 5 — cập nhật `README.md`** khi thay đổi chạm tới: danh sách văn bản trong
kho, số chunk, số ảnh, chỉ số truy hồi, hoặc danh sách công cụ. README là tệp
duy nhất người dùng đọc để biết kho có gì; nó đã từng lạc hậu qua **sáu lần bổ
sung văn bản** vì bốn bước trên không có bước nào đụng tới nó, còn `CLAUDE.md`
thì được cập nhật đều vì đó là tệp AI đọc. Hai tệp có hai người đọc khác nhau,
nên phải cập nhật cả hai.

Chỉ số tụt mà không giải thích được bằng phép đo thì **không đẩy**. Thay đổi
**đụng tới nội dung corpus của văn bản pháp luật** thì còn phải kiểm chứng bằng
thị giác máy đối chiếu bản gốc — đây là loại lỗi mà chỉ số truy hồi không bắt được.

Mức truy hồi hiện tại (225 câu, 16 văn bản, 1 303 chunk): Recall@1 = 0,555 ·
Recall@3 = 0,796 · Recall@5 = 0,845 · Recall@10 = 0,891 · MRR = 0,701. Trước khi
đổi bất kỳ hằng số xếp hạng nào, **gọi skill `do-luong-truy-hoi`** — mỗi con
số ở đó đến từ một phép quét dải giá trị, không phải cảm tính.

## Ngôn ngữ và cách trình bày

Nội dung văn bản giữ nguyên **tiếng Việt**, không dịch. Viết **văn xuôi tự
nhiên**, không phải bảng biểu khô khan, nhưng luôn kèm trích dẫn đầy đủ.

Bốn quy tắc người dùng đã yêu cầu rõ, áp dụng cho **mọi** câu trả lời:

- **Không bao giờ viết tắt hoặc rút gọn từ.** Viết "phòng cháy chữa cháy", không
  viết "PCCC"; viết "giới hạn chịu lửa", không viết tắt. Ngoại lệ duy nhất là
  **phần trích dẫn nguyên văn** — trong ngoặc kép phải giữ đúng chữ bản gốc, kể
  cả khi bản gốc viết tắt.
- **Không dùng văn nói.** Không xưng hô suồng sã, không chêm câu cảm thán, không
  tán gẫu ngoài lề. Giữ giọng văn viết, trang trọng, đi thẳng vào nội dung.
- **Mọi thứ phải rõ ràng.** Đủ số hiệu mục, đủ tên bảng, đủ tên văn bản. Con số
  phụ thuộc điều kiện thì nêu điều kiện ra, đừng để người đọc tự đoán.
- **Ảnh phải đi NGAY SAU nội dung mà nó minh họa, không gom lại một chỗ.** Nguyên
  văn yêu cầu: *"luôn cung cấp hình ảnh của các nội dung ngay sau nó nếu có"*.
  Trước khi viết, **rà xem mỗi mục, bảng, hình sắp trích có ảnh trong kho không**
  (`tra_muc.py` in sẵn danh sách). Viết đoạn trích → **gửi ảnh của đúng đoạn đó
  ngay** → mới viết tiếp. Gửi dồn ảnh ở đầu hoặc cuối là SAI.

  **BẢNG NHIỀU TRANG: PHẢI GỬI ĐỦ CẢ CHUỖI.** Lỗi đã mắc và bị người dùng bắt:
  trích Bảng G.9 nhưng chỉ gửi `bang-g-9.png` (mục 1–6), trong khi mục 11 mà câu
  trả lời đang dựa vào nằm ở `bang-g-9-tiep-1.png`. Trước khi gửi ảnh bất kỳ bảng
  nào, **luôn `ls` cả thư mục để xem có tệp `-tiep-N` không**, gửi trọn bộ theo
  đúng thứ tự.

  Trích điều khoản có dẫn chiếu hình (mục 3.2.8 dẫn Hình I.3, I.4, I.5; mục
  3.4.10 dẫn Hình I.7, I.8) thì **phải gửi kèm các hình đó**, không chỉ gửi bảng.

  Kho hiện có **200 ảnh bảng** và **13 hình** của Phụ lục I, tất cả đã được chèn
  liên kết vào corpus nên chunk trả về đã mang sẵn đường dẫn — chỉ việc gửi tệp,
  **không cần cắt lại**. Chưa có ảnh thì **nói thẳng là chưa có và cần bản PDF
  gốc**, tuyệt đối không vẽ lại bảng hay hình rồi trình bày như ảnh chụp bản in.
  Cách cắt ảnh mới: gọi skill `them-van-ban`.
