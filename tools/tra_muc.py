#!/usr/bin/env python3
"""Tra một điều khoản kèm TOÀN BỘ ngữ cảnh của nó — nhất là PHẠM VI.

Vì sao cần công cụ này (lỗi có thật, đã mắc):

    Người dùng hỏi kích thước lối đi thoát nạn. Tôi chạy
        grep -n 'thông thủy' corpus/.../qcvn-10-2024-bxd/toan-van.md
    và nhận về đúng một dòng:
        **2.7.4** Các chướng ngại vật đứng độc lập ... độ nhô ra tối đa 100 mm
    rồi trích nó cạnh mục 3.3.5 QCVN 06:2022/BXD như hai quy định song song.

    Thực tế điều khoản đó nằm trong mục 2.7 "ĐƯỜNG VÀ HÈ PHỐ" — quy định cho
    vỉa hè NGOÀI NHÀ, cho người khiếm thị, không liên quan thoát nạn.

    Điều đáng nói: phạm vi ấy CÓ SẴN trong chỉ mục (chunk chứa 2.7.4 mang
    tiêu đề "Đường và hè phố"). grep trên file phẳng đã cắt mất tiêu đề đó.

Kết luận rút ra: `grep` chỉ dùng để ĐỊNH VỊ, không bao giờ dùng để KẾT LUẬN.
Định vị xong thì chạy công cụ này để đọc điều khoản kèm phạm vi.

Chạy:
    python3 tools/tra_muc.py 2.7.4
    python3 tools/tra_muc.py 3.3.6 --doc qcvn-06-2022-bxd
    python3 tools/tra_muc.py G.9
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index"

# Dấu hiệu trong TIÊU ĐỀ mục cho biết điều khoản điều chỉnh không gian nào.
# Chỉ nêu ra để người đọc tự xét — KHÔNG tự kết luận thay.
DAU_HIEU_NGOAI_NHA = (
    "đường và hè phố", "hè phố", "bãi đỗ xe", "điểm dừng", "ngoài nhà",
    "đường cho xe chữa cháy", "khoảng cách phòng cháy", "hạ tầng",
)
DAU_HIEU_TRONG_NHA = (
    "thoát nạn", "hành lang", "buồng thang", "cầu thang", "gian phòng",
    "trong nhà", "trong công trình", "cửa", "thang máy",
)


def nap() -> list[dict]:
    return [json.loads(l) for l in (INDEX / "chunks.jsonl").open(encoding="utf-8")]


def tim(recs: list[dict], so: str, doc: str | None) -> list[dict]:
    """Chunk mang đúng số hiệu, hoặc chunk có chứa điều khoản con đó."""
    so_chuan = so.strip().upper().replace("BẢNG", "").strip()
    ra = []
    for r in recs:
        if doc and r["doc_id"] != doc:
            continue
        shm = (r.get("so_hieu_muc") or "").upper()
        if shm == so_chuan:
            ra.append((0, r))
            continue
        # "**2.7.4**" hoặc "### 2.7.4" hoặc "Bảng G.9" nằm trong thân chunk
        mau = re.escape(so_chuan)
        if re.search(rf"(?:^|\*\*|#\s|\n)\s*{mau}(?:\*\*|\s|$|\.)", r["text"], re.M | re.I):
            ra.append((1, r))
        elif so_chuan.startswith(tuple("ABCDEFGHI")) and re.search(
            rf"B[aả]ng\s+{mau}\b", r["text"], re.I
        ):
            ra.append((1, r))
    ra.sort(key=lambda x: x[0])
    return [r for _, r in ra]


def nhan_pham_vi(tieu_de: str) -> str:
    t = (tieu_de or "").lower()
    ngoai = [d for d in DAU_HIEU_NGOAI_NHA if d in t]
    trong = [d for d in DAU_HIEU_TRONG_NHA if d in t]
    if ngoai and not trong:
        return f"có dấu hiệu NGOÀI NHÀ (tiêu đề chứa: {', '.join(ngoai)})"
    if trong and not ngoai:
        return f"có dấu hiệu TRONG NHÀ (tiêu đề chứa: {', '.join(trong)})"
    if ngoai and trong:
        return "MẬP MỜ — tiêu đề mang dấu hiệu của cả hai, phải đọc kỹ"
    return "không suy được từ tiêu đề — PHẢI TỰ ĐỌC"


def in_ra(r: dict, so: str, day_du: bool) -> None:
    print("═" * 78)
    print(f"  TRÍCH DẪN : {r['trich_dan']}")
    print(f"  Văn bản   : {r['so_hieu']}")
    print(f"  PHẠM VI   : {r['tieu_de']}")
    print(f"              → {nhan_pham_vi(r['tieu_de'])}")
    if r.get("chuong"):
        print(f"  Mục cấp trên: {r['chuong']}")
    if r.get("muc"):
        print(f"  Mục cha   : {r['muc']}")
    print(f"  Hiệu lực  : {r.get('ngay_hieu_luc') or 'CHƯA XÁC ĐỊNH'}")
    if r.get("gia_tri_phap_ly"):
        print(f"  🛑 {r['gia_tri_phap_ly']} — KHÔNG dùng làm căn cứ pháp lý")
    for sd in r.get("sua_doi_boi") or []:
        print(f"  ⚠️  ĐÃ BỊ SỬA ĐỔI bởi {sd['so_hieu']} (hiệu lực {sd['ngay_hieu_luc']})")
        print(f"      → {sd['duong_dan']}")
    anh = re.findall(r"!\[([^\]]*)\]\(([^)]+\.png)\)", r["text"])
    if anh:
        print(f"  Ảnh kèm   : {len(anh)} tệp — PHẢI GỬI ĐỦ CẢ CHUỖI")
        for alt, p in anh:
            print(f"      · {p}")
            print(f"        {alt}")
    print(f"  File      : {r['duong_dan']}")
    print("─" * 78)
    text = r["text"]
    if not day_du:
        # Cắt lấy đoạn quanh điều khoản được hỏi cho dễ đọc.
        m = re.search(rf"(?:\*\*)?{re.escape(so.upper())}(?:\*\*)?", text, re.I)
        if m and len(text) > 1400:
            a = max(0, m.start() - 200)
            text = ("…" if a else "") + text[a : m.start() + 1200] + "…"
    print(text)
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("so_hieu", help='số hiệu mục ("2.7.4", "3.3.6") hoặc bảng ("G.9")')
    ap.add_argument("--doc", help="khoanh một văn bản, ví dụ qcvn-06-2022-bxd")
    ap.add_argument("--day-du", action="store_true", help="in trọn chunk, không cắt")
    args = ap.parse_args()

    hits = tim(nap(), args.so_hieu, args.doc)
    if not hits:
        print(f'Không thấy điều khoản "{args.so_hieu}" trong kho.')
        print("Thử --doc để khoanh văn bản, hoặc dùng tools/search.py để tìm theo từ khoá.")
        return

    print(f'\n{len(hits)} chunk chứa "{args.so_hieu}". '
          f"ĐỌC PHẠM VI TRƯỚC KHI TRÍCH.\n")
    for r in hits[:5]:
        in_ra(r, args.so_hieu, args.day_du)
    if len(hits) > 5:
        print(f"(còn {len(hits) - 5} chunk nữa — dùng --doc để thu hẹp)")


if __name__ == "__main__":
    main()
