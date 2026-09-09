#!/usr/bin/env python3
"""
Cắt một hình vẽ ra khỏi file PDF gốc, lưu vào thư mục hình của văn bản.

Dùng khi số hóa văn bản có hình vẽ, sơ đồ, biểu đồ. Chép chú dẫn thành chữ là
đủ để tìm kiếm, nhưng bản thân hình vẽ vẫn cần giữ lại để người đọc nhìn được —
nhất là với quy chuẩn xây dựng, nơi hình học của bản vẽ mang thông tin mà lời
văn không diễn đạt hết.

    # Bước 1: xem trang để ước lượng vùng cắt (in ra lưới toạ độ)
    python3 tools/cat_hinh.py vanban.pdf --trang 52 --xem

    # Bước 2: cắt (toạ độ tính bằng điểm - point, gốc ở góc trên bên trái)
    python3 tools/cat_hinh.py vanban.pdf --trang 52 \
        --vung 72,62,540,268 \
        --ra corpus/quy-chuan/qcvn-10-2025-bca/phu-luc/hinh/hinh-h-01.png

Cắt thẳng từ PDF chứ không cắt từ ảnh trang đã render, nên nét vẽ giữ nguyên độ
sắc ở bất kỳ dpi nào.

Sau khi cắt, chèn link vào file Markdown trong corpus/ theo đường dẫn tương đối
so với chính file đó, kèm mô tả thay thế (alt text) nói rõ hình thể hiện gì:

    ![Hình H.1 - Mặt cắt bến lấy nước, thể hiện trụ chống trôi xe và rào chắn](hinh/hinh-h-01.png)

Mô tả này quan trọng: công cụ tìm kiếm chỉ đọc được chữ, nên nếu không có nó thì
hình vẽ coi như vô hình với người tra cứu. `tools/build_index.py` sẽ tự sửa lại
đường dẫn tương đối khi sinh file chunk, không cần chỉnh tay.

Yêu cầu: pip install pymupdf
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Cắt hình vẽ từ PDF gốc.")
    parser.add_argument("pdf", type=Path, help="File PDF nguồn")
    parser.add_argument(
        "--trang", type=int, required=True, help="Số trang (đếm từ 1)"
    )
    parser.add_argument(
        "--vung",
        help="Vùng cắt 'trái,trên,phải,dưới' tính bằng point. Bỏ qua thì cắt cả trang.",
    )
    parser.add_argument("--ra", type=Path, help="File PNG đầu ra")
    parser.add_argument("--dpi", type=int, default=300, help="Độ phân giải (mặc định 300)")
    parser.add_argument(
        "--xem",
        action="store_true",
        help="Chỉ in kích thước trang và gợi ý vùng cắt, không xuất file",
    )
    args = parser.parse_args()

    try:
        import pymupdf
    except ImportError:
        sys.exit("Thiếu pymupdf. Cài bằng: pip install pymupdf")

    if not args.pdf.exists():
        sys.exit(f"Không tìm thấy file: {args.pdf}")

    doc = pymupdf.open(args.pdf)
    if not 1 <= args.trang <= len(doc):
        sys.exit(f"Trang {args.trang} nằm ngoài khoảng 1-{len(doc)}.")
    page = doc[args.trang - 1]
    rong, cao = page.rect.width, page.rect.height

    if args.xem:
        print(f"Trang {args.trang}: rộng {rong:.0f} pt, cao {cao:.0f} pt\n")
        print("Lưới tham chiếu để ước lượng vùng cắt:")
        for ten, chieu, tong in (("ngang", "trái→phải", rong), ("dọc", "trên→dưới", cao)):
            moc = "  ".join(f"{p}%={tong * p / 100:.0f}" for p in (0, 25, 50, 75, 100))
            print(f"  {ten:6} ({chieu:11}): {moc}")
        print(
            "\nVí dụ: hình nằm ở nửa trên trang, chừa lề hai bên"
            f"\n  --vung {rong * 0.12:.0f},{cao * 0.07:.0f},{rong * 0.91:.0f},{cao * 0.32:.0f}"
        )
        return

    if not args.ra:
        sys.exit("Thiếu --ra (đường dẫn file PNG đầu ra).")

    clip = None
    if args.vung:
        try:
            so = [float(v) for v in args.vung.split(",")]
        except ValueError:
            sys.exit("--vung phải là 4 số cách nhau bởi dấu phẩy.")
        if len(so) != 4:
            sys.exit("--vung cần đúng 4 số: trái,trên,phải,dưới")
        clip = pymupdf.Rect(*so)
        if not clip.intersects(page.rect):
            sys.exit(f"Vùng cắt nằm ngoài trang (trang rộng {rong:.0f} x cao {cao:.0f} pt).")

    args.ra.parent.mkdir(parents=True, exist_ok=True)
    pix = page.get_pixmap(dpi=args.dpi, clip=clip)
    pix.save(args.ra)
    print(f"Đã lưu {args.ra} ({pix.width}x{pix.height} px, {args.ra.stat().st_size // 1024} KB)")
    print(
        "\nBước tiếp theo: chèn vào file Markdown trong corpus/ với đường dẫn tương đối"
        "\nvà mô tả thay thế nói rõ hình thể hiện gì, rồi chạy tools/build_index.py"
    )


if __name__ == "__main__":
    main()
