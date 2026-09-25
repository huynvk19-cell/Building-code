---
name: bao-tri-kho
description: >-
  Cấu trúc thư mục của kho và quy trình bắt buộc trước mỗi lần commit hoặc đẩy
  nhánh: dựng chỉ mục hai lần, chạy bộ đánh giá, kiểm tra liên kết ảnh, cập nhật
  README.md, kiểm chứng bằng thị giác máy khi đụng tới nội dung corpus, và mức
  truy hồi hiện hành để so sánh. BẮT BUỘC gọi skill này TRƯỚC KHI commit, đẩy
  nhánh, sửa bất kỳ tệp nào trong corpus/, tools/, eval/, docs/, README.md,
  CLAUDE.md hay .claude/skills/, hoặc khi người dùng hỏi với vai bảo trì kho.
  README đã từng lạc hậu qua sáu lần bổ sung văn bản vì bước cập nhật nó bị bỏ
  qua.
---

# Bảo trì kho — cấu trúc và quy trình đẩy nhánh

## Cấu trúc kho

```
corpus/quy-chuan/  corpus/nghi-dinh/   văn bản quy phạm pháp luật — CHỈ sửa ở đây
corpus/huong-dan/                      tài liệu THAM KHẢO, không có giá trị pháp lý
chunks/  index/                        sinh tự động — KHÔNG sửa tay
eval/    tools/    docs/
.claude/skills/                        skill nạp theo yêu cầu — xem bảng đầu CLAUDE.md
```

Hướng dẫn dành cho người dùng cuối (không phải cho AI) ở `docs/huong-dan-su-dung.md`.

## Quy trình đẩy nhánh

Người dùng đã chọn rõ: **luôn đẩy lên nhánh làm việc của phiên**, tự đẩy không
cần hỏi lại, không đẩy thẳng lên `main`, không mở pull request trừ khi được yêu
cầu. Tên nhánh do phiên chỉ định (ví dụ
`claude/tieu-chuan-thiet-ke-chung-cu-r50hdn`); phiên không chỉ định nhánh nào thì
hỏi người dùng, **tuyệt đối không rơi về `main`**. Vì người dùng đã bỏ cửa kiểm
tra thủ công, **bốn bước sau là bắt buộc trước mỗi lần đẩy**:

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
nên phải cập nhật cả hai. Thêm văn bản mới thì còn phải cập nhật bảng hiệu lực
trong skill `tra-cuu-hieu-luc`.

**Giữ `CLAUDE.md` dưới 50 dòng.** Tệp đó chỉ chứa hàng rào phải bật trong mọi
câu trả lời; chi tiết mới thì đưa vào skill phù hợp, rồi thêm một dòng vào bảng
gọi skill của `CLAUDE.md` nếu là skill mới.

Chỉ số tụt mà không giải thích được bằng phép đo thì **không đẩy**. Thay đổi
**đụng tới nội dung corpus của văn bản pháp luật** thì còn phải kiểm chứng bằng
thị giác máy đối chiếu bản gốc — đây là loại lỗi mà chỉ số truy hồi không bắt được.

Mức truy hồi hiện tại (250 câu, 19 văn bản, 1 387 chunk): Recall@1 = 0,582 ·
Recall@3 = 0,799 · Recall@5 = 0,844 · Recall@10 = 0,886 · MRR = 0,715. Trước khi
đổi bất kỳ hằng số xếp hạng nào, **gọi skill `do-luong-truy-hoi`** — mỗi con
số ở đó đến từ một phép quét dải giá trị, không phải cảm tính.
