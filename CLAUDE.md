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

Kho hiện có **năm văn bản quy phạm pháp luật** và **một tài liệu tham khảo**
(hỏi đáp nghiệp vụ — xem mục riêng bên dưới). Mặc định của bạn khi không chắc
phải là *"chưa có trong kho"*, không phải *"có lẽ là…"*.

**Tài liệu tham khảo không bao giờ là căn cứ pháp lý.** Nếu chỉ tìm được câu trả
lời trong phần hỏi đáp mà không có điều khoản nào chống lưng, phải nói thẳng
rằng kho chưa có căn cứ quy phạm cho việc này, và nêu rõ phần hỏi đáp chỉ cho
biết cơ quan quản lý đang hiểu quy định như thế nào.

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
| **QCVN 10:2025/BCA** | `CHƯA XÁC ĐỊNH` | không có trong bản Quy chuẩn | Hiệu lực nằm ở Thông tư 103/2025/TT-BCA — **chưa có trong kho**. Phần hỏi đáp (giải đáp số 1531 và 1538) nói **30/12/2025**; đã ghi vào `ngay_hieu_luc_theo_tham_khao` nhưng **chưa được coi là đã chứng minh** — vẫn cần Thông tư. |
| **Hỏi đáp C07** | `KHÔNG ÁP DỤNG` | không có | **KHÔNG phải văn bản quy phạm pháp luật.** 132 giải đáp của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ. Không có ngày trả lời — xem mục riêng bên dưới. |

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

## HỎI ĐÁP NGHIỆP VỤ — KINH NGHIỆM THỰC CHIẾN, KHÔNG PHẢI CĂN CỨ PHÁP LÝ

Kho có **132 giải đáp** của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ
đối với câu hỏi của công dân và doanh nghiệp, thu thập từ chuyên mục hỏi đáp
trên cổng thông tin `canhsatpccc.gov.vn`, đặt tại
`corpus/huong-dan/hoi-dap-c07/`.

Giá trị của nó là cho biết **cơ quan thẩm duyệt thực tế đang hiểu và áp dụng quy
định như thế nào** — thứ mà đọc trần văn bản quy chuẩn không thấy được. Nhiều
giải đáp trả lời đúng những câu mà quy chuẩn để mập mờ: công trình đã hoạt động
rồi có phải nâng cấp theo tiêu chuẩn mới không, nhà ở kết hợp kinh doanh bao
nhiêu mét vuông thì thành cơ sở thuộc diện quản lý, kết cấu thép có bắt buộc sơn
chống cháy không.

### Bốn quy tắc bắt buộc khi dùng phần này

1. **Không bao giờ trích giải đáp làm căn cứ pháp lý.** Căn cứ luôn là văn bản
   quy phạm pháp luật mà giải đáp đó viện dẫn. Giải đáp chỉ đi kèm để cho thấy
   cơ quan quản lý hiểu điều khoản đó ra sao.
2. **Luôn nói rõ đây là tài liệu tham khảo.** Chuỗi trích dẫn đã mang sẵn cảnh
   báo, dùng đúng chuỗi đó: *"Giải đáp số 60 của Cục Cảnh sát Phòng cháy chữa
   cháy và Cứu nạn cứu hộ (tài liệu tham khảo, không phải văn bản quy phạm pháp
   luật)"*.
3. **Không mục nào có ngày trả lời.** Không thể biết giải đáp được viết theo văn
   bản nào còn hiệu lực tại thời điểm nào. `tools/build_index.py` tự liệt kê các
   văn bản mà mỗi giải đáp viện dẫn và `tools/search.py` in ra hai loại cảnh báo:

   ```
   🛑  THAM KHẢO - KHÔNG PHẢI VĂN BẢN QUY PHẠM PHÁP LUẬT — KHÔNG ĐƯỢC dùng làm căn cứ pháp lý.
   ⚠️  Viện dẫn QCVN 06:2021/BXD — kho xác định văn bản này ĐÃ BỊ THAY THẾ bởi QCVN 06:2022/BXD.
   ⚠️  Viện dẫn văn bản KHÔNG CÓ TRONG KHO: TCVN 3890:2009, TCVN 3890:2023
   ```

   Thấy dòng thứ hai thì **tuyệt đối không dùng lại nội dung đó** mà chưa đối
   chiếu văn bản thay thế. Thấy dòng thứ ba thì phải nói rõ với người dùng rằng
   kho không tự kiểm chứng được nội dung được viện dẫn.
