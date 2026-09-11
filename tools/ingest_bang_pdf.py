#!/usr/bin/env python3
"""Trích BẢNG TRA từ PDF có lớp văn bản, giữ đúng quan hệ hàng - cột.

Vì sao cần công cụ riêng, không dùng `tools/ingest_pdf_text.py`: với một bảng,
lớp văn bản chỉ cho ra **một chuỗi ô** và **mất hoàn toàn thông tin ô đó thuộc
cột nào**. Với Thông tư 06/2021/TT-BXD, chuỗi phẳng của Bảng 1.1 đọc là
"Trường tiểu học · Tổng số học sinh toàn trường · ≥ 700 · < 700" — không cách
nào biết ≥ 700 là cấp II còn < 700 là cấp III. Đoán sai một cột là sai cấp công
trình, tức sai toàn bộ đường đi của hồ sơ.

`page.find_tables()` dựng lại lưới từ chính đường kẻ in trong PDF, nên quan hệ
hàng - cột là **đọc ra được, không phải suy đoán**.

CHỮ XOAY NGANG: Công báo in bảng khổ lớn nằm ngang trên trang dọc. Trang khai
`rotation = 0` nhưng từng dòng chữ được vẽ xoay 90 độ, nên `find_tables()` nhìn
thấy một lưới xoay và trả về kết quả vô nghĩa. Phải gọi `page.set_rotation(90)`
TRƯỚC khi dò — lúc đó PyMuPDF quy đổi toạ độ và bảng trở lại đúng chiều. Script
tự phát hiện việc này qua hướng của các dòng chữ.

Chạy:
    python3 tools/ingest_bang_pdf.py <file.pdf> --tu-trang 6 --den-trang 36
    python3 tools/ingest_bang_pdf.py <file.pdf> --tu-trang 6 --den-trang 36 \
        --anh corpus/.../bang --tien-to bang
"""
from __future__ import annotations

import argparse
import re
import sys
import warnings
from collections import Counter
from pathlib import Path

warnings.filterwarnings("ignore")

try:
    import pymupdf
except ImportError:
    sys.exit("Cần PyMuPDF: pip install pymupdf")

DPI_ANH = 200
# Tiêu đề bảng thật: sau số hiệu là tên bảng, luôn mở đầu bằng CHỮ HOA
# ("Bảng 1.4 Phân cấp công trình phục vụ giao thông vận tải"). Câu viện dẫn bị
# ngắt trang thành "Bảng 1.3 để xác định cấp theo mức độ quan trọng…" mở đầu
# bằng chữ thường — không có ràng buộc này thì nó chiếm chỗ tiêu đề thật và
# Bảng 1.4 biến mất khỏi kho cùng cả bảy trang của nó.
RE_TEN_BANG = re.compile(r"^Bảng\s+(\d+(?:\.\d+)?)\.?\s+(\S.*)$", re.M)
# Chữ hoa được kiểm bằng `str.isupper()`, KHÔNG bằng dải `[A-ZĐÀ-Ỹ]`: dải đó
# tính theo mã Unicode nên nuốt luôn chữ thường "đ" (U+0111) nằm giữa "À"
# (U+00C0) và "Ỹ" (U+1EF8) — và thế là "Bảng 1.3 để xác định cấp…" vẫn lọt.
RE_PHU_LUC = re.compile(r"^(Phụ lục\s+[IVX]+)\s*$", re.M)
# Dòng rác lặp ở đầu mọi trang Công báo.
RE_RAC = re.compile(r"^(?:\d{1,3}|CÔNG BÁO/.*)$")


def goc_xoay(trang) -> int:
    """Chữ trên trang này bị vẽ xoay bao nhiêu độ?

    Đọc hướng của từng dòng (`dir`): (1,0) là nằm ngang bình thường, (0,-1) là
    xoay 90 độ. Lấy hướng chiếm đa số vì tiêu đề chạy ở mép trang vẫn nằm ngang.
    """
    huong = Counter()
    for khoi in trang.get_text("dict")["blocks"]:
        for d in khoi.get("lines", []):
            huong[tuple(round(x) for x in d["dir"])] += len(d["spans"])
    if not huong:
        return 0
    return 90 if huong.most_common(1)[0][0] == (0, -1) else 0


