#!/usr/bin/env python3
"""Đo chất lượng truy hồi trên bộ câu hỏi có nhãn vàng.

Chỉ đo TẦNG TRUY HỒI, không đo chất lượng câu trả lời của LLM. Lý do: nếu chunk
đúng không lọt vào top-K thì LLM không có cách nào trả lời đúng — truy hồi là
trần trên của toàn hệ thống.

Hai nhóm câu hỏi được chấm khác nhau:

  * Câu CÓ nhãn vàng  -> Recall@K, MRR.
  * Câu KHÔNG có đáp án trong corpus (`vang` rỗng, loại N và một phần loại I)
    -> đo khả năng TỪ CHỐI: hệ thống có nhận ra mình không đủ căn cứ không.
    Đây là chỉ số an toàn quan trọng nhất với văn bản pháp luật, vì một câu trả
    lời tự tin cho câu hỏi ngoài phạm vi corpus nguy hiểm hơn là không trả lời.

    python3 eval/chay_danh_gia.py            # cấu hình hiện hành
    python3 eval/chay_danh_gia.py --so-sanh  # đối chiếu với tokenizer cũ
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("s", ROOT / "tools/search.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

K_LIST = [1, 3, 5, 10]


def nap_cau_hoi() -> list[dict]:
    with (ROOT / "eval/bo_cau_hoi.jsonl").open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def kiem_chung_nhan_vang(cau_hoi: list[dict], recs: list[dict]) -> int:
    """Nhãn vàng phải thực sự chứa chuỗi kiểm chứng — chặn việc bịa nhãn."""
    theo_id = {r["chunk_id"]: r for r in recs}
    loi = 0
    for q in cau_hoi:
        for g in q["vang"]:
            if g not in theo_id:
                print(f"  LỖI {q['id']}: chunk không tồn tại — {g}")
                loi += 1
        if q["vang"] and not any(
            q["kiem_chung"].lower() in theo_id[g]["text"].lower()
            for g in q["vang"] if g in theo_id
        ):
            print(f"  LỖI {q['id']}: nhãn vàng không chứa {q['kiem_chung']!r}")
            loi += 1
    return loi


def do(ten: str, tokfn, truong, dung_boost: bool) -> dict:
    recs = S.load_index(S.INDEX_PATH)
    cau_hoi = nap_cau_hoi()
    if kiem_chung_nhan_vang(cau_hoi, recs):
        sys.exit("Nhãn vàng không hợp lệ — dừng để tránh đo trên dữ liệu sai.")

    docs, avg, idf = S.build_bm25(recs, False, tokfn=tokfn, truong=truong)

    co_nhan = [q for q in cau_hoi if q["vang"]]
    khong_dap_an = [q for q in cau_hoi if not q["vang"]]

    tong = {k: 0.0 for k in K_LIST}
    mrr = 0.0
    theo_loai: dict[str, list] = defaultdict(lambda: [0, 0.0])
    truot = []

    for q in co_nhan:
        xh = S.xep_hang(q["hoi"], recs, docs, avg, idf, tokfn, dung_boost)
        ids = [r["chunk_id"] for _, r in xh]
        vang = set(q["vang"])
        for k in K_LIST:
            tong[k] += len(vang & set(ids[:k])) / len(vang)
        vt = next((i + 1 for i, c in enumerate(ids) if c in vang), None)
        mrr += 1 / vt if vt else 0.0
        theo_loai[q["loai"]][0] += 1
        theo_loai[q["loai"]][1] += len(vang & set(ids[:5])) / len(vang)
        if len(vang & set(ids[:5])) < len(vang):
            truot.append((q["id"], q["loai"], q["hoi"][:44], sorted(vang - set(ids[:5]))))

    # Câu ngoài phạm vi corpus. Không chấm đúng/sai bằng ngưỡng điểm, vì đã đo
    # được rằng điểm BM25 không tách được hai nhóm (xem chú thích trong
    # tools/search.py). Chỉ ghi lại dải điểm để theo dõi mức chồng lấn.
    diem_cao_nhat = []
    for q in khong_dap_an:
        xh = S.xep_hang(q["hoi"], recs, docs, avg, idf, tokfn, dung_boost)
        diem_cao_nhat.append((q["id"], round(xh[0][0] if xh else 0.0, 2)))

    n = len(co_nhan)
    print(f"\n═══ {ten} ═══")
    print(f"  Câu có nhãn vàng: {n} | câu ngoài phạm vi corpus: {len(khong_dap_an)}")
    for k in K_LIST:
        print(f"  Recall@{k:<2} = {tong[k]/n:.3f}")
    print(f"  MRR      = {mrr/n:.3f}")
    d_ngoai = [d for _, d in diem_cao_nhat]
    d_trong = []
    for q in co_nhan:
        xh = S.xep_hang(q["hoi"], recs, docs, avg, idf, tokfn, dung_boost)
        d_trong.append(xh[0][0] if xh else 0.0)
    print(f"  Điểm top-1 câu NGOÀI phạm vi: {min(d_ngoai):.1f}–{max(d_ngoai):.1f}"
          f" | câu CÓ đáp án: {min(d_trong):.1f}–{max(d_trong):.1f}"
          f"  → {'CHỒNG LẤN, không dùng ngưỡng được' if min(d_trong) < max(d_ngoai) else 'tách được'}")
    print("  Recall@5 theo loại: " + "  ".join(
        f"{l}={v[1]/v[0]:.2f}({v[0]})" for l, v in sorted(theo_loai.items())))
    return {"r": {k: tong[k]/n for k in K_LIST}, "mrr": mrr/n,
            "tu_choi": (0, len(khong_dap_an)),
            "truot": truot, "diem_ngoai_pham_vi": diem_cao_nhat}


def main() -> None:
    ap = argparse.ArgumentParser(description="Đo chất lượng truy hồi.")
    ap.add_argument("--so-sanh", action="store_true",
                    help="Đối chiếu cấu hình hiện hành với tokenizer cũ")
    ap.add_argument("--chi-tiet", action="store_true", help="In các câu còn trượt")
    args = ap.parse_args()

    moi = do("CẤU HÌNH HIỆN HÀNH", S.tokenize, S.truong_lap_chi_muc, True)

    if args.so_sanh:
        cu = do("ĐỐI CHỨNG — tokenizer cũ, không boost",
                S.tokenize_cu, lambda r: f"{r['tieu_de']} {r['text']}", False)
        print("\n═══ CHÊNH LỆCH (hiện hành − đối chứng) ═══")
        for k in K_LIST:
            d = moi["r"][k] - cu["r"][k]
            print(f"  Recall@{k:<2} {cu['r'][k]:.3f} → {moi['r'][k]:.3f}   {d:+.3f}")
        print(f"  MRR      {cu['mrr']:.3f} → {moi['mrr']:.3f}   {moi['mrr']-cu['mrr']:+.3f}")


    if args.chi_tiet:
        print(f"\n  ── {len(moi['truot'])} câu chưa lấy đủ nhãn vàng trong top-5 ──")
        for t in moi["truot"]:
            print(f"    {t[0]} [{t[1]}] {t[2]:46} thiếu={t[3]}")
        print("\n  ── điểm cao nhất ở câu ngoài phạm vi corpus ──")
        for i, d in sorted(moi["diem_ngoai_pham_vi"], key=lambda x: -x[1]):
            print(f"    {i}: {d:6.2f}")


if __name__ == "__main__":
    main()
