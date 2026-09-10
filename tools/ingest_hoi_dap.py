#!/usr/bin/env python3
"""Chuyển tệp hỏi đáp của Cục Cảnh sát PCCC và CNCH thành corpus.

Nguồn là bản thu thập từ chuyên mục hỏi đáp công dân trên cổng thông tin
canhsatpccc.gov.vn. Đây KHÔNG phải văn bản quy phạm pháp luật — xem phần
`gia_tri_phap_ly` trong front matter sinh ra. Script này chỉ:

  - tách từng cặp câu hỏi / câu trả lời;
  - LOẠI BỎ các mục là đơn thư phản ánh về cơ sở, cá nhân cụ thể (xem
    LOAI_TRU bên dưới) — chúng chứa dữ liệu cá nhân và không mang nội dung
    hướng dẫn nào;
  - GỘP các mục dùng chung một câu trả lời thành một chunk, giữ đủ mọi câu hỏi;
  - xếp vào nhóm chủ đề theo bộ quy tắc từ khoá cố định;
  - chuẩn hoá khoảng trắng để đọc được (KHÔNG sửa một chữ nào của nội dung).

Chạy:  python3 tools/ingest_hoi_dap.py <tệp nguồn.md>
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICH = ROOT / "corpus" / "huong-dan" / "hoi-dap-c07"

RE_FAQ = re.compile(
    r"\n## FAQ \d+\n\n\*\*ID:\*\* (\d+)\n\n\*\*Source:\*\* (\S+)\n\n"
    r"### Câu hỏi\n\n(.*?)\n\n### Trả lời\n\n(.*?)(?=\n\n---\n|\Z)",
    re.S,
)

# Đơn thư phản ánh về một cơ sở/cá nhân cụ thể. Câu trả lời chỉ là thông báo
# chuyển đơn về Công an địa phương, không có nội dung hướng dẫn; phần hỏi thì
# mang tên người, địa chỉ nhà, thư điện tử, số điện thoại của bên thứ ba.
LOAI_TRU = {
    "632", "634", "704", "706", "758", "850", "852", "917", "919", "959",
    "963", "1206", "1339", "1341", "1343", "1466", "1551", "1553",
}

# Nhóm chủ đề. Quy tắc đầu tiên khớp sẽ thắng, nên thứ tự ở đây là thứ tự ưu
# tiên: cái hẹp đứng trước cái rộng.
NHOM: list[tuple[str, str, tuple[str, ...]]] = [
    ("01", "Nhà ở riêng lẻ và nhà ở kết hợp sản xuất, kinh doanh",
     ("nhà ở riêng lẻ", "nhà ở kết hợp", "nhà trọ", "hộ gia đình", "nhà ở hộ")),
    ("02", "Cơ sở kinh doanh karaoke, vũ trường",
     ("karaoke", "vũ trường")),
    ("03", "Đối tượng và thủ tục thẩm duyệt thiết kế, nghiệm thu",
     ("thẩm duyệt", "nghiệm thu", "phụ lục v", "phụ lục iii", "hồ sơ thiết kế",
      "thuộc diện thẩm duyệt")),
    ("04", "Kiểm định phương tiện phòng cháy chữa cháy",
     ("kiểm định", "giấy chứng nhận kiểm định", "tem kiểm định")),
    ("05", "Trang bị hệ thống và phương tiện phòng cháy chữa cháy",
     ("trang bị", "bình chữa cháy", "họng nước", "đầu báo", "sprinkler",
      "chữa cháy tự động", "báo cháy", "truyền tin báo cháy", "tcvn 3890")),
    ("06", "Giải pháp kết cấu, ngăn cháy và bậc chịu lửa",
     ("chịu lửa", "sơn chống cháy", "bậc chịu lửa", "khoang cháy",
      "ngăn cháy", "vách ngăn", "tường ngăn")),
    ("07", "Thoát nạn",
     ("thoát nạn", "lối ra", "buồng thang", "thang bộ", "hành lang", "lối thoát")),
    ("08", "Giao thông và cấp nước phục vụ chữa cháy",
     ("đường cho xe chữa cháy", "bãi đỗ", "trụ nước", "cấp nước", "bể nước",
      "xe chữa cháy")),
    ("09", "Điều kiện kinh doanh dịch vụ, huấn luyện, chứng chỉ, bảo hiểm",
     ("huấn luyện", "chứng chỉ", "bảo hiểm", "tập huấn", "kinh doanh dịch vụ",
      "chứng nhận đủ điều kiện")),
    ("10", "Kiểm tra, xử phạt, tạm đình chỉ",
     ("xử phạt", "tạm đình chỉ", "đình chỉ", "kiểm tra an toàn", "vi phạm hành chính")),
    ("11", "Áp dụng chuyển tiếp và công trình hiện hữu",
     ("chuyển tiếp", "đã đưa vào sử dụng", "công trình hiện hữu", "trước ngày")),
    ("99", "Nội dung khác", ()),
]


def go_dau(s: str) -> str:
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()


def chuan_hoa(text: str) -> str:
    """Làm cho khối văn bản dính liền đọc được. KHÔNG đổi một ký tự nội dung nào.

    Bản thu thập nối các gạch đầu dòng vào cuối câu trước ("quy định:- Đối
    với…"). Ở đây chỉ CHÈN ký tự xuống dòng trước dấu gạch đầu dòng, không
    thêm, bớt hay thay bất kỳ chữ nào.
    """
    text = text.replace("\r\n", "\n").strip()
    # Gạch đầu dòng dính vào chữ hoặc dấu câu ngay trước nó.
    text = re.sub(r"(?<=[^\s\n])([-–+])\s(?=[A-ZĐÀ-Ỹ])", r"\n\1 ", text)
    # Mục đánh số dính liền: "…như sau:1. Kết cấu…"
    text = re.sub(r"(?<=[:;.])(\d{1,2}\.)\s(?=[A-ZĐÀ-Ỹ])", r"\n\n\1 ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def nhan(cau_hoi: str, gioi_han: int = 95) -> str:
    """Nhãn hiển thị, lấy từ câu đầu tiên có nội dung của phần hỏi.

    Chỉ dùng để hiển thị và tìm kiếm — trích dẫn luôn dựa vào số hiệu câu hỏi.
    """
    bo_dau_thu = re.compile(
        r"^(kính (gửi|gởi)|xin (chào|hỏi|phép)|chào|tôi xin|em xin|cho (tôi|em) hỏi"
        r"|kinh gui)\b[^.;:\n]*[.;:\n]?\s*",
        re.I,
    )
    t = " ".join(cau_hoi.split())
    truoc = None
    while truoc != t:
        truoc, t = t, bo_dau_thu.sub("", t).strip()
    cau = re.split(r"(?<=[.?;])\s+", t)[0] if t else ""
    if not cau:
        cau = t
    cau = cau.strip(" .;:?")
    if len(cau) > gioi_han:
        cau = cau[:gioi_han].rsplit(" ", 1)[0] + "…"
    return cau or "(không rõ nội dung hỏi)"


def slugify(text: str, max_len: int = 60) -> str:
    s = go_dau(text.replace("đ", "d").replace("Đ", "D")).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:max_len].rstrip("-")


def xep_nhom(cau_hoi: str, cau_tra_loi: str) -> tuple[str, str]:
    s = (cau_hoi + " " + cau_tra_loi).lower()
    for ma, ten, tu_khoa in NHOM:
        if any(w in s for w in tu_khoa):
            return ma, ten
    return NHOM[-1][0], NHOM[-1][1]


def doc_nguon(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    muc = []
    for ma_id, url, hoi, dap in RE_FAQ.findall(text):
        muc.append(
            {
                "id": ma_id,
                "url": url,
                "hoi": chuan_hoa(hoi),
                "dap": chuan_hoa(dap),
            }
        )
    return muc


def gom_trung(muc: list[dict]) -> list[dict]:
    """Gộp các mục dùng chung một câu trả lời thành một mục, giữ đủ mọi câu hỏi."""
    theo_dap: dict[str, list[dict]] = defaultdict(list)
    for m in muc:
        khoa = hashlib.sha1(" ".join(m["dap"].split()).encode()).hexdigest()
        theo_dap[khoa].append(m)

    ket_qua = []
    for nhom_muc in theo_dap.values():
        dau = dict(nhom_muc[0])
        dau["cac_cau_hoi"] = [(m["id"], m["url"], m["hoi"]) for m in nhom_muc]
        ket_qua.append(dau)
    ket_qua.sort(key=lambda m: int(m["id"]))
    return ket_qua


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("nguon", type=Path, help="tệp hỏi đáp đã thu thập (.md)")
    ap.add_argument("--dich", type=Path, default=DICH)
    args = ap.parse_args()

    if not args.nguon.exists():
        sys.exit(f"Không thấy tệp nguồn: {args.nguon}")

    tho = doc_nguon(args.nguon)
    print(f"Đọc được {len(tho)} mục hỏi đáp.")

    giu = [m for m in tho if m["id"] not in LOAI_TRU]
    print(f"Loại bỏ {len(tho) - len(giu)} mục là đơn thư phản ánh về cơ sở, cá nhân cụ thể.")

    muc = gom_trung(giu)
    gop = sum(1 for m in muc if len(m["cac_cau_hoi"]) > 1)
    print(f"Gộp {gop} nhóm dùng chung câu trả lời → còn {len(muc)} chunk.")

    theo_nhom: dict[str, list[dict]] = defaultdict(list)
    for m in muc:
        ma, ten = xep_nhom(m["hoi"], m["dap"])
        m["nhom_ma"], m["nhom_ten"] = ma, ten
        theo_nhom[ma].append(m)

    dem = Counter(m["nhom_ma"] for m in muc)
    for ma, ten, _ in NHOM:
        if dem[ma]:
            print(f"  {ma}  {dem[ma]:>3}  {ten}")

    args.dich.mkdir(parents=True, exist_ok=True)
    ghi_toan_van(args.dich, muc, theo_nhom)
    print(f"\nĐã ghi {args.dich / 'toan-van.md'}")


def ghi_toan_van(dich: Path, muc: list[dict], theo_nhom: dict[str, list[dict]]) -> None:
    fm = f'''---
doc_id: "hoi-dap-c07"
so_hieu: "Hỏi đáp C07"
loai_van_ban: "Hỏi đáp nghiệp vụ"
co_quan_ban_hanh: "Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ (C07) - Bộ Công an"
ngay_ban_hanh: "KHÔNG XÁC ĐỊNH"
tieu_de: "Giải đáp của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ đối với câu hỏi của công dân và doanh nghiệp"
linh_vuc: ["phòng cháy chữa cháy", "thẩm duyệt thiết kế", "nghiệm thu", "kiểm định phương tiện", "trang bị phương tiện"]
gia_tri_phap_ly: "THAM KHẢO - KHÔNG PHẢI VĂN BẢN QUY PHẠM PHÁP LUẬT"
ngay_hieu_luc: "KHÔNG ÁP DỤNG"
can_cu_hieu_luc: "Tài liệu giải đáp nghiệp vụ, không có hiệu lực pháp lý. Căn cứ bắt buộc luôn là văn bản quy phạm pháp luật mà câu trả lời viện dẫn."
thay_the: []
het_hieu_luc: ""
sua_doi_boi: []
dieu_khoan_chuyen_tiep: ""
nguon: "https://canhsatpccc.gov.vn/vi/faq-contact/citizen-faq (thu thập {len(muc)} mục dùng được)"
phuong_phap_so_hoa: "Thu thập từ cổng thông tin điện tử; chỉ chuẩn hoá khoảng trắng và xuống dòng, không sửa chữ"
trang_thai: "hoàn chỉnh"
ngon_ngu: "vi"
cau_truc: "hoi-dap"
---

# Giải đáp của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ

> **CẢNH BÁO BẮT BUỘC ĐỌC.** Toàn bộ nội dung dưới đây là **giải đáp nghiệp vụ**
> của cơ quan quản lý nhà nước đối với câu hỏi của công dân và doanh nghiệp.
> Đây **không phải văn bản quy phạm pháp luật** và **không có hiệu lực pháp lý
> bắt buộc**. Giá trị của nó là cho biết cơ quan thẩm duyệt **thực tế đang hiểu
> và áp dụng quy định như thế nào** — tức là kinh nghiệm thực tiễn, không phải
> căn cứ pháp lý.
>
> Khi trả lời câu hỏi của người dùng:
>
> 1. **Căn cứ pháp lý luôn phải là văn bản quy phạm pháp luật** mà câu trả lời
>    viện dẫn, không phải bản thân câu trả lời này.
> 2. **Các mục hỏi đáp không mang ngày trả lời.** Nhiều câu viện dẫn văn bản
>    đã hết hiệu lực (Nghị định số 79/2014/NĐ-CP, Nghị định số 136/2020/NĐ-CP,
>    Nghị định số 50/2024/NĐ-CP, QCVN 06:2020/BXD, QCVN 06:2021/BXD,
>    TCVN 3890:2009). Phải kiểm tra văn bản được viện dẫn còn hiệu lực không
>    trước khi dùng lại nội dung.
> 3. **Phần lớn câu trả lời viện dẫn Nghị định số 105/2025/NĐ-CP** quy định chi
>    tiết Luật Phòng cháy, chữa cháy và cứu nạn, cứu hộ. Văn bản đó **chưa có
>    trong kho**, nên không tự kiểm chứng được nội dung viện dẫn.
> 4. Khi trích dẫn, phải nói rõ đây là giải đáp nghiệp vụ, ví dụ: *"Theo giải
>    đáp số 60 của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ (tài
>    liệu tham khảo, không phải văn bản quy phạm pháp luật)…"*

'''
    lines = [fm]
    for ma, ten, _ in NHOM:
        ds = theo_nhom.get(ma)
        if not ds:
            continue
        lines.append(f"## Nhóm {ma}. {ten}\n")
        for m in ds:
            lines.append(f"### HĐ-{m['id']} {nhan(m['hoi'])}\n")
            if len(m["cac_cau_hoi"]) == 1:
                lines.append("**Câu hỏi**\n")
                lines.append(m["hoi"] + "\n")
            else:
                ids = ", ".join(f"HĐ-{i}" for i, _, _ in m["cac_cau_hoi"])
                lines.append(
                    f"**Câu hỏi** — {len(m['cac_cau_hoi'])} câu hỏi khác nhau "
                    f"({ids}) được cơ quan trả lời bằng cùng một nội dung.\n"
                )
                for i, _, h in m["cac_cau_hoi"]:
                    lines.append(f"*HĐ-{i}:* {h}\n")
            lines.append(
                "**Trả lời của Cục Cảnh sát Phòng cháy chữa cháy và Cứu nạn cứu hộ**\n"
            )
            lines.append(m["dap"] + "\n")
            for i, u, _ in m["cac_cau_hoi"]:
                lines.append(f"> Nguồn HĐ-{i}: {u}\n")
    (dich / "toan-van.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
