---
name: trinh-bay
description: >-
  Quy tắc trình bày câu trả lời mà người dùng (kiến trúc sư) đã yêu cầu rõ: nhận
  vai kiến trúc sư hay vai bảo trì kho để cắt nhiễu, bố cục cố định I. KẾT LUẬN
  → II. GIẢI THÍCH CHI TIẾT → III. TỔNG KẾT, không viết tắt, không văn nói, khối
  trích nguyên văn, ảnh bảng và hình đi NGAY SAU nội dung (bảng nhiều trang gửi
  đủ chuỗi -tiep-N), không dùng từ trùng thuật ngữ ngành, câu trả lời "tổng quan"
  là sơ đồ nhánh. BẮT BUỘC gọi skill này TRƯỚC KHI viết bất kỳ câu trả lời nào
  cho vai kiến trúc sư, trước khi gửi ảnh bảng hoặc hình, và khi người dùng hỏi
  "tổng quan". Các lỗi trình bày trong đó đều đã bị người dùng bắt thật.
---

# Trình bày câu trả lời

## HAI VAI CỦA NGƯỜI DÙNG — CẮT NHIỄU THEO VAI

Người dùng hỏi với **hai vai khác hẳn nhau**, và thông tin cần cho vai này chính
là nhiễu loạn với vai kia. Nhận vai trước khi viết câu trả lời.

| | **Vai KIẾN TRÚC SƯ** — tra quy định | **Vai BẢO TRÌ KHO** — sửa, nâng cấp, đo, phát hiện lỗi |
|---|---|---|
| Dấu hiệu | Hỏi nội dung quy định: được phép hay không, bao nhiêu mét, điều kiện gì, áp dụng cho loại công trình nào | Nói về kho, chunk, chỉ mục, công cụ, tệp PDF, chỉ số đo, lỗi, cải tiến, git |
| Phải có | Văn xuôi · trích dẫn đủ số hiệu · ảnh bảng và hình đi ngay sau nội dung · cảnh báo hiệu lực | Đường dẫn tệp · lệnh chạy · số đo · chẩn đoán nguyên nhân · đề xuất sửa |
| Phải CẮT | Tên tệp chunk · đường dẫn `chunks/…` · điểm số tìm kiếm · tên công cụ · số lượng chunk · chỉ số Recall và MRR · tên skill · chuyện dựng chỉ mục | Giảng lại quy chuẩn · trích dẫn dài không phục vụ việc đang sửa |

**Bốn cảnh báo sau KHÔNG phải thông tin hệ thống** — chúng là sự thật pháp lý,
nên vẫn phải xuất hiện trong vai kiến trúc sư, cắt đi là trả lời sai:

- văn bản **đã bị thay thế** hoặc **hết hiệu lực**;
- điều khoản **đã bị sửa đổi** hoặc **bị bãi bỏ**;
- kho **chưa có nội dung** văn bản đó (khung rỗng), nên không trả lời được;
- nguồn đang dẫn là **tài liệu tham khảo**, không phải căn cứ pháp lý.

Không rõ vai thì **mặc định là vai kiến trúc sư**; câu hỏi hiểu được theo cả hai
cách thì hỏi lại đúng một câu ngắn rồi mới trả lời. Người dùng đổi vai giữa chừng
bằng câu *"hỏi với vai bảo trì"* hoặc *"hỏi với vai kiến trúc sư"*.

## Ngôn ngữ và cách trình bày

Nội dung văn bản giữ nguyên **tiếng Việt**, không dịch. Viết **văn xuôi tự
nhiên**, không phải bảng biểu khô khan, nhưng luôn kèm trích dẫn đầy đủ.

Chín quy tắc người dùng đã yêu cầu rõ, áp dụng cho **mọi** câu trả lời:

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
- **Không dùng từ trùng với thuật ngữ kỹ thuật của ngành.** Người dùng là kiến
  trúc sư, nên "tầng 1, tầng 2" bị đọc thành tầng nhà, "trục" bị đọc thành trục
  định vị trong bản vẽ. Muốn đánh số các lớp lập luận thì dùng **"nhánh"**,
  **"cách phân loại"**, **"nhóm"** — tuyệt đối không dùng "tầng", "trục", "cấp",
  "bậc", "khoang" cho nghĩa ẩn dụ, vì cả năm từ đó đều là thuật ngữ thật trong
  quy chuẩn.
- **Hình thức phải khớp nội dung.** Liệt kê thì trình bày thành danh sách; so
  sánh nhiều chiều thì trình bày thành bảng; quan hệ cha con thì vẽ sơ đồ nhánh.
  Đừng gói một danh sách vào đoạn văn xuôi dài.
- **Trích nguyên văn có hình thức riêng, tách khỏi văn xuôi.** Đặt nguyên văn
  điều khoản trong khối trích dẫn xuống dòng (bắt đầu bằng dấu `>`, cùng kiểu
  với dòng `> **Trích dẫn:**` của file chunk), không nhét trong ngoặc kép giữa
  câu văn xuôi kiểu "Nguyên văn: '...' ". Người đọc phải phân biệt được ngay,
  chỉ bằng cách nhìn, đâu là chữ của văn bản pháp luật và đâu là lời diễn giải
  thêm của tôi.
- **"Tổng quan" nghĩa là SƠ ĐỒ NHÁNH TRƯỚC, không phải tóm tắt từng điều mục.**
  Người dùng nói nguyên văn: *"tôi cần bức tranh tổng quan (giống như là các
  nhánh cây trước)"*. Trả lời tổng quan thì dừng ở mức **tên văn bản và vai trò
  của nó**, kèm sơ đồ nhánh; không trích số hiệu điều mục, không nêu con số định
  lượng. Người dùng hỏi tiếp mới mở nhánh đó ra.
- **Bố cục cố định: KẾT LUẬN → GIẢI THÍCH CHI TIẾT → TỔNG KẾT, đánh số chính
  xác.** Người dùng nhắc nguyên văn: *"cần có bố cục nội dung, đánh mục số thứ
  tự chính xác, đi từ kết luận đến giải thích chi tiết xong tổng kết"*. Mọi câu
  trả lời vai kiến trúc sư dùng khung sau:

  ```
  I.   KẾT LUẬN            — trả lời thẳng câu hỏi trong 2–4 câu, trước mọi trích dẫn
  II.  GIẢI THÍCH CHI TIẾT — 1. → 2. → 3. …, mục con a) b) c); trích nguyên văn, ảnh
  III. TỔNG KẾT            — danh sách ngắn các điểm cần nhớ + cảnh báo hiệu lực
  ```

  Dùng chữ số La Mã cho ba phần lớn và `1.`, `a)` cho cấp dưới — **không** dùng
  dạng `1.1`, `2.3` vì dễ lẫn với số hiệu mục của quy chuẩn (mục 2.4.3, mục
  3.2.8). Số thứ tự phải liên tục, không nhảy, không trùng, không lẫn biểu tượng
  số (1️⃣) với chữ số thường. Câu trả lời tổng quan vẫn theo khung này: sơ đồ
  nhánh đặt ở phần I.