def o_sach(o: str | None) -> str:
    """Gộp dòng trong một ô thành một dòng, giữ nguyên chữ."""
    return re.sub(r"\s+", " ", (o or "").replace("\n", " ")).strip()


def hang_markdown(hang: list[str]) -> str:
    # Thanh dọc trong nội dung sẽ phá cấu trúc bảng Markdown.
    return "| " + " | ".join(o.replace("|", "\\|") for o in hang) + " |"


def doc_trang(trang, so_cot: int | None) -> list[list[str]]:
    """Các hàng DỮ LIỆU của trang, đã bỏ hai dòng tiêu đề lặp lại."""
    tb = trang.find_tables()
    ra: list[list[str]] = []
    for t in tb.tables:
        # Khối chú thích cuối trang cũng bị nhận thành "bảng" 2 cột — loại bỏ
        # bằng cách chỉ nhận bảng có đúng số cột của lưới phân cấp.
        if so_cot and t.col_count != so_cot:
            continue
        hang = [[o_sach(o) for o in r] for r in t.extract()]
        # Hai dòng đầu của MỌI trang là tiêu đề lặp ("STT | Loại… | Cấp công
        # trình" rồi "Đặc biệt | I | II | III | IV"). Giữ lại sẽ nhân tiêu đề
        # lên hàng chục lần giữa thân bảng.
        while hang and (hang[0][0] == "STT" or set(hang[0][3:]) >= {"I", "II", "III"}):
            hang.pop(0)
        ra += [h for h in hang if any(h)]
    return ra


# Đầu một đoạn văn xuôi trong phụ lục: "1.", "a)", "- ", "3.1 Ví dụ 1:".
# LƯU Ý khi cắt theo ví dụ: cùng một bản in dùng CẢ dấu hai chấm lẫn dấu
# gạch ngang sau số hiệu ("Ví dụ 1: …" nhưng "Ví dụ 5 - …"). Chỉ nhận dấu
# hai chấm thì Ví dụ 5 và Ví dụ 12 của Phụ lục III Thông tư 06/2021/TT-BXD
# không thành chunk riêng mà bị nuốt vào ví dụ liền trước.
RE_DAU_DOAN_PL = re.compile(r"^(?:\d+(?:\.\d+)*[.)]?\s|[a-zđ]\)\s|[-–—]\s|Ví dụ\s)")


def van_xuoi_trang(trang) -> list[str]:
    """Toàn bộ văn xuôi của một trang KHÔNG có bảng.

    Phụ lục II kết thúc bằng phần "Cách xác định Chiều cao, Số tầng" và Phụ lục
    III là các ví dụ tính cấp — đều là văn xuôi thuần, nhưng vẫn in xoay ngang
    nên phải đi qua cùng đường xử lý xoay. Bỏ các trang này là mất chính phần
    định nghĩa cách ĐO những tiêu chí mà Bảng 2 dùng để phân cấp.
    """
    dong = [l.strip() for l in trang.get_text().split("\n") if l.strip()]
    doan: list[str] = []
    for l in dong:
        if RE_RAC.match(l) or RE_PHU_LUC.match(l):
            continue
        if RE_DAU_DOAN_PL.match(l) or not doan:
            doan.append(l)
        else:
            doan[-1] = f"{doan[-1]} {l}"
    return [re.sub(r"\s+", " ", d).strip() for d in doan if len(d) > 3]


def la_tieu_de_bang(dong: str) -> re.Match | None:
    """Dòng này có phải TIÊU ĐỀ BẢNG thật không?

    Một dòng mở đầu bằng "Bảng 1.3" chưa chắc là tiêu đề: câu viện dẫn bị ngắt
    trang thành "Bảng 1.3 để xác định cấp theo mức độ quan trọng…" cũng thế.
    Tên bảng thật luôn mở đầu bằng CHỮ HOA. Kiểm bằng `str.isupper()` chứ không
    bằng dải `[A-ZĐÀ-Ỹ]` — dải đó nuốt luôn "đ" (U+0111) nằm giữa "À" và "Ỹ",
    nên "để" vẫn lọt. Một hàm dùng chung cho cả hai chỗ cần kiểm, vì lần trước
    sửa mỗi chỗ một kiểu đã làm ghi chú của Bảng 1.3 bị cắt mất hai gạch đầu dòng.
    """
    m = RE_TEN_BANG.match(dong.strip())
    return m if m and m.group(2).strip()[:1].isupper() else None


