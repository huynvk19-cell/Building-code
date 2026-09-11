#!/usr/bin/env python3
"""Chèn liên kết ảnh bảng vào corpus, ngay dưới dòng tiêu đề của bảng đó.

Vì sao cần công cụ này: ảnh bảng được cắt hàng loạt vào `bang/`, nhưng việc
chèn liên kết vào Markdown trước đây làm tay nên bỏ sót — đã đo được 34 trên
121 ảnh chưa từng được chèn, trong đó có trọn bộ phụ lục QCVN 10:2025/BCA.
Ảnh không được chèn thì chunk trả về từ search.py không mang đường dẫn ảnh,
và người trả lời sẽ tưởng là kho không có ảnh.

Chạy:  python3 tools/chen_anh_bang.py            # xem trước, không sửa
       python3 tools/chen_anh_bang.py --ghi      # ghi vào corpus
"""
from __future__ import annotations

import argparse
import os
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"

# "**Bảng G.9 – Hệ số không gian sàn** ^1)^"  ·  "## Bảng B.1 - Quy định về..."
RE_TIEU_DE = re.compile(
    r"^(?:#{1,4}\s+|\*\*)B[aả]ng\s+([A-Z]?\.?\d+(?:\.\d+)?[a-zA-Z]?)\s*[-–—:]\s*(.+?)(?:\*\*)?\s*(?:\^\d\)\^)?\s*$"
)
RE_ANH = re.compile(r"^!\[.*\]\([^)]*bang/.*\.png\)\s*$")
RE_DUONG_DAN = re.compile(r"\(([^()]+\.png)\)\s*$")


def slug_bang(so: str) -> str:
    """'G.9' -> 'g-9' ; 'E.4a' -> 'e-4a' ; '11' -> '11'."""
    s = unicodedata.normalize("NFD", so).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def anh_cua_bang(thu_muc: Path, so: str) -> list[Path]:
    """Ảnh chính rồi tới các trang tiếp theo, theo đúng thứ tự."""
    base = f"bang-{slug_bang(so)}"
    chinh = thu_muc / f"{base}.png"
    if not chinh.exists():
        return []
    tiep = sorted(
        thu_muc.glob(f"{base}-tiep-*.png"),
        key=lambda p: int(re.search(r"-tiep-(\d+)", p.name).group(1)),
    )
    return [chinh] + tiep


def dong_anh(so: str, ten: str, duong_dan: Path, thu_tu: int, md: Path) -> str:
    ten = re.sub(r"\*\*|\^\d\)\^", "", ten).strip().rstrip("*").strip()
    hau_to = "" if thu_tu == 0 else f" (trang tiếp theo {thu_tu})"
    # Đường dẫn phải tương đối so với chính file Markdown đang sửa: bảng ở
    # toan-van.md nhưng ảnh nằm trong phu-luc/bang/ thì phải ghi đủ hai cấp.
    rel = os.path.relpath(duong_dan, md.parent).replace(os.sep, "/")
    return f"![Ảnh chụp Bảng {so} từ bản in gốc — {ten}{hau_to}]({rel})"


def xu_ly(md: Path, thu_muc_anh: Path, ghi: bool) -> int:
    dong = md.read_text(encoding="utf-8").splitlines()
    ra: list[str] = []
    them = 0
    i = 0
    while i < len(dong):
        ra.append(dong[i])
        m = RE_TIEU_DE.match(dong[i])
        if not m:
            i += 1
            continue
        so, ten = m.group(1), m.group(2)
        anh = anh_cua_bang(thu_muc_anh, so)
        if not anh:
            i += 1
            continue
        # Gom các dòng ảnh đã có ngay dưới tiêu đề (bỏ qua dòng trống xen kẽ).
        # KHÔNG được chỉ kiểm tra "có ảnh hay chưa": một bảng đã chèn ảnh
        # trang đầu nhưng thiếu các trang tiếp theo vẫn là thiếu — đây đúng là
        # lỗi đã gặp với Bảng B.1 QCVN 10:2025/BCA.
        j = i + 1
        da_co: list[str] = []
        while j < len(dong):
            if not dong[j].strip():
                j += 1
                continue
            if RE_ANH.match(dong[j]):
                # Phải neo vào CUỐI dòng: chú thích ảnh trang tiếp theo có
                # chứa "(trang tiếp theo 1)", lấy cặp ngoặc đầu tiên sẽ ra
                # nhầm chuỗi đó thay vì đường dẫn tệp.
                da_co.append(Path(RE_DUONG_DAN.search(dong[j]).group(1)).name)
                j += 1
                continue
            break
        thieu = [(k, x) for k, x in enumerate(anh) if x.name not in da_co]
        if not thieu:
            i += 1
            continue
        # Chèn trọn bộ ngay dưới tiêu đề, bỏ các dòng ảnh cũ để giữ đúng thứ tự.
        ra.append("")
        for k, x in enumerate(anh):
            ra.append(dong_anh(so, ten, x, k, md))
        them += len(thieu)
        i = j
    if them and ghi:
        md.write_text("\n".join(ra) + "\n", encoding="utf-8")
    return them


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ghi", action="store_true", help="ghi thật vào corpus")
    args = ap.parse_args()

    tong = 0
    for thu_muc_anh in sorted(CORPUS.rglob("bang")):
        if not thu_muc_anh.is_dir():
            continue
        goc = thu_muc_anh.parent
        # Bảng có thể được viết trong toan-van.md ở thư mục văn bản, trong khi
        # ảnh lại nằm ở phu-luc/bang/ — phải quét cả hai cấp.
        files = sorted(goc.glob("*.md"))
        if goc.name == "phu-luc":
            files += sorted(goc.parent.glob("*.md"))
        for md in files:
            n = xu_ly(md, thu_muc_anh, args.ghi)
            if n:
                print(f"  +{n:>3} ảnh  {md.relative_to(ROOT)}")
                tong += n
    print(f"\n{'Đã chèn' if args.ghi else 'Sẽ chèn'} {tong} liên kết ảnh.")
    if not args.ghi:
        print("Chạy lại với --ghi để ghi vào corpus.")


if __name__ == "__main__":
    main()
