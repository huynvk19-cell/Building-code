---
name: phan-cap-cong-trinh
description: >-
  Danh sách đủ 17 chỗ Thông tư 02/2025/TT-BXD đã sửa, bổ sung, BÃI BỎ trong
  Thông tư 06/2021/TT-BXD về phân cấp công trình xây dựng, lý do kho KHÔNG có
  cảnh báo sửa đổi tự động trên từng chunk của cặp văn bản này, và cách trích
  dẫn đúng cả hai. BẮT BUỘC gọi skill này TRƯỚC KHI trả lời bất kỳ câu hỏi nào
  chạm tới: cấp công trình, phân cấp công trình, công trình cấp đặc biệt, cấp I,
  II, III, IV, Bảng 1.1 đến 1.5 hay Bảng 2 Phụ lục II, ví dụ Phụ lục III, Thông
  tư 06/2021/TT-BXD hoặc Thông tư 02/2025/TT-BXD. Trích Thông tư 06/2021/TT-BXD
  mà không đọc skill này là trích quy định đã hết hiệu lực — mục 1.2.1.3 Bảng
  1.2 đã bị bãi bỏ.
---

# PHÂN CẤP CÔNG TRÌNH — ĐỌC KÈM THÔNG TƯ 02/2025/TT-BXD

Cấp công trình quyết định thẩm quyền thẩm định, điều kiện năng lực nhà thầu, thời
hạn bảo hành và nhiều thủ tục khác, nên trả lời sai cấp là sai cả đường đi hồ sơ.

Kho có **hai văn bản** cho cùng một chế định:

- **Thông tư 06/2021/TT-BXD** — bản gốc, hiệu lực 15/8/2021. Đủ 5 Điều, Phụ lục I
  (Bảng 1.1 đến 1.5, phân cấp theo mức độ quan trọng hoặc quy mô công suất),
  Phụ lục II (Bảng 2, phân cấp theo quy mô kết cấu), Phụ lục III (15 ví dụ).
- **Thông tư 02/2025/TT-BXD** — hiệu lực **20/5/2025**, sửa 17 chỗ. **Không thay
  thế** bản gốc; quy định đang có hiệu lực = bản gốc đã vá bằng bản sửa đổi.

## Vì sao ở đây KHÔNG có cảnh báo tự động trên từng chunk

Với QCVN 06, `search.py` in cảnh báo `⚠️ ĐÃ BỊ SỬA ĐỔI` trên từng mục vì bản sửa
đổi đánh số theo đúng số hiệu mục của bản gốc. Thông tư 02/2025/TT-BXD thì đánh
số Điều **của chính nó**, còn đích sửa nằm trong tên mục phụ lục ("Sửa đổi, bổ
sung mục 1.1.3.3 Bảng 1.1 Phụ lục I"), mà chunk phụ lục của bản gốc lại không
mang số hiệu mục để ghép. Ghép bừa theo số thứ tự đã gắn nhầm "Điều 2. Điều khoản
thi hành" của bản sửa đổi lên "Điều 2. Nguyên tắc xác định cấp công trình" của
bản gốc — `build_index.py` nay chặn việc đó. **Bảng dưới đây thay cho cảnh báo tự
động: đọc nó mỗi khi tra cấp công trình.**

## 17 chỗ đã bị sửa — tra trước khi trích Thông tư 06/2021/TT-BXD

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
