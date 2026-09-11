# Phản biện kế hoạch "AI Code Compliance Reviewer"

Tài liệu này phản biện bản kế hoạch 20 phase do ChatGPT soạn, đối chiếu với
**trạng thái đo được** của kho tại thời điểm viết: 12 văn bản, 866 chunk,
197 câu hỏi chuẩn, Recall@1 = 0.559 · Recall@5 = 0.820 · MRR = 0.701.

Mọi con số dưới đây đều lấy từ lệnh chạy thật, không ước lượng.

---

## 1. Kế hoạch đúng ở đâu

Bốn nguyên tắc của nó trùng khớp với những gì kho đã **đo được và trả giá** để
học, nên chúng đáng giữ nguyên:

| Nguyên tắc của kế hoạch | Kho đã làm |
|---|---|
| Rule 5 — không dùng LLM cho logic tất định | `build_index.py` ghép bản sửa đổi bằng rule, không nhờ LLM |
| Rule 9 — "search không thấy" ≠ "pháp luật không quy định" | Đã ghi trong CLAUDE.md; `search.py` in cảnh báo khi rỗng |
| Rule 10 — FAQ không ngang hàng quy chuẩn | Trường `gia_tri_phap_ly`, hệ số 0.90, cảnh báo 🛑 |
| Rule 8 — điểm truy hồi không phải độ tin cậy pháp lý | Đã đo và ghi: hai dải điểm **chồng lấn hoàn toàn** |

Ba phase là **giá trị mới thật sự**, kho chưa có: kiểm chứng trích dẫn (Phase 9),
kiểm chứng con số và đơn vị (Phase 10), và máy xác định tình trạng hiệu lực theo
mốc thời gian dự án (Phase 3).

---

## 2. Kế hoạch giả định một điểm xuất phát không đúng

Nó được viết như thể kho là một chatbot RAG thô sơ. Đối chiếu thực tế:

| Phase | Kế hoạch yêu cầu | Trạng thái thật |
|---|---|---|
| 0 | Tạo `docs/AUDIT_BASELINE.md` | **CLAUDE.md (687 dòng) đã là tài liệu đó.** Tạo thêm sẽ có hai nguồn sự thật, đúng cái mà chính Phase 18 cảnh báo |
| 1 | Thiết kế schema metadata | Đã có: 18 trường front matter, gồm `ngay_hieu_luc`, `can_cu_hieu_luc`, `sua_doi_boi`, `dieu_khoan_chuyen_tiep`, `gia_tri_phap_ly`, `trang_thai` |
| 1 | Phân cấp nguồn LAW/DECREE/QCVN/FAQ | Đã có qua `loai_van_ban` + `gia_tri_phap_ly` + thư mục `corpus/huong-dan/` |
| 12 | `corpus_audit.py` phát hiện MISSING_DEPENDENCY | **Đã có**: `danh_dau_vien_dan()` chia hai loại `vien_dan_da_bi_thay_the` và `vien_dan_ngoai_kho`; 104 chunk đang mang cờ |
| 12 | Khung cho văn bản thiếu | **Đã có**: 5 khung rỗng, `trang_thai: "KHUNG RỖNG"`, có cảnh báo 📭 |
| 16 | Tách biệt đo lường | Đã có 197 câu, 11 loại, chia theo loại câu hỏi |

Làm lại những phần này là lãng phí và tạo rủi ro trôi dạt tài liệu.

---

## 3. Ba điểm kế hoạch SAI hoặc NGUY HIỂM

### 3.1. Phase 2 — "Consolidated legal version engine" là điểm nguy hiểm nhất

Kế hoạch yêu cầu sinh ra một `current_text` hợp nhất giữa bản gốc và bản sửa đổi.

**Vấn đề:** văn bản hợp nhất đó **không tồn tại trong bất kỳ công báo nào**. Nó
là sản phẩm phái sinh do máy tạo ra, nhưng lại được trình bày như điều luật.

Nguyên tắc nền của kho là **trung thành với bản in** — đó không phải sự cứng
nhắc mà là điều kiện để người dùng kiểm tra được hệ thống. Ba lần trong phiên
làm việc gần nhất, người dùng bắt được lỗi của hệ thống **chính nhờ đối chiếu
với bản gốc**. Một văn bản hợp nhất tự động sẽ xoá mất khả năng đó.

Thêm nữa, sửa đổi trong pháp luật Việt Nam có những dạng mà phép ghép máy móc
thất bại **âm thầm**:

- *"Thay thế cụm từ A bằng cụm từ B tại điểm k khoản 1 Điều 42"* — phải định vị
  đúng một cụm từ trong một điểm;
- *"Bãi bỏ cụm từ 'là buồng thang bộ không nhiễm khói và'"* (mục 3.4.8 QCVN 06)
  — bãi bỏ giữa câu, ghép sai thì câu vẫn đọc trôi nhưng nghĩa ngược lại;
