# Hướng dẫn sử dụng

## 1. Tra cứu hằng ngày

```bash
python3 tools/search.py "câu hỏi của bạn"
```

Các tùy chọn hữu ích:

| Tùy chọn | Tác dụng |
|---|---|
| `--k 10` | Lấy 10 kết quả thay vì 5 |
| `--full` | In toàn văn Điều thay vì trích đoạn |
| `--khong-dau` | Gõ không dấu vẫn tìm được (`chung chi hanh nghe`) |
| `--loai dieu` | Chỉ tìm trong các Điều (nghị định, luật) |
| `--loai muc` | Chỉ tìm trong các mục của quy chuẩn (1.1, 2.3, H.2…) |
| `--loai bang` | Chỉ tìm trong các bảng tra cứu (Bảng A.1, B.1…) |
| `--loai bieu-mau` | Chỉ tìm biểu mẫu (Mẫu số 01…) |
| `--doc 212-2026-nd-cp` | Giới hạn trong một văn bản |
| `--json` | Xuất JSON cho script hoặc agent đọc |

Ví dụ thực tế:

```bash
# Tôi có 5 năm kinh nghiệm, xin được chứng chỉ hạng mấy?
python3 tools/search.py --full "thời gian kinh nghiệm hạng I hạng II hạng III"

# Hồ sơ xin cấp chứng chỉ gồm những gì?
python3 tools/search.py --full "hồ sơ đề nghị cấp chứng chỉ hành nghề"

# Chuyên ngành kiến trúc được cấp chứng chỉ lĩnh vực nào?
python3 tools/search.py --loai phu-luc "chuyên ngành đào tạo kiến trúc"

# Cần mẫu đơn nào?
python3 tools/search.py --loai bieu-mau "đơn đề nghị cấp chứng chỉ"
```

Về phòng cháy chữa cháy (QCVN 10:2025/BCA):

```bash
# Nhà tôi có phải lắp báo cháy / chữa cháy tự động không?
python3 tools/search.py --full --loai bang "chung cư báo cháy tự động số tầng"

# Bao nhiêu tầng thì phải có họng nước chữa cháy trong nhà?
python3 tools/search.py --full "họng nước chữa cháy trong nhà chung cư số tầng"

# Lưu lượng nước chữa cháy ngoài nhà cho khu dân cư?
python3 tools/search.py --full --doc qcvn-10-2025-bca "lưu lượng nước chữa cháy ngoài nhà dân số"
```

> **Thứ tự tra bảng PCCC** (mục 1.5.9 QCVN 10:2025/BCA):
> **Bảng A.1** (toàn nhà) → **Bảng A.2** (hạng mục/khu vực) → **Bảng A.3**
> (gian phòng) → **Bảng A.4** (thiết bị). Nhớ xem thêm **mục 1.5.11** liệt kê các
> khu vực KHÔNG phải trang bị (phòng tắm, vệ sinh, cầu thang bộ, hành lang bên…).

## 2. Đọc thẳng khi đã biết số Điều

```bash
cat chunks/212-2026-nd-cp/dieu-33-*.md      # Điều 33
cat corpus/nghi-dinh/212-2026-nd-cp/muc-luc.md   # xem toàn bộ mục lục
```

## 3. Thêm một văn bản mới

**Bước 1 — PDF sang ảnh + OCR nháp**

```bash
python3 tools/ingest_pdf.py ~/Downloads/nghi-dinh-moi.pdf --ten 213-2026-nd-cp
```

Kết quả nằm trong `.ingest/213-2026-nd-cp/` (không được commit).

**Bước 2 — Hiệu đính bằng AI**

Đưa các file `trang-*.png` cho Claude và yêu cầu:

> Đọc các trang này và chép lại chính xác thành Markdown tiếng Việt.
> Giữ nguyên dấu tiếng Việt. Dùng `## Chương I. TÊN`, `### Mục 1. TÊN`,
> `### Điều 1. Tên điều` làm tiêu đề. File `ocr-nhap.txt` chỉ dùng để đối chiếu.

**Đừng bỏ qua bước này.** OCR tiếng Việt sai dấu rất nhiều, mà với văn bản
pháp luật sai một dấu là sai nghĩa.

**Bước 3 — Lưu vào corpus**

`corpus/nghi-dinh/213-2026-nd-cp/toan-van.md`, mở đầu bằng front matter:

```yaml
---
doc_id: "213-2026-nd-cp"
so_hieu: "213/2026/NĐ-CP"
loai_van_ban: "Nghị định"
co_quan_ban_hanh: "Chính phủ"
ngay_ban_hanh: "2026-07-01"
tieu_de: "..."
linh_vuc: ["xây dựng"]
nguon: "Cổng thông tin điện tử Chính phủ"
ngon_ngu: "vi"
---
```

Phụ lục để trong `corpus/nghi-dinh/213-2026-nd-cp/phu-luc/`.

**Bước 4 — Dựng lại chỉ mục và commit**

```bash
python3 tools/build_index.py
git add -A
git commit -m "Thêm Nghị định 213/2026/NĐ-CP"
git push
```

## 4. Khi một văn bản bị sửa đổi

Sửa thẳng trong `corpus/`, chạy lại `build_index.py`, rồi commit với thông điệp
nói rõ điều gì đổi. Git giữ lại bản cũ — `git log -p` xem được lịch sử,
`git show <commit>:<file>` lấy lại bản tại một thời điểm.

Nếu văn bản mới **thay thế** văn bản cũ, giữ cả hai và ghi rõ trong front matter:

```yaml
trang_thai: "hết hiệu lực từ 2027-01-01"
bi_thay_the_boi: "215/2026/NĐ-CP"
```

## 5. Quy ước tiêu đề (bộ chia chunk dựa vào đây)

Khai báo `cau_truc` trong front matter để chọn kiểu cắt.

**`cau_truc: "dieu"`** (mặc định — Nghị định, Luật, Thông tư):

| Cấp | Cú pháp |
|---|---|
| Chương | `## Chương I. NHỮNG QUY ĐỊNH CHUNG` |
| Mục | `### Mục 1. TÊN MỤC` |
| Điều | `### Điều 1. Phạm vi điều chỉnh` |

**`cau_truc: "muc"`** (Quy chuẩn QCVN, Tiêu chuẩn TCVN):

| Cấp | Cú pháp |
|---|---|
| Phần | `## 1 QUY ĐỊNH CHUNG` |
| Mục | `### 1.1 Phạm vi điều chỉnh` |

Phần không có mục con (ví dụ `## 3 QUY ĐỊNH VỀ QUẢN LÝ`) thì tự nó là một chunk.

**Phụ lục** — khai báo `chia_theo` trong front matter của từng file:

| `chia_theo` | Cắt tại |
|---|---|
| `"Mẫu số"` | `## Mẫu số 01 — Tên mẫu` |
| `"Bảng"` | `## Bảng A.1 - Đối với nhà` |
| `"H."` | `## H.1 Yêu cầu thiết kế…` |
| *(không khai báo)* | giữ nguyên cả phụ lục làm một chunk |

Sai cú pháp thì `build_index.py` sẽ không tách được mục đó thành chunk riêng.