4. **Không suy rộng từ một trường hợp cụ thể.** Phần lớn giải đáp trả lời cho
   một công trình có quy mô, công năng cụ thể. Đừng biến câu trả lời cho một nhà
   ở 60 m² bán hàng ăn sáng thành quy tắc chung cho mọi nhà ở kết hợp kinh doanh.

### Phần hỏi đáp đã lấp được một khoảng trống của kho

Kho từng để trống ngày hiệu lực của QCVN 10:2025/BCA. Giải đáp số 1531 và số
1538 nêu nguyên văn *"Phạm vi áp dụng của QCVN 10:2025/BCA (có hiệu lực từ
30/12/2025)"*. Ngày này đã được ghi vào corpus dưới trường riêng
`ngay_hieu_luc_theo_tham_khao`, **không** ghi đè `ngay_hieu_luc`.

Đây là cách xử lý bắt buộc với mọi thông tin lấy từ tài liệu tham khảo: **ghi
lại được, nhưng không nâng lên thành đã chứng minh.** Muốn khẳng định chắc chắn
vẫn phải có Thông tư số 103/2025/TT-BCA.

### Khoảng trống lớn nhất của kho, đã đo được

**72 trên 132 giải đáp viện dẫn Nghị định số 105/2025/NĐ-CP** quy định chi tiết
Luật Phòng cháy, chữa cháy và cứu nạn, cứu hộ, hiệu lực từ 01/7/2025 — và văn
bản đó **chưa có trong kho**. Nghĩa là hơn một nửa phần hỏi đáp trỏ tới một văn
bản mà kho không đọc được: biết được cơ quan quản lý kết luận gì, nhưng không tự
kiểm chứng được căn cứ.

Các văn bản khác được viện dẫn nhiều nhưng chưa có trong kho:
`50/2024/NĐ-CP` (15 lần) · `136/2020/NĐ-CP` (13) · `TCVN 3890:2023` (11) ·
`36/2025/TT-BCA` (11) · Luật `55/2024/QH15` (10).

**Đây là danh sách tài liệu nên đề nghị người dùng bổ sung, theo đúng thứ tự ưu
tiên trên.** Có Nghị định số 105/2025/NĐ-CP thì phần hỏi đáp mới dùng được hết
giá trị.

### Những gì đã bị loại khỏi kho, và vì sao

Bản thu thập có 152 mục. **18 mục đã bị loại**: đó là đơn thư phản ánh về một cơ
sở hoặc cá nhân cụ thể, mang tên người, địa chỉ nhà, thư điện tử, số điện thoại
của bên thứ ba, còn câu trả lời chỉ là thông báo chuyển đơn về Công an địa
phương — không có nội dung hướng dẫn nào. Danh sách nằm trong hằng `LOAI_TRU`
của `tools/ingest_hoi_dap.py`. Ba mục cùng dùng chung một câu trả lời đã được
**gộp thành một chunk** giữ đủ cả ba câu hỏi, thay vì để ba chunk gần trùng nhau.

### Vì sao chunk hỏi đáp bị hạ trọng số khi tìm kiếm

`tools/search.py` nhân điểm của chunk tài liệu tham khảo với `HE_SO_THAM_KHAO`
(hiện là **0.90**). Lý do đo được, không phải cảm tính: hỏi đáp là văn xuôi dài,
dày từ khoá đời thường, nói đúng những chủ đề mà quy chuẩn nói bằng ngôn ngữ
pháp lý cô đọng — để nguyên trọng số thì **nó lấn át chính điều khoản mà nó đang
giải thích**. Trên bộ 165 câu cũ, thêm 133 chunk hỏi đáp làm Recall@3 tụt từ
0.774 xuống 0.728; hạ trọng số kéo lại còn 0.762.

Giá trị 0.90 được chọn bằng cách quét dải 1.00 → 0.60 và đo cả hai chiều: nó cho
chỉ số tổng hợp cao nhất **đồng thời** cho loại câu hỏi hỏi đáp (loại K)
Recall@5 = 0.90. Hạ sâu hơn thì chôn mất phần hỏi đáp mà không được thêm gì.
Đổi giá trị này thì **phải chạy lại `eval/chay_danh_gia.py` và quét lại dải**,
đừng chỉnh theo cảm giác.

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

