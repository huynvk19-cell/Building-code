#!/usr/bin/env python3
"""
Bước 1 của quy trình số hóa: PDF → ảnh trang + bản OCR nháp.

    python3 tools/ingest_pdf.py duong-dan/vanban.pdf --ten 213-2026-nd-cp

Kết quả (mặc định ghi vào thư mục .ingest/, đã bị .gitignore bỏ qua):

    .ingest/<ten>/trang-001.png ...   ảnh từng trang, 300 dpi
    .ingest/<ten>/ocr-nhap.txt        bản OCR nháp, có mốc <<<TRANG n>>>

QUAN TRỌNG — OCR chỉ là BẢN NHÁP, không phải bản chính thức.
Tesseract tiếng Việt hay đánh rơi dấu ("thẩm quyền" → "thâm quyên",
"dữ liệu" → "đữ liệu"). Với văn bản pháp luật, sai một dấu là sai nghĩa.

Quy trình đầy đủ:

  1. Chạy script này để có ảnh trang + OCR nháp.
  2. Đưa ảnh từng trang cho Claude đọc (thị giác máy) và yêu cầu chép lại
     chính xác vào Markdown, dùng OCR nháp làm đối chiếu.
  3. Lưu kết quả vào corpus/<loai>/<ten>/toan-van.md kèm front matter
     (xem corpus/nghi-dinh/212-2026-nd-cp/toan-van.md làm mẫu).
  4. Chạy: python3 tools/build_index.py

Yêu cầu hệ thống:
    pip install pymupdf
    apt-get install tesseract-ocr tesseract-ocr-vie
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / ".ingest"


def check_deps() -> None:
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        sys.exit("Thiếu pymupdf. Cài bằng: pip install pymupdf")
    if not shutil.which("tesseract"):
        sys.exit(
            "Thiếu tesseract. Cài bằng: apt-get install tesseract-ocr tesseract-ocr-vie"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF → ảnh trang + OCR nháp.")
    parser.add_argument("pdf", type=Path, help="File PDF đầu vào")
    parser.add_argument("--ten", help="Tên thư mục kết quả (mặc định: tên file PDF)")
    parser.add_argument("--dpi", type=int, default=300, help="Độ phân giải (mặc định 300)")
    parser.add_argument("--lang", default="vie", help="Ngôn ngữ OCR (mặc định vie)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Thư mục gốc kết quả")
    parser.add_argument(
        "--bo-qua-ocr",
        action="store_true",
        help="Chỉ xuất ảnh, không chạy OCR (khi đã định chép tay bằng thị giác máy)",
    )
    args = parser.parse_args()

    check_deps()
    import pymupdf

    if not args.pdf.exists():
        sys.exit(f"Không tìm thấy file: {args.pdf}")

    name = args.ten or args.pdf.stem
    out_dir = args.out / name
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(args.pdf)
    print(f"{args.pdf.name}: {len(doc)} trang → {out_dir}")

    parts: list[str] = []
    for i, page in enumerate(doc, start=1):
        png = out_dir / f"trang-{i:03d}.png"
        if not png.exists():
            page.get_pixmap(dpi=args.dpi).save(png)

        if args.bo_qua_ocr:
            print(f"  trang {i:3d}: đã xuất ảnh")
            continue

        result = subprocess.run(
            ["tesseract", str(png), "stdout", "-l", args.lang, "--psm", "6"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  trang {i:3d}: OCR lỗi — {result.stderr.strip()[:120]}")
            continue
        parts.append(f"\n<<<TRANG {i}>>>\n{result.stdout}")
        print(f"  trang {i:3d}: {len(result.stdout):5d} ký tự")

    if not args.bo_qua_ocr:
        ocr_path = out_dir / "ocr-nhap.txt"
        ocr_path.write_text("".join(parts), encoding="utf-8")
        print(f"\nOCR nháp: {ocr_path}")

    print(
        "\nTiếp theo: đưa các file ảnh trang-*.png cho Claude đọc và chép lại"
        "\nthành Markdown chuẩn, rồi lưu vào corpus/. OCR nháp chỉ để đối chiếu."
    )


if __name__ == "__main__":
    main()