- *"Bổ sung vào cuối điểm 3.4.1 đoạn văn sau"* — phải biết "cuối" ở đâu.

Sai ở đây **không có dấu hiệu nào để phát hiện**. Đó là định nghĩa của lỗi nguy
hiểm.

**Đề xuất thay thế:** giữ cơ chế gắn cờ hiện tại (đang chạy đúng, 92 chunk có
cờ), bổ sung một lớp **trình bày song song** — in bản gốc và bản sửa đổi cạnh
nhau, nêu rõ quan hệ — chứ không tổng hợp thành một văn bản duy nhất mạo danh
điều luật.

### 3.2. Phase 13 — nhãn "PROBABLE" mâu thuẫn với chính dữ liệu của kho

Kho **đã đo**: điểm top-1 của câu ngoài phạm vi rơi vào 14.1–31.1, của câu có
đáp án rơi vào 5.4–71.7 — **chồng lấn hoàn toàn**. Kết luận đã ghi trong
CLAUDE.md: *"một nhãn tin cậy sai nguy hiểm hơn không có nhãn, vì nó tạo cảm
giác an toàn giả"*.

Nhãn "PROBABLE" tái lập đúng thứ đó dưới tên khác.

**Đề xuất thay thế:** dùng **nhãn trạng thái bằng chứng** — là sự kiện kiểm tra
được, không phải xác suất:

```
CÓ ĐIỀU KHOẢN TRỰC TIẾP      — trích được nguyên văn, đã kiểm tra cờ sửa đổi
CHỈ CÓ TÀI LIỆU THAM KHẢO    — chỉ có hỏi đáp, không có điều khoản chống lưng
THIẾU VĂN BẢN NGUỒN          — điều khoản dẫn chiếu tới văn bản chưa có trong kho
MÂU THUẪN CHƯA GIẢI QUYẾT    — hai điều khoản cùng phạm vi, chưa xác định quan hệ
THIẾU DỮ KIỆN DỰ ÁN          — chưa đủ thông số để áp ngưỡng
KHÔNG TÌM THẤY TRONG KHO     — không phải "pháp luật không quy định"
```

Mỗi nhãn trả lời được bằng `if`, không cần đoán.

### 3.3. Phase 15 và 16 — chỉ tiêu không đo được

**300 câu hỏi:** kế hoạch không nói **ai gán nhãn vàng**. Bộ 197 câu hiện tại
mỗi câu đều có trường `kiem_chung` và `chay_danh_gia.py` **tự kiểm tra chuỗi đó
có thật nằm trong chunk vàng không** — không qua bước này thì bộ đo chỉ đo chính
cái máy sinh ra nó. Sinh 300 câu bằng LLM rồi tự gán nhãn là tạo ra một con số
đẹp mà vô nghĩa.

**`hallucination_rate`:** không thể đo nếu không có tập câu trả lời chuẩn do
người viết. Kế hoạch yêu cầu chỉ tiêu này nhưng không cung cấp nguồn chân lý.

**Đề xuất thay thế:** bổ sung câu hỏi **đúng chỗ đang trượt** thay vì cho đủ số
tròn. Dữ liệu trượt hiện tại (chạy `--chi-tiet`) chỉ ra ba cụm:

- loại G (bắc cầu nhiều văn bản) = 0.17 — 4/6 câu trượt;
- loại I (câu mơ hồ) = 0.00;
- các câu về bản sửa đổi (SD07, SD11, SD14, SD17) — chunk sửa đổi ngắn, bị chunk
  dài lấn át.

Và chỉ đo những gì **kiểm tra được bằng máy**: điều khoản được trích có tồn tại
không, con số trong câu trả lời có nằm trong chunk được trích không, câu ngoài
phạm vi có bị từ chối không.

---

## 4. Điều kế hoạch bỏ sót: truy hồi đã hết dư địa tinh chỉnh

Kế hoạch nhảy thẳng sang "hybrid retrieval + vector + rerank" (Phase 6). Trước
khi thêm phụ thuộc nặng, phải biết còn bao nhiêu dư địa ở tham số hiện có. **Đã
quét thật:**

| B (chuẩn hoá độ dài) | Recall@1 | Recall@3 | Recall@5 | MRR |
|---|---|---|---|---|
| 0.50 (hiện hành) | 0.578 | 0.802 | 0.845 | 0.701 |
| 0.60 | 0.588 | 0.802 | 0.845 | 0.707 |
| **0.65** | **0.594** | 0.797 | 0.850 | **0.709** |
| 0.70 | 0.583 | 0.786 | 0.856 | 0.702 |

Chênh lệch lớn nhất là **0.016 Recall@1, tức 3 câu trên 187** — nằm trong sai số
của bộ đo. Tăng trọng số tiêu đề cũng thử rồi: hạng của mục 3.3.6 đứng yên ở 7
dù nhân 1, 2 hay 3 lần.

