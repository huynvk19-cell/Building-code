# Ba cách cho AI "ngồi lên" kho này

Từ dễ đến khó. Với một thư viện cỡ vài chục văn bản, **cách 1 hoặc 2 là đủ**.

## Cách 1 — Claude Projects (không cần code)

1. Tạo một Project trên claude.ai
2. Tải các file trong `chunks/` lên phần **Project knowledge**
   (mỗi Điều một file — Claude trích dẫn chính xác hơn là tải cả file lớn)
3. Dán nội dung `CLAUDE.md` vào ô **Custom instructions**

Mọi hội thoại trong Project đó đều đọc cùng một kho kiến thức. Nhược điểm:
mỗi lần cập nhật văn bản phải tải file lên lại thủ công.

## Cách 2 — GitHub connector / MCP (đúng ý "AI ngồi lên hệ thống" nhất)

Kết nối Claude thẳng vào repository này. Claude tìm và đọc file theo yêu cầu
thay vì phải nhớ hết trong đầu.

- Trên claude.ai: Settings → Connectors → GitHub, rồi cấp quyền cho repo này
- Trong Claude Code: repo đã sẵn ở máy, chỉ cần chạy `tools/search.py`

Ưu điểm: `git push` là AI thấy bản mới ngay, không phải tải lại gì cả.
`CLAUDE.md` được đọc tự động nên quy tắc trích dẫn luôn được áp dụng.

## Cách 3 — Vector database (chỉ khi kho thật lớn)

Khi lên tới hàng trăm văn bản và cần tìm kiếm ngữ nghĩa thực sự
("công trình cấp mấy thì cần giám sát trưởng?" — không trùng từ khóa nào):

1. Sinh embedding cho từng dòng trong `index/chunks.jsonl`
2. Nạp vào Chroma / Pinecone / pgvector
3. Bọc thành một MCP server để Claude gọi như một công cụ

Phần này cần code. **Chưa cần thiết ở quy mô hiện tại** — văn bản pháp luật
dùng thuật ngữ rất cố định ("chứng chỉ hành nghề", "hạng II", "chủ nhiệm"),
nên BM25 trong `tools/search.py` đã cho kết quả tốt.

## Vì sao chia chunk theo Điều?

Điều là đơn vị trích dẫn tự nhiên của văn bản pháp luật. Người ta nói
"theo Điều 33" chứ không nói "theo trang 27". Chia theo Điều nghĩa là:

- Kết quả tìm kiếm luôn là một đơn vị trích dẫn được
- Không có chunk nào bị cắt ngang giữa một quy định
- Metadata (chương, mục, số điều) đi kèm sẵn để AI dẫn nguồn đúng

Cách chia theo số ký tự cố định (512 token, 1000 ký tự...) sẽ cắt ngang câu và
làm mất ngữ cảnh — hỏng ngay ở chỗ quan trọng nhất với văn bản pháp luật.
