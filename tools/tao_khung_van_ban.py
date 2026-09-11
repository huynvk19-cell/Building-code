#!/usr/bin/env python3
"""Tạo KHUNG RỖNG cho một văn bản mà kho chưa có nội dung.

Vì sao cần: kho liên tục gặp các văn bản được viện dẫn nhưng chưa có bản gốc.
Trước đây chúng chỉ tồn tại dưới dạng một dòng ghi chú trong CLAUDE.md, nên khi
tra cứu thì không có gì hiện ra và rất dễ tưởng là "pháp luật không quy định".

Khung rỗng giải quyết việc đó: tra "105/2025" sẽ trả về một chunk nói thẳng
**văn bản này chưa có trong kho, đây là những gì đã biết về nó, cần bổ sung**.

Khung rỗng **không bao giờ được dùng làm căn cứ trả lời** — nó không có nội
dung. Trường `trang_thai: "KHUNG RỖNG"` là tín hiệu để search.py cảnh báo.

Chạy:  python3 tools/tao_khung_van_ban.py --tu-bang <tệp .tsv>
       (mỗi dòng: so_hieu <TAB> ngay_ban_hanh <TAB> tiêu đề <TAB> ghi chú)
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus" / "nghi-dinh"


def slug(s: str) -> str:
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def tao(so_hieu: str, ngay: str, tieu_de: str, ghi_chu: str,
        hieu_luc_tham_khao: str = "", nguon_tham_khao: str = "") -> Path:
    doc_id = slug(so_hieu)
    d = CORPUS / doc_id
    d.mkdir(parents=True, exist_ok=True)
    fm = [
        "---",
        f'doc_id: "{doc_id}"',
        f'so_hieu: "{so_hieu}"',
        'loai_van_ban: "Nghị định"',
        'co_quan_ban_hanh: "Chính phủ"',
        f'ngay_ban_hanh: "{ngay}"',
        f'tieu_de: "{tieu_de}"',
        'ngay_hieu_luc: "CHƯA XÁC ĐỊNH"',
        'can_cu_hieu_luc: "Kho chưa có bản gốc của văn bản này nên không đọc được điều khoản hiệu lực."',
    ]
    if hieu_luc_tham_khao:
        fm += [
            f'ngay_hieu_luc_theo_tham_khao: "{hieu_luc_tham_khao}"',
            f'nguon_ngay_hieu_luc_tham_khao: "{nguon_tham_khao}"',
        ]
    fm += [
        'thay_the: []',
        'het_hieu_luc: ""',
        'sua_doi_boi: []',
        'dieu_khoan_chuyen_tiep: ""',
        'nguon: "CHƯA CÓ — cần người dùng cung cấp bản gốc"',
        'phuong_phap_so_hoa: "chưa số hóa"',
        'trang_thai: "KHUNG RỖNG"',
        'ngon_ngu: "vi"',
        'cau_truc: "dieu"',
        "---",
        "",
        f"# {so_hieu} — KHUNG RỖNG, CHƯA CÓ NỘI DUNG",
        "",
        "> **CẢNH BÁO.** Đây **không phải** nội dung văn bản. Kho mới chỉ có tên,",
        "> số hiệu và ngày ban hành của nó, chưa có một điều khoản nào.",
        ">",
        "> **Tuyệt đối không trích khung rỗng này làm căn cứ trả lời.** Khi câu hỏi",
        "> rơi vào phạm vi văn bản này, phải nói thẳng với người dùng rằng *kho chưa",
        "> có nội dung của văn bản này* và đề nghị họ cung cấp bản gốc.",
        "",
        f"**Tên đầy đủ:** {tieu_de}",
        "",
        f"**Ngày ban hành:** {ngay}",
        "",
    ]
    if hieu_luc_tham_khao:
        fm += [
            f"**Ngày hiệu lực theo tài liệu tham khảo:** {hieu_luc_tham_khao} — "
            f"nguồn: {nguon_tham_khao}. Đây là thông tin từ tài liệu tham khảo, "
            "**chưa được coi là đã chứng minh**.",
            "",
        ]
    fm += ["## Vì sao kho cần văn bản này", "", ghi_chu, ""]
    (d / "toan-van.md").write_text("\n".join(fm), encoding="utf-8")
    return d / "toan-van.md"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tu-bang", type=Path, required=True,
                    help="tệp TSV: so_hieu, ngay_ban_hanh, tiêu đề, ghi chú, "
                         "[hiệu lực tham khảo], [nguồn tham khảo]")
    args = ap.parse_args()
    if not args.tu_bang.exists():
        sys.exit(f"Không thấy tệp: {args.tu_bang}")
    n = 0
    for dong in args.tu_bang.read_text(encoding="utf-8").splitlines():
        if not dong.strip() or dong.lstrip().startswith("#"):
            continue
        cot = dong.split("\t")
        if len(cot) < 4:
            sys.exit(f"Dòng thiếu cột: {dong[:60]}")
        p = tao(*[c.strip() for c in cot[:4]],
                *[c.strip() for c in cot[4:6]])
        print(f"  + {p.relative_to(ROOT)}")
        n += 1
    print(f"\nĐã tạo {n} khung rỗng.")


if __name__ == "__main__":
    main()