def ghi_chu_cua_trang(trang) -> list[tuple[int, str]]:
    """Khối "Ghi chú" đi kèm bảng, lấy từ văn bản tuyến tính của trang.

    Không dò theo hình học: khung mà `find_tables()` trả về phủ trùm luôn khối
    ghi chú in ngay dưới bảng, nên lọc theo toạ độ sẽ loại mất chính nó và chỉ
    để lọt vài mảnh cụt. Văn bản tuyến tính thì giữ đúng thứ tự đọc, và khối
    ghi chú luôn mở bằng dòng "Ghi chú:" rồi tới các gạch đầu dòng.

    Bỏ những ghi chú này là đánh rơi quy định thật — ví dụ ghi chú (*) của
    Bảng 1.3 quy định quy đổi 6 chỗ để xe mô tô bằng 1 chỗ để xe ô tô, thứ
    quyết định diện tích tính cấp của một nhà để xe hỗn hợp.
    """
    dong = [l.strip() for l in trang.get_text().split("\n") if l.strip()]
    ra: list[tuple[int, str]] = []
    dang_ghi = False
    for vi_tri, l in enumerate(dong):
        if l.startswith("Ghi chú"):
            dang_ghi = True
            if l.rstrip(":").strip() != "Ghi chú":
                ra.append((vi_tri, l))   # ghi chú viết liền một dòng
            continue
        if not dang_ghi:
            continue
        # Dừng khi sang bảng kế hoặc gặp lại dòng tiêu đề lưới.
        if la_tieu_de_bang(l) or l in ("Cấp công trình", "STT") or RE_RAC.match(l):
            dang_ghi = False
            continue
        if l.startswith(("-", "–", "—")):
            ra.append((vi_tri, l))
        elif ra:
            ra[-1] = (ra[-1][0], f"{ra[-1][1]} {l}")   # dòng ngắt giữa chừng
    return [(v, re.sub(r"\s+", " ", x).strip()) for v, x in ra]


def vi_tri_tieu_de_bang(trang) -> int | None:
    """Dòng thứ mấy của trang là tiêu đề bảng ĐẦU TIÊN?

    Cần biết để gắn ghi chú đúng bảng: khi một trang vừa kết thúc bảng trước
    vừa mở bảng sau, khối "Ghi chú" in GIỮA hai bảng và thuộc về bảng TRƯỚC.
    Không phân biệt theo vị trí thì ghi chú của Bảng 1.2 bị treo dưới tiêu đề
    Bảng 1.3 — vẫn còn trong kho nhưng chú giải sai bảng, còn tệ hơn mất.
    """
    dong = [l.strip() for l in trang.get_text().split("\n") if l.strip()]
    for i, l in enumerate(dong):
        if la_tieu_de_bang(l):
            return i
    return None