`eval/` có bộ 185 câu hỏi gán nhãn vàng (trong đó 10 câu cố tình nằm ngoài phạm
vi kho). Sau khi sửa `tools/search.py` hoặc thay đổi cách cắt chunk, **phải chạy
lại**:

```bash
python3 eval/chay_danh_gia.py            # chỉ số hiện hành
python3 eval/chay_danh_gia.py --so-sanh  # đối chứng với tokenizer cũ
python3 eval/chay_danh_gia.py --chi-tiet # liệt kê câu trượt
```

Mức hiện tại (185 câu, 6 văn bản, 815 chunk): Recall@1 = 0.569 · Recall@3 = 0.767 · Recall@5 = 0.808 · Recall@10 = 0.895 · MRR = 0.705.

Chi phí đã đo của việc thêm 133 chunk hỏi đáp, tính trên **đúng bộ 165 câu cũ**
để so sánh công bằng: Recall@3 từ 0.774 xuống 0.762, MRR từ 0.709 xuống 0.698 —
khoảng 1 đến 2 câu trong 155. Đổi lại 132 giải đáp thực tiễn tìm được ở mức
Recall@5 = 0.90. Đây là đánh đổi có chủ ý, không phải hồi quy bị bỏ sót.
**Đừng merge một thay đổi làm các số này tụt** mà không có lý do đo được.
Điểm yếu đã biết: loại G (câu hỏi bắc cầu nhiều văn bản) = 0.17, loại I (câu hỏi
mơ hồ) = 0.25. Loại K là câu hỏi nhắm vào phần hỏi đáp nghiệp vụ. Giới hạn của bộ đo được ghi ở `eval/README.md` — đọc trước khi
trích dẫn con số.

## Cấu trúc kho

```
corpus/quy-chuan/  Quy chuẩn, tiêu chuẩn — văn bản quy phạm pháp luật
corpus/nghi-dinh/  Nghị định, Luật, Thông tư — văn bản quy phạm pháp luật
corpus/huong-dan/  Tài liệu THAM KHẢO — không có giá trị pháp lý bắt buộc
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

Kho **đã có sẵn 122 ảnh bảng**, phủ **toàn bộ bảng của cả bốn văn bản**:

| Văn bản | Thư mục ảnh | Số bảng |
|---|---|---|
| QCVN 06:2022/BXD phần chính | `corpus/quy-chuan/qcvn-06-2022-bxd/bang/` | 16 |
| QCVN 06:2022/BXD phụ lục | `corpus/quy-chuan/qcvn-06-2022-bxd/phu-luc/bang/` | 48 |
| QCVN 10:2025/BCA | `corpus/quy-chuan/qcvn-10-2025-bca/phu-luc/bang/` | 19 |
| QCVN 10:2024/BXD | `corpus/quy-chuan/qcvn-10-2024-bxd/phu-luc/bang/` | 2 |

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
- **Ảnh phải đi NGAY SAU nội dung mà nó minh họa, không gom lại một chỗ.**
  Người dùng đã yêu cầu rõ: *"luôn cung cấp hình ảnh của các nội dung ngay sau
  nó nếu có"*. Cách làm bắt buộc:
  1. Trước khi viết câu trả lời, **rà xem mỗi mục/bảng/hình sắp trích có ảnh
     trong kho không** — cả `bang/` lẫn `hinh/` của mọi văn bản liên quan.
  2. Viết đoạn trích dẫn → **gửi ảnh của đúng đoạn đó ngay** → mới viết tiếp.
     Gửi dồn toàn bộ ảnh ở đầu hoặc cuối câu trả lời là SAI, vì người đọc phải
     tự ghép ảnh với đoạn văn.
  3. Trích một điều khoản có dẫn chiếu hình (ví dụ mục 3.2.8 dẫn Hình I.3, I.4,
     I.5; mục 3.4.10 dẫn Hình I.7, I.8) thì **phải gửi kèm các hình đó**, không
     chỉ gửi bảng.
  4. Không có ảnh trong kho thì **nói thẳng là chưa có và cần bản PDF gốc**,
     tuyệt đối không vẽ lại rồi trình bày như ảnh chụp bản in.
