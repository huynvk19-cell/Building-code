#!/usr/bin/env python3
"""Cắt ảnh các BẢNG TRA từ bản PDF gốc vào corpus.

Vì sao cần: kho chép nội dung bảng thành Markdown để tìm kiếm được, nhưng người
dùng là kiến trúc sư và cần nhìn đúng bản in khi lập hồ sơ. Bản PDF gốc nằm ở
thư mục tải lên của phiên làm việc và sẽ biến mất, nên ảnh phải được cắt vào
corpus và đưa vào git.

Cách định vị: dùng Tesseract lấy toạ độ DÒNG chữ, tìm dòng bắt đầu bằng
"Bảng <số hiệu>", rồi cắt từ dòng đó xuống tới ngay trước tiêu đề "Bảng" kế
tiếp (hoặc tới đáy vùng chữ của trang). OCR ở đây CHỈ dùng để định vị, không
bao giờ dùng làm nội dung — Tesseract đánh rơi dấu tiếng Việt.

Dùng:
    python3 tools/cat_bang.py --pdf <file.pdf> --tu-trang 56 --den-trang 65 \
        --dich corpus/quy-chuan/qcvn-06-2022-bxd/phu-luc/bang --tien-to bang-g
    python3 tools/cat_bang.py --pdf <file.pdf> --trang 57 --bang G.2a \
        --y0 82 --y1 395 --dich <thu-muc>     # cắt tay khi cần chỉnh
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import pymupdf

# Lề trái/phải của khổ A4 trong các quy chuẩn này. Lấy trọn bề ngang để không
# mất phần chú thích nằm bên phải bảng.
X0, X1 = 32, 566
DPI_CAT = 200      # độ phân giải ảnh XUẤT RA — cần nét để đọc số trong bảng
# Độ phân giải đưa vào Tesseract chỉ để DÒ vị trí dòng tiêu đề, không cần nét.
# Đo trên máy rảnh: 110 dpi mất 1,4 s/trang, 200 dpi mất 1,8 s/trang, kết quả dò
# như nhau. Toạ độ vẫn quy về ĐIỂM nên độ chính xác khung cắt không đổi.
DPI_OCR = 110

# Tiêu đề bảng thật có dạng "Bảng G.2a – Khoảng cách…" (có dấu gạch nối rồi tới
# tên), hoặc "Bảng G.2b (tiếp theo)" / "(kết thúc)" ở trang nối tiếp. Nếu chỉ dò
# "Bảng <số>" thì mọi câu viện dẫn kiểu "quy định tại Bảng G.1." cũng bị nhận
# nhầm là tiêu đề — đã gặp thật khi chạy trên Phụ lục G.
RE_TIEU_DE_BANG = re.compile(
    r"^B[aả]ng\s+([A-Z]?\.?\d+[a-z]?)\s*(?:[-–—]\s*(?P<ten>\S.*)"
    r"|\((?P<noi>ti[eế]p theo|k[eế]t th[uú]c)\))"
)


def khong_dau(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def slugify(s: str, gioi_han: int = 60) -> str:
    s = khong_dau(s).lower().replace("đ", "d")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:gioi_han].rstrip("-")


def doc_dong(pdf: Path, so_trang: int) -> list[tuple[float, float, str]]:
    """Trả về [(y_trên, y_dưới, nội dung dòng)] theo ĐƠN VỊ ĐIỂM của trang PDF."""
    doc = pymupdf.open(pdf)
    trang = doc[so_trang - 1]
    png = trang.get_pixmap(dpi=DPI_OCR).tobytes("png")
    ket_qua = subprocess.run(
        ["tesseract", "stdin", "stdout", "-l", "vie", "tsv"],
        input=png, capture_output=True, check=True,
    ).stdout.decode("utf-8", "replace")

    ty_le = 72 / DPI_OCR
    dong: dict[tuple, list] = {}
    for hang in ket_qua.splitlines()[1:]:
        o = hang.split("\t")
        if len(o) < 12 or o[11].strip() in ("", "-1"):
            continue
        khoa = (o[1], o[2], o[3], o[4])          # page/block/par/line
        top, chieu_cao = float(o[7]), float(o[9])
        muc = dong.setdefault(khoa, [top, top + chieu_cao, []])
        muc[0] = min(muc[0], top)
        muc[1] = max(muc[1], top + chieu_cao)
        muc[2].append(o[11])
    return [
        (v[0] * ty_le, v[1] * ty_le, " ".join(v[2]).strip())
        for v in sorted(dong.values(), key=lambda v: v[0])
    ]


def tim_bang(pdf: Path, tu_trang: int, den_trang: int) -> list[dict]:
    """Quét dải trang, trả về danh sách bảng kèm khung cắt gợi ý."""
    ra: list[dict] = []
    for trang in range(tu_trang, den_trang + 1):
        cac_dong = doc_dong(pdf, trang)
        moc = [
            (i, RE_TIEU_DE_BANG.match(nd))
            for i, (_, _, nd) in enumerate(cac_dong)
            if RE_TIEU_DE_BANG.match(nd)
        ]
        print(f"  … quét trang {trang}", file=sys.stderr, flush=True)
        for thu_tu, (i, m) in enumerate(moc):
            y0 = max(cac_dong[i][0] - 8, 20)
            if thu_tu + 1 < len(moc):
                y1 = cac_dong[moc[thu_tu + 1][0]][0] - 6
            else:
                # tới đáy vùng chữ, bỏ số trang ở chân
                duoi = [d[1] for d in cac_dong[i:] if d[1] < 800]
                y1 = (max(duoi) if duoi else 780) + 10
            ra.append(
                {
                    "trang": trang,
                    "bang": m.group(1),
                    "noi_tiep": bool(m.group("noi")),
                    "tieu_de": cac_dong[i][2],
                    "y0": round(y0, 1),
                    "y1": round(min(y1, 812), 1),
                }
            )
    return ra


def cat(pdf: Path, trang: int, y0: float, y1: float, dich: Path) -> Path:
    """Cắt một khung và lưu PNG THANG XÁM.

    Bản gốc là ảnh quét đen trắng nên màu không mang thông tin gì; lưu thang xám
    giảm dung lượng khoảng ba lần mà chữ và số trong bảng vẫn nét như cũ. Với
    122 ảnh thì đây là khác biệt giữa một kho 130 MB và một kho khoảng 45 MB.
    """
    doc = pymupdf.open(pdf)
    khung = pymupdf.Rect(X0, y0, X1, y1)
    dich.parent.mkdir(parents=True, exist_ok=True)
    doc[trang - 1].get_pixmap(
        dpi=DPI_CAT, clip=khung, colorspace=pymupdf.csGRAY
    ).save(dich)
    return dich


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pdf", required=True, type=Path)
    p.add_argument("--dich", required=True, type=Path, help="thư mục chứa ảnh")
    p.add_argument("--tu-trang", type=int)
    p.add_argument("--den-trang", type=int)
    p.add_argument("--trang", type=int, help="cắt tay một trang")
    p.add_argument("--bang", help="số hiệu bảng khi cắt tay, ví dụ G.2a")
    p.add_argument("--y0", type=float)
    p.add_argument("--y1", type=float)
    p.add_argument("--tien-to", default="bang", help="tiền tố tên tệp")
    p.add_argument("--chi-liet-ke", action="store_true",
                   help="chỉ in danh sách bảng tìm được, không cắt")
    a = p.parse_args()

    if a.trang and a.bang:
        if a.y0 is None or a.y1 is None:
            sys.exit("Cắt tay cần cả --y0 và --y1.")
        ten = f"{a.tien_to}-{slugify(a.bang)}.png"
        print("đã cắt:", cat(a.pdf, a.trang, a.y0, a.y1, a.dich / ten))
        return

    if not (a.tu_trang and a.den_trang):
        sys.exit("Cần --tu-trang và --den-trang, hoặc --trang kèm --bang.")

    ds = tim_bang(a.pdf, a.tu_trang, a.den_trang)
    for b in ds:
        print(f"trang {b['trang']:>3}  Bảng {b['bang']:<8} "
              f"y {b['y0']:>6.1f} → {b['y1']:>6.1f}  | {b['tieu_de'][:70]}")
    if a.chi_liet_ke:
        return
    dem_noi: dict[str, int] = {}
    for b in ds:
        goc = slugify(b["bang"])
        if b["noi_tiep"]:
            dem_noi[goc] = dem_noi.get(goc, 0) + 1
            ten = f"{a.tien_to}-{goc}-tiep-{dem_noi[goc]}.png"
        else:
            ten = f"{a.tien_to}-{goc}.png"
        cat(a.pdf, b["trang"], b["y0"], b["y1"], a.dich / ten)
    print(f"\nĐã cắt {len(ds)} ảnh vào {a.dich}")


if __name__ == "__main__":
    main()