def tieu_de_luoi(trang, so_cot: int | None) -> list[str] | None:
    for t in trang.find_tables().tables:
        if so_cot and t.col_count != so_cot:
            continue
        r = t.extract()
        if len(r) >= 2 and o_sach(r[0][0]) == "STT":
            tren = [o_sach(x) for x in r[0]]
            duoi = [o_sach(x) for x in r[1]]
            # Ô "Cấp công trình" trải 5 cột; ghép hai tầng tiêu đề lại.
            return [d or t_ for t_, d in zip(tren, duoi)]
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--tu-trang", type=int, required=True)
    ap.add_argument("--den-trang", type=int, required=True)
    ap.add_argument("--so-cot", type=int, default=8,
                    help="chỉ nhận bảng có đúng số cột này (mặc định 8)")
    ap.add_argument("--anh", type=Path, help="thư mục lưu ảnh từng trang bảng")
    ap.add_argument("--tien-to", default="bang")
    a = ap.parse_args()

    if not a.pdf.exists():
        sys.exit(f"Không thấy tệp: {a.pdf}")
    # PyMuPDF in một dòng gợi ý ra STDOUT ngay lần gọi find_tables() đầu tiên;
    # nếu không chặn thì nó lọt vào chính bản trích và thành dòng đầu corpus.
    import contextlib, io
    _nuot = contextlib.redirect_stdout(io.StringIO())
    _nuot.__enter__()
    doc = pymupdf.open(a.pdf)

    ten_bang: dict[int, list[tuple[str, str]]] = {}   # trang -> [(số hiệu, tên)]
    phu_luc: dict[int, str] = {}
    for i in range(a.tu_trang, a.den_trang + 1):
        t = doc[i - 1].get_text()
        dong = t.split("\n")
        for k, l in enumerate(dong):
            m = la_tieu_de_bang(l)
            if not m:
                continue
            ten = m.group(2).strip()
            # Tên bảng dài bị bản in ngắt giữa chừng ("…nông nghiệp và phát" +
            # "triển nông thôn"); dòng nối tiếp luôn mở đầu bằng chữ thường.
            j = k
            while j + 1 < len(dong) and dong[j + 1].strip()[:1].islower():
                j += 1
                ten = f"{ten} {dong[j].strip()}"
            ten_bang.setdefault(i, []).append(
                (m.group(1), re.sub(r"\s+", " ", ten).strip()))
        m = RE_PHU_LUC.search(t)
        if m:
            phu_luc[i] = m.group(1)

    dem_trang: Counter[str] = Counter()
    hien: str | None = None
    ra: list[str] = []
    for i in range(a.tu_trang, a.den_trang + 1):
        trang = doc[i - 1]
        if goc_xoay(trang) == 90:
            trang.set_rotation(90)
        # Dấu mốc trang, đặt TRƯỚC mọi thứ khác của trang: cần để gắn ảnh đúng
        # trang chứa từng nhóm công trình. Gắn trọn bộ ảnh của cả bảng vào mọi
        # nhóm thì một nhóm của Bảng 1.2 mang theo 15 ảnh, phần lớn không liên
        # quan. Đặt sau tiêu đề bảng thì trang đầu của bảng bị mất dấu.
        ra.append(f"<!-- trang {i} -->")

        if i in phu_luc:
            ra += ["", f"# {phu_luc[i]}", ""]
        co_bang = any(t.col_count == a.so_cot
                      for t in trang.find_tables().tables)
        if not co_bang:
            if i in phu_luc:
                pass          # tiêu đề phụ lục đã in ở trên
            vx = van_xuoi_trang(trang)
            if vx:
                ra += [""] + vx + [""]
            continue

        moc = vi_tri_tieu_de_bang(trang)
        da_co_truoc = ""
        gc_tat_ca = ghi_chu_cua_trang(trang)
        truoc = [t for v, t in gc_tat_ca if moc is not None and v < moc]
        sau = [t for v, t in gc_tat_ca if moc is None or v > moc]
        if truoc:
            ra += ["", "**Ghi chú:**", ""] + truoc + [""]
            da_co_truoc = " ".join(truoc)

        for so, ten in ten_bang.get(i, []):
            hien = so
            td = tieu_de_luoi(trang, a.so_cot)
            ra += ["", f"## Bảng {so} {ten}", ""]
            if td:
                ra += [hang_markdown(td), hang_markdown(["---"] * len(td))]

        hang_da_ghi: list[str] = []
        for h in doc_trang(trang, a.so_cot):
            ra.append(hang_markdown(h))
            hang_da_ghi += h

        # Ghi chú có thể vừa nằm trong ô bảng vừa in lại ngoài bảng; giữ cả
        # hai là lặp nội dung, nên bỏ bản đã có trong lưới.
        da_co = " ".join(hang_da_ghi) + da_co_truoc
        gc = [d for d in sau if d[:40] not in da_co]
        if gc:
            ra += ["", "**Ghi chú:**", ""] + gc + [""]

        if hien:
            dem_trang[hien] += 1
            if a.anh:
                a.anh.mkdir(parents=True, exist_ok=True)
                slug = hien.replace(".", "-")
                n = dem_trang[hien]
                ten_tep = (f"{a.tien_to}-{slug}.png" if n == 1
                           else f"{a.tien_to}-{slug}-tiep-{n - 1}.png")
                trang.get_pixmap(dpi=DPI_ANH,
                                 colorspace=pymupdf.csGRAY).save(a.anh / ten_tep)

    _nuot.__exit__(None, None, None)
    print("\n".join(ra))
    for so, n in sorted(dem_trang.items()):
        print(f"  Bảng {so}: {n} trang", file=sys.stderr)


if __name__ == "__main__":
    main()