**Kết luận có căn cứ: tinh chỉnh tham số BM25 đã cạn.** Các câu còn trượt là lỗi
**cấu trúc**, không phải lỗi tham số. Ví dụ cụ thể:

- *"chiều rộng hành lang chung thoát nạn tối thiểu"* → mục 3.3.6 (647 ký tự,
  chứa đúng đáp án) đứng **hạng 8**, thua mục G.2 và 3.3.5 vốn dài hơn và nhắc
  các từ đó nhiều lần hơn.
- *"quy chuẩn số 10 của Bộ Công an nói về cái gì"* → cần mục 1.1 (phạm vi điều
  chỉnh), nhưng câu hỏi **không chứa từ nào** của điều khoản đó.

Câu thứ hai là loại mà vector search giải được. Câu thứ nhất thì không — nó cần
ưu tiên chunk **ngắn và đúng trọng tâm** hơn chunk dài.

**Cách rẻ hơn, thử trước khi thêm vector:** sinh cho mỗi văn bản một **chunk thẻ
giới thiệu** ("QCVN 10:2025/BCA là quy chuẩn của Bộ Công an về trang bị phương
tiện phòng cháy chữa cháy, gồm các phụ lục A đến H…"). Nó giải trực tiếp cụm G04,
G05, I04, và tốn vài chục dòng code thay vì một mô hình nhúng.

---

## 5. Thứ tự ưu tiên đề xuất, theo tác động đo được

### P0 — an toàn, tất định, rẻ

1. **`tools/kiem_tra_trich_dan.py`** — cho một trích dẫn, kiểm tra: điều khoản có
   tồn tại không; có mang cờ đã bị sửa đổi không; **chuỗi được trích có thật nằm
   trong chunk đó không**. Đây là thứ chặn đúng loại lỗi mà người dùng đã bắt
   được ba lần trong phiên gần nhất.
2. **Kiểm tra con số và đơn vị** — trường hợp thật đã xảy ra: một trị số
   "1,2 m" của *chiều rộng* bị dùng cho *chiều cao*; và mục 2.7.4 QCVN 10:2024
   (vỉa hè, cho người khiếm thị) bị đặt cạnh mục 3.3.5 QCVN 06 (hành lang thoát
   nạn). Máy kiểm tra phải soát **đại lượng đi kèm con số**, không chỉ con số.

### P1 — chất lượng câu trả lời

3. **`tools/hieu_luc.py`** — trả về `đang có hiệu lực / chưa có hiệu lực / đã hết
   hiệu lực / theo điều khoản chuyển tiếp / chưa xác định`, tính theo mốc thời
   gian của hồ sơ. Có ca thật đang chờ: Nghị định 347/2026/NĐ-CP hiệu lực
   **15/9/2026**, hôm nay **11/9/2026** — chưa có hiệu lực; và một phần của nó
   (Điều 41 khoản 2) có hiệu lực theo một Luật mà kho chưa có.
4. **Chunk thẻ giới thiệu cho từng văn bản** — giải cụm G04, G05, I04.

### P2 — làm sau khi P0, P1 đã đo được

5. Trích dữ kiện dự án thành cấu trúc (Phase 4). Có giá trị nhưng cần LLM; nên
   làm dạng **danh sách kiểm** để người dùng tự điền, không phải bộ phân tích tự
   động — vì đoán sai dữ kiện dự án nguy hiểm hơn là hỏi lại.

### KHÔNG làm

- Văn bản hợp nhất tự động (mục 3.1);
- Nhãn tin cậy kiểu xác suất (mục 3.2);
- Bộ 300 câu sinh tự động, chỉ tiêu `hallucination_rate` (mục 3.3);
- Vector search **lúc này** — chưa chứng minh được lợi ích so với chunk thẻ;
- Thư mục `src/` và 8 công cụ tạo sẵn theo khuôn — 11 công cụ hiện có đều sinh
  ra từ một lỗi đo được, không phải từ sơ đồ.

---

## 6. Điều quan trọng hơn mọi phase

**72 trên 132 giải đáp trong kho viện dẫn Nghị định số 105/2025/NĐ-CP, và kho
không có văn bản đó.**

Không kỹ thuật nào bù được nguồn thiếu. Thứ tự ưu tiên bổ sung tài liệu:

1. Nghị định số 105/2025/NĐ-CP — mở khoá hơn một nửa phần hỏi đáp;
2. Nghị định số 217/2026/NĐ-CP — quản lý hoạt động xây dựng;
3. TCVN 3890:2023 — căn cứ trang bị phương tiện;
4. Thông tư số 103/2025/TT-BCA — chốt ngày hiệu lực QCVN 10:2025/BCA;
5. Nghị định số 106/2025/NĐ-CP — xử phạt.

Một buổi quét tài liệu đáng giá hơn nhiều tuần viết thêm công cụ.
