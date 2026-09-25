---
name: tra-cuu-hieu-luc
description: >-
  Quy trình tra cứu, kiểm chứng và kiểm tra hiệu lực cho MỌI câu trả lời về nội
  dung quy định: bảng hiệu lực và điều khoản chuyển tiếp của từng văn bản trong
  kho, cách đọc điểm BM25, năm khung rỗng chưa có nội dung, 132 giải đáp nghiệp
  vụ chỉ là tài liệu tham khảo, cách đọc phạm vi mục lớn trước khi trích điều
  khoản con, và các lệnh tra cứu. BẮT BUỘC gọi skill này TRƯỚC KHI trả lời bất kỳ
  câu hỏi nào hỏi nội dung quy định (được phép hay không, bao nhiêu mét, điều
  kiện gì, hồ sơ gì, áp dụng từ ngày nào), trước khi trích một Điều, mục, bảng,
  hoặc khi kết quả tìm kiếm mang cảnh báo KHUNG RỖNG, THAM KHẢO, CHƯA XÁC ĐỊNH.
  Bỏ qua nó là cách nhanh nhất để trích một văn bản chưa có hiệu lực hoặc ghép
  các mảnh chỉ trùng từ khóa thành câu trả lời nghe hợp lý.
---

# Tra cứu, kiểm chứng và kiểm tra hiệu lực

Tách khỏi `CLAUDE.md` để tệp đó chỉ còn hàng rào thường trực. Nội dung dưới đây
là chi tiết của các nguyên tắc 3 đến 6 trong `CLAUDE.md`.

## Quy trình kiểm chứng bắt buộc

`tools/search.py` **luôn trả về kết quả** miễn câu hỏi có một từ trùng với kho.
Điểm in ra là **điểm BM25 — đo mức trùng từ khóa, không đo mức liên quan**.

Đã đo, không phải phỏng đoán: điểm top-1 của câu **ngoài phạm vi kho** rơi vào
17,4–47,1, của câu **có đáp án thật** rơi vào 6,3–87,5 — **chồng lấn hoàn toàn**.
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

Kho hiện có **mười một văn bản quy phạm pháp luật có nội dung**, **một văn bản
hợp nhất**, **hai tài liệu tham khảo** (hỏi đáp nghiệp vụ và quyết định công bố
thủ tục hành chính) và **năm khung rỗng**. Mặc định khi không chắc là
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
| **06/2021/TT-BXD** | `2021-08-15` (khoản 1 Điều 5) | **Điều 4** | **Phân cấp công trình xây dựng.** 5 Điều, 3 phụ lục, 6 bảng phân cấp. Thay thế TT 03/2016/TT-BXD. ⚠️ **ĐÃ BỊ Thông tư 02/2025/TT-BXD sửa 17 chỗ** — BẮT BUỘC gọi skill `phan-cap-cong-trinh` trước khi kết luận cấp công trình. |
| **02/2025/TT-BXD** | `2025-05-20` (khoản 1 Điều 2) | **khoản 2, 3, 4 Điều 2** | Sửa đổi, bổ sung Thông tư 06/2021/TT-BXD. **Không thay thế** — phải đọc kèm bản gốc. |
| **QCVN 01:2021/BXD** | `2021-07-05` (Điều 2 TT 01/2021/TT-BXD) | **mục 3.4** | **Quy hoạch xây dựng.** 5 phần, 164 mục, 32 bảng. ⚠️ Viện dẫn QCVN 06:2021/BXD và QCVN 10:2014/BXD — cả hai đã bị thay thế; gọi `an-toan-chay`. |
| **QCVN 04:2021/BXD** | `2021-07-05` (Điều 2 TT 03/2021/TT-BXD) | không có | **Nhà chung cư.** ⚠️ Viện dẫn QCVN 06:2021/BXD (12 chỗ) và QCVN 10:2014/BXD (7 chỗ) — cả hai đã bị thay thế; gọi `an-toan-chay`. |
| **QCVN 10:2024/BXD** | `CHƯA XÁC ĐỊNH` | mục 3.1 | Hiệu lực nằm ở Thông tư 06/2024/TT-BXD — **chưa có trong kho**. |
| **QCVN 10:2025/BCA** | `CHƯA XÁC ĐỊNH` | không có | Hiệu lực nằm ở Thông tư 103/2025/TT-BCA — **chưa có trong kho**. Hỏi đáp nói 30/12/2025, đã ghi vào `ngay_hieu_luc_theo_tham_khao` nhưng **chưa coi là đã chứng minh**. |
| **347/2026/NĐ-CP** | `2026-09-15` (Điều 41 khoản 1) | **Điều 40** | Sửa 4 nghị định: 169/2025, **105/2025**, 106/2025, 282/2025. Bãi bỏ Điều 74 NĐ 217/2026. ⚠️ Điều 41 khoản 2 có hiệu lực cùng Luật sửa đổi Luật Phòng cháy chữa cháy — ngày đó **CHƯA XÁC ĐỊNH**. |
| **40/2019/QH14** | `2020-07-01` (Điều 40) | **Điều 41** | **Luật Kiến trúc.** 5 Chương, 41 Điều. Điều 39 sửa Luật Xây dựng, Luật Quy hoạch đô thị, Luật Nhà ở, Luật Đấu thầu; **bãi bỏ Điều 81 Luật Xây dựng và Điều 60 Luật Quy hoạch đô thị**. |
| **25/VBHN-BXD** | `2020-09-07` (Điều 32 NĐ 85/2020) | **Điều 33** | **VĂN BẢN HỢP NHẤT**, không tự nó là văn bản quy phạm pháp luật — gọi skill `hanh-nghe-kien-truc`. |
| **105/2025 · 106/2025 · 169/2025 · 282/2025 · 217/2026** | `CHƯA XÁC ĐỊNH` | — | **KHUNG RỖNG — chưa có nội dung.** |
| **975/QĐ-BXD** | `2026-07-01` (Điều 2) | không có | **KHÔNG phải văn bản quy phạm pháp luật** — quyết định công bố thủ tục hành chính. Bãi bỏ 6 thủ tục hành chính lĩnh vực kiến trúc. Căn cứ thật sự là **Nghị quyết 66.18/2026/NQ-CP — chưa có trong kho**. Gọi skill `hanh-nghe-kien-truc`. |
| **Hỏi đáp C07** | `KHÔNG ÁP DỤNG` | không có | **KHÔNG phải văn bản quy phạm pháp luật.** 132 giải đáp, không mục nào có ngày trả lời. |

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
