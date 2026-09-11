# Đo lường và các quyết định thiết kế — hồ sơ bằng chứng

Tệp này tách khỏi `CLAUDE.md` vì nó là **hồ sơ tra khi cần**, không phải hàng
rào phải bật lên trong mọi câu trả lời. Đọc nó khi bạn định:

- sửa `tools/search.py`, `tools/build_index.py` hoặc cách cắt chunk;
- đổi một hằng số xếp hạng (`HE_SO_THAM_KHAO`, `HE_SO_GAN_NHAU`,
  `SO_UNG_VIEN_XEP_LAI`);
- đề xuất đổi sang cơ sở dữ liệu vector hoặc nhúng ngữ nghĩa;
- trích dẫn một con số chất lượng truy hồi cho người dùng.

**Nguyên tắc chung của kho: không đổi một hằng số nào theo cảm giác.** Mỗi con
số dưới đây đến từ một phép quét dải giá trị, và đổi nó thì phải quét lại.

---

## Đo chất lượng truy hồi

`eval/` có bộ 215 câu hỏi gán nhãn vàng (trong đó 10 câu cố tình nằm ngoài phạm
vi kho). Sau khi sửa `tools/search.py` hoặc thay đổi cách cắt chunk, **phải chạy
lại**:

```bash
python3 eval/chay_danh_gia.py            # chỉ số hiện hành
python3 eval/chay_danh_gia.py --so-sanh  # đối chứng với tokenizer cũ
python3 eval/chay_danh_gia.py --chi-tiet # liệt kê câu trượt
```

Mức hiện tại (215 câu, 14 văn bản, 1 214 chunk): Recall@1 = 0.550 · Recall@3 = 0.781 · Recall@5 = 0.842 · Recall@10 = 0.890 · MRR = 0.698.

Chi phí đã đo của việc thêm QCVN 01:2021/BXD (168 chunk) và giữ lại các **mục cha chỉ
có tên** (57 chunk trong các văn bản cũ): Recall@1 từ 0.570 xuống 0.550, MRR từ 0.711
xuống 0.698. Tách riêng hai nguyên nhân bằng phép đo: giữ mục cha tốn 0.005 (khoảng
một câu trên 205), phần còn lại là pha loãng do thêm một văn bản mới — đúng loại đánh
đổi đã chấp nhận khi thêm phần hỏi đáp. Đổi lại, 10 câu hỏi mới về quy hoạch xây dựng
đều tìm được đáp án, và **phạm vi của mục cha quay lại chỉ mục** — thứ mà việc thiếu nó
đã gây ra lỗi trích nhầm mục 2.7.4 QCVN 10:2024/BXD.

### Vì sao KHÔNG dùng cơ sở dữ liệu vector — đã đo, không phải quan điểm

Quy mô hiện tại: **1 214 chunk · 2,5 MB · 15 ms mỗi truy vấn · 0,46 s dựng lại
toàn bộ chỉ mục**. Cơ sở dữ liệu vector sinh ra để giải bài toán tìm láng giềng
gần đúng ở quy mô hàng triệu véc-tơ; ở đây nó giải một bài toán kho này chưa có.

Quan trọng hơn, **phép đo cho thấy truy hồi không phải là chỗ hỏng**:

| Recall@K | Giá trị |
|---|---|
| @5 | 0.839 |
| @10 | 0.892 |
| @50 | 0.949 |
| @100 | 0.979 |

(Bảng này đo ở quy mô 989 chunk, trước khi thêm QCVN 01:2021/BXD; kết luận
về hình dạng đường cong không đổi.)

**Không một câu nào** trong bộ đánh giá thất bại vì BM25 tìm không ra chunk
vàng — mọi chunk vàng đều được tìm thấy, chỉ bị xếp hạng thấp. Nghĩa là việc
cần làm là **xếp hạng lại**, không phải đổi cách tìm. Nhúng ngữ nghĩa có dư địa
thật (trần của một bộ xếp hạng lại hoàn hảo trên top 50 là 0.949), nhưng nó là
lớp XẾP HẠNG LẠI đặt sau BM25, không phải lớp thay thế BM25.

Lý do không thay BM25: tra cứu pháp luật cần khớp **định danh chính xác** —
"mục 3.3.6", "Bảng G.9", và nhất là "QCVN 10:2024/BXD" so với "QCVN 10:2025/BCA"
(khác một ký tự, hai văn bản hoàn toàn khác nhau). Véc-tơ nhúng làm mờ đúng thứ
đó. Kho đã có `diem_cau_truc` cộng 12 điểm cho khớp số hiệu chính xác — một hệ
thống thuần véc-tơ mất tín hiệu này.

**Ngưỡng nên xem lại quyết định:** khi kho vượt khoảng **100 000 chunk** (gấp
100 lần hiện nay, tương đương hơn 1 000 văn bản), hoặc khi có bằng chứng đo được
rằng một lớp xếp hạng lại bằng nhúng vượt hơn tín hiệu vị trí gần nhau.

**Ràng buộc môi trường hiện tại:** PyPI truy cập được nhưng `huggingface.co` bị
chặn (HTTP 000) — tải được thư viện nhưng **không tải được trọng số mô hình**,
nên không kiểm chứng được nhúng ngữ nghĩa từ đầu đến cuối trong phiên làm việc.

### Tín hiệu vị trí gần nhau — lớp xếp hạng lại hiện hành

`search.py` xếp hạng lại **top 10** bằng `diem_gan_nhau()`: cửa sổ ngắn nhất
chứa được nhiều từ truy vấn nhất. Lý do: điều khoản pháp luật phát biểu quy định
cô đọng nên các từ nằm sát nhau; chunk dài trùng nhiều từ nhưng rải rác thường
chỉ *nhắc tới* chủ đề chứ không *quy định* về nó.

Đo được: Recall@5 từ 0.809 lên 0.839, MRR từ 0.700 lên 0.711, Recall@10 giữ
nguyên, thời gian từ 8 ms lên 15 ms. Hệ số 2.0 chọn từ một **mặt phẳng** 1.0–2.5
chứ không phải một đỉnh nhọn. Số ứng viên 10 chọn từ quét 10/15/20/30/50/100 —
xếp lại sâu hơn làm Recall@10 tụt 0.024.

Đổi hai hằng số `HE_SO_GAN_NHAU` và `SO_UNG_VIEN_XEP_LAI` thì **phải quét lại
cả hai dải**, đừng chỉnh theo cảm giác.

Chi phí đã đo của việc thêm 133 chunk hỏi đáp, tính trên **đúng bộ 165 câu cũ**
để so sánh công bằng: Recall@3 từ 0.774 xuống 0.762, MRR từ 0.709 xuống 0.698 —
khoảng 1 đến 2 câu trong 155. Đổi lại 132 giải đáp thực tiễn tìm được ở mức
Recall@5 = 0.90. Đây là đánh đổi có chủ ý, không phải hồi quy bị bỏ sót.
**Đừng merge một thay đổi làm các số này tụt** mà không có lý do đo được.
Điểm yếu đã biết: loại G (câu hỏi bắc cầu nhiều văn bản) = 0.17, loại I (câu hỏi
mơ hồ) = 0.25. Loại K là câu hỏi nhắm vào phần hỏi đáp nghiệp vụ. Giới hạn của bộ đo được ghi ở `eval/README.md` — đọc trước khi
trích dẫn con số.

---

## Hỏi đáp nghiệp vụ — phân tích và đánh đổi đã đo

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
