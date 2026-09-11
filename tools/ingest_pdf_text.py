#!/usr/bin/env python3
"""Chuyển PDF **có lớp văn bản thật** thành Markdown cho corpus.

Khác `tools/ingest_pdf.py`: script kia dành cho bản SCAN, phải đọc từng ảnh
trang bằng thị giác máy rồi chép tay vì OCR đánh rơi dấu tiếng Việt. Script này
dành cho bản ký số do cơ quan phát hành — chữ nằm sẵn trong PDF, trích ra là
chính xác tuyệt đối, không qua OCR.

**Vẫn phải mở vài trang bằng thị giác máy để đối chiếu** trước khi tin kết quả:
một số PDF có lớp văn bản sai lệch so với hình in.

Việc script làm:
  - bỏ dòng lặp ở đầu/chân trang (tên cơ quan, chữ ký số, số trang trơ trọi);
  - nối các dòng bị ngắt giữa câu thành đoạn văn liền mạch;
  - nhận diện `Chương I` + tiêu đề chương, `Điều 12. Tên điều` và đánh dấu
    theo đúng quy ước tiêu đề mà `tools/build_index.py` cần.

Chạy:
    python3 tools/ingest_pdf_text.py <file.pdf> > /tmp/thu.md
    python3 tools/ingest_pdf_text.py <file.pdf> --phu-luc   # không tách Điều
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    sys.exit("Cần PyMuPDF: pip install pymupdf")

# Tiêu đề chương thường bị gom chung một đoạn với tên chương viết HOA.
RE_CHUONG = re.compile(r"^Chương\s+([IVXLC]+)\b\s*(.*)$")
RE_DIEU = re.compile(r"^Điều\s+(\d+)\.\s*(.*)$")
# Tên điều đang dang dở khi kết thúc bằng dấu phẩy hoặc một từ nối/từ dẫn.
DANG_DO = re.compile(r"(?:,|\b(?:và|khoản|điểm|Điều|tên|của|số|tại|các))\s*$")
RE_BAT_DAU_THUONG = re.compile(r"^[a-zà-ỹ]")


def con_tiep(ten: str, dong_ke: str) -> bool:
    """Tên điều có bị ngắt dòng và còn nối tiếp ở dòng kế không?

    Ba tín hiệu, thử lần lượt:
      1. dòng kế bắt đầu bằng CHỮ THƯỜNG  → chắc chắn là phần nối tiếp
         ("...ngày 19 tháng 6" + "năm 2026 của Chính phủ...");
      2. tên kết thúc bằng dấu phẩy hoặc từ nối ("khoản", "điểm", "và"…);
      3. tên kết thúc bằng CHỮ SỐ *và* dòng kế mở đầu bằng "Điều"
         ("...điểm c khoản 1" + "Điều 44").

    Không dùng riêng "kết thúc bằng chữ số" làm tín hiệu, vì rất nhiều tên điều
    trọn vẹn kết thúc đúng như vậy ("Sửa đổi, bổ sung khoản 5 Điều 31").
    """
    ke = dong_ke.strip()
    if not ke or ke.startswith(("“", '"', "1.", "a)")) or RE_DIEU.match(ke):
        return bool(re.search(r"\d\s*$", ten)) and ke.startswith("Điều")
    if RE_BAT_DAU_THUONG.match(ke):
        return True
    if DANG_DO.search(ten):
        return True
    return bool(re.search(r"\d\s*$", ten)) and ke.startswith("Điều")
# Dòng rác lặp trên mọi trang của bản ký số.
RE_RAC = re.compile(
    r"^(?:\d{1,3}|Cơ quan phát hành:.*|Người ký:.*|Email:.*|Cơ quan:.*"
    r"|Thời gian ký:.*|CHÍNH PHỦ|_+)$"
)
# Dòng mở đầu một đoạn mới: "1. ", "a) ", "“1. ", "Chương", "Điều"…
RE_DAU_DOAN = re.compile(
    r"^\s*(?:[“\"]?\d+\.\s|[“\"]?[a-zđ]\)\s|[“\"]?\d+\.\d+\.\s|Chương\s|Điều\s|Mẫu\s"
    r"|Phụ lục\s|Căn cứ\s|Theo đề nghị\s|Chính phủ ban hành\s)"
)


def doc_text(pdf: Path) -> list[str]:
    doc = pymupdf.open(pdf)
    dong: list[str] = []
    for page in doc:
        for l in page.get_text().splitlines():
            l = l.rstrip()
            if not l.strip() or RE_RAC.match(l.strip()):
                continue
            dong.append(l)
    return dong


def gom_doan(dong: list[str]) -> list[str]:
    """Nối dòng bị ngắt giữa câu; giữ nguyên ranh giới đoạn."""
    doan: list[str] = []
    dem: list[str] = []

    def chot():
        if dem:
            doan.append(" ".join(x.strip() for x in dem).strip())
            dem.clear()

    gom_tieu_de = False
    for idx, l in enumerate(dong):
        st = l.strip()
        ke = dong[idx + 1] if idx + 1 < len(dong) else ""
        # Tiêu đề Điều là MỘT DÒNG RIÊNG trong bản in. Phải giữ ranh giới đó:
        # nếu gom chung với dòng kế rồi mới tách, tên điều sẽ nuốt mất phần
        # thân — đã gặp với Điều 38 ("Bãi bỏ một số quy định" hút luôn câu
        # "Bãi bỏ điểm i, điểm k khoản 2..." làm thân chunk rỗng).
        if RE_DIEU.match(st):
            chot()
            dem.append(l)
            if con_tiep(st, ke):
                gom_tieu_de = True      # tên điều bị ngắt dòng, còn nối tiếp
            else:
                chot()
            continue
        if gom_tieu_de:
            dem.append(l)
            if not con_tiep(" ".join(x.strip() for x in dem), ke):
                chot()
                gom_tieu_de = False
            continue
        if RE_DAU_DOAN.match(l) or RE_CHUONG.match(st):
            chot()
        dem.append(l)
        # Đoạn kết thúc rõ ràng bằng dấu chấm + ngoặc kép đóng.
        if l.rstrip().endswith(("”.", '".')):
            chot()
    chot()
    return doan


LA_MA = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV"]


def dinh_dang(doan: list[str], la_phu_luc: bool) -> list[str]:
    """Nhận diện tiêu đề Chương/Điều.

    Ràng buộc then chốt: **số Chương và số Điều phải tăng liên tiếp**. Không có
    ràng buộc này thì mọi DẪN CHIẾU CHÉO trong thân văn bản đều bị nhận nhầm
    thành tiêu đề — đã gặp thật: câu "...tên Chương III; tên Điều 23..." của
    Điều 8 sinh ra một "Chương III" giả, và "khoản 4 Điều 42." sinh ra một
    "Điều 42" giả nằm lọt giữa Điều 9.
    """
    ra: list[str] = []
    cho_chuong = 0   # chỉ số chương kế tiếp trong LA_MA
    cho_dieu = 1     # số Điều kế tiếp
    i = 0
    while i < len(doan):
        d = doan[i]
        m = RE_CHUONG.match(d.strip())
        if m and not la_phu_luc and cho_chuong < len(LA_MA) \
                and m.group(1) == LA_MA[cho_chuong]:
            cho_chuong += 1
            ten = re.sub(r"\s+", " ", m.group(2)).strip()
            j = i + 1
            # Tên chương có thể tràn sang đoạn sau nếu bị ngắt trang.
            while not ten and j < len(doan) and not RE_DIEU.match(doan[j]):
                ten = re.sub(r"\s+", " ", doan[j]).strip()
                j += 1
            ra += ["", f"## Chương {m.group(1)}. {ten}", ""]
            i = j
            continue
        m = RE_DIEU.match(d)
        if m and not la_phu_luc and int(m.group(1)) == cho_dieu:
            cho_dieu += 1
            so, ten = m.group(1), m.group(2).strip()
            if "“" in ten:
                ten, phan_du = ten.split("“", 1)
                doan.insert(i + 1, "“" + phan_du)
                ten = ten.strip()
            # Tên điều có thể tràn sang đoạn sau nếu chưa kết thúc bằng dấu câu.
            # Tên điều bị ngắt dòng thì nối tiếp; NHƯNG phải dừng khi gặp nội
            # dung được sửa đổi (mở bằng dấu ngoặc kép “), và chỉ nối khi tên
            # thật sự đang DANG DỞ. Không có điều kiện "dang dở" thì tên điều
            # nuốt luôn phần thân — đã gặp thật với Điều 38: tên hút mất câu
            # "Bãi bỏ điểm i, điểm k khoản 2..." làm thân chunk rỗng và bị loại.
            while (ten and not ten.endswith((".", ":")) and DANG_DO.search(ten)
                   and i + 1 < len(doan)):
                ke = doan[i + 1].strip()
                if RE_DIEU.match(ke) or ke.startswith(("1.", "“", '"', "a)")):
                    break
                ten = f"{ten} {ke}"
                i += 1
            ra += ["", f"### Điều {so}. {ten.rstrip('.').strip()}", ""]
            i += 1
            continue
        ra.append(re.sub(r"\s+", " ", d).strip())
        ra.append("")
        i += 1
    return ra


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--phu-luc", action="store_true",
                    help="phụ lục: không tách Chương/Điều, chỉ làm sạch đoạn")
    args = ap.parse_args()

    if not args.pdf.exists():
        sys.exit(f"Không thấy tệp: {args.pdf}")
    out = dinh_dang(gom_doan(doc_text(args.pdf)), args.phu_luc)
    text = "\n".join(out)
    print(re.sub(r"\n{3,}", "\n\n", text).strip())


if __name__ == "__main__":
    main()
