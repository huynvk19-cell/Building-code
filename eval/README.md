# Bộ đánh giá truy hồi

Đo **tầng truy hồi**, không đo chất lượng câu trả lời của LLM. Lý do: nếu chunk
đúng không lọt vào top-K thì LLM không có cách nào trả lời đúng — truy hồi là
trần trên của toàn hệ thống.

```bash
python3 eval/chay_danh_gia.py
```

## Nội dung

- `bo_cau_hoi.jsonl` — 40 câu hỏi, mỗi câu có nhãn vàng là `chunk_id` và một
  chuỗi `kiem_chung`. Script tự xác nhận chuỗi đó thực sự nằm trong chunk vàng,
  nên nhãn không thể bịa.
- `chay_danh_gia.py` — tính Recall@1/3/5/10 và MRR, tách theo loại câu hỏi.

## Phân loại câu hỏi

| Loại | Nghĩa | Số câu |
|---|---|---|
| A | Tra cứu trực tiếp theo số Điều/mục | 6 |
| B | Tra cứu ngữ nghĩa (diễn đạt đời thường) | 6 |
| C | Cần nhiều Điều/Phụ lục | 4 |
| D | Ngoại lệ, trường hợp được miễn | 4 |
| E | Hiệu lực, chuyển tiếp, thay thế | 4 |
| F | Giá trị định lượng | 8 |
| G | Nhiều văn bản | 2 |
| H | Phủ định / vắng mặt quy định | 3 |
| I | Câu hỏi thiếu thông tin | 1 |
| J | Suy luận tuân thủ từ dữ kiện | 2 |
| K | Hỏi đáp nghiệp vụ (tài liệu tham khảo) | 20 |

## Số đo tại thời điểm lập (2026-09-09)

Chạy trên `index/chunks.jsonl` gồm 137 chunk của 3 văn bản.

| Chỉ số | BM25 hiện tại |
|---|---|
| Recall@1 | 0,483 |
| Recall@3 | 0,775 |
| Recall@5 | 0,838 |
| Recall@10 | 0,917 |
| MRR | 0,671 |

Recall@5 theo loại: A=0,67 · B=0,83 · C=0,75 · D=1,00 · E=1,00 · F=1,00 ·
**G=0,25** · H=1,00 · **I=0,00** · J=1,00

## Đọc số này cho đúng — các giới hạn phải biết

1. **n=40 là mẫu nhỏ.** Chênh lệch dưới ~5 điểm phần trăm nằm trong nhiễu. Đừng
   dùng bộ này để kết luận A hơn B khi khoảng cách hẹp.
2. **Câu hỏi do chính người dựng corpus viết**, nên có thiên lệch: dùng đúng từ
   vựng của văn bản. Người dùng thật sẽ hỏi khác. Recall thực tế nhiều khả năng
   **thấp hơn** con số ở đây.
3. **Chỉ đo truy hồi.** Chưa đo: độ đúng của câu trả lời, độ đúng của trích dẫn,
   độ đúng của con số, tỉ lệ bịa. Retrieval đúng là điều kiện cần, không phải đủ.
4. Loại G và I chỉ có 2 và 1 câu — số của chúng chỉ đủ để **báo động**, không đủ
   để đo lường.

## Việc nên làm tiếp

- Mở rộng lên ~100 câu, ưu tiên loại G, I, C.
- Nhờ một kiến trúc sư không tham gia dựng corpus viết câu hỏi, để bỏ thiên lệch từ vựng.
- Bổ sung đo độ đúng trích dẫn và độ đúng con số.


## Hệ số trọng số của tài liệu tham khảo

`tools/search.py` nhân điểm BM25 của chunk thuộc tài liệu THAM KHẢO với
`HE_SO_THAM_KHAO`. Giá trị hiện hành là **0.90**, chọn bằng cách quét dải và đo
trên bộ 185 câu:

| hệ số | Recall@1 | Recall@3 | MRR | loại K (Recall@5) |
|---|---|---|---|---|
| 1.00 | 0.563 | 0.742 | 0.693 | 0.95 |
| 0.95 | 0.569 | 0.753 | 0.697 | 0.90 |
| **0.90** | **0.569** | **0.767** | **0.705** | **0.90** |
| 0.85 | 0.563 | 0.761 | 0.702 | 0.85 |
| 0.80 | 0.557 | 0.763 | 0.702 | 0.80 |
| 0.72 | 0.548 | 0.757 | 0.697 | 0.75 |
| 0.60 | 0.542 | 0.737 | 0.687 | 0.65 |

0.90 cho chỉ số tổng hợp cao nhất đồng thời giữ được loại K ở mức 0.90. Quét lại
dải này mỗi khi thêm tài liệu tham khảo mới:

```bash
for h in 1.00 0.95 0.90 0.85 0.80 0.72 0.60; do
  HE_SO_THAM_KHAO=$h python3 eval/chay_danh_gia.py | grep -E 'Recall@1 |Recall@3|MRR|theo loại'
done
```

## Chi phí đã đo của việc thêm phần hỏi đáp

Đo trên **đúng bộ 165 câu trước khi thêm**, để so sánh công bằng:

| | trước | sau (hệ số 1.00) | sau (hệ số 0.90) |
|---|---|---|---|
| Recall@1 | 0.554 | 0.545 | 0.558 |
| Recall@3 | 0.774 | 0.728 | 0.762 |
| Recall@5 | 0.811 | 0.794 | 0.796 |
| Recall@10 | 0.887 | 0.859 | 0.882 |
| MRR | 0.709 | 0.680 | 0.698 |

Không hạ trọng số thì Recall@3 mất 0.046. Hạ trọng số kéo lại còn mất 0.012.
