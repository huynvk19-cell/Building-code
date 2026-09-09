#!/usr/bin/env python3
"""Đo chất lượng truy hồi trên bộ câu hỏi có nhãn vàng.

Chỉ đo TẦNG TRUY HỒI (retrieval), không đo chất lượng câu trả lời của LLM.
Lý do: nếu chunk đúng không lọt vào top-K thì LLM không có cách nào trả lời
đúng — retrieval là trần trên của toàn hệ thống.
"""
import json, sys, importlib.util
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("s", ROOT / "tools/search.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)

def xep_hang(recs, docs, avg, idf, cau, khong_dau=False):
    qt = S.tokenize(cau, khong_dau)
    diem = [(S.score(qt, d, avg, idf), r) for d, r in zip(docs, recs)]
    diem.sort(key=lambda x: x[0], reverse=True)
    return [r["chunk_id"] for s, r in diem if s > 0]

def do(bien_the="baseline", khong_dau=False):
    recs = S.load_index(ROOT / "index/chunks.jsonl")
    docs, avg, idf = S.build_bm25(recs, khong_dau)
    qs = [json.loads(l) for l in open(ROOT / "eval/bo_cau_hoi.jsonl", encoding="utf-8")]
    K = [1, 3, 5, 10]
    tong = {k: 0.0 for k in K}; mrr = 0.0
    theo_loai = defaultdict(lambda: {"n": 0, "r5": 0.0})
    truot = []
    for q in qs:
        xh = xep_hang(recs, docs, avg, idf, q["hoi"], khong_dau)
        vang = set(q["vang"])
        for k in K:
            tong[k] += len(vang & set(xh[:k])) / len(vang)   # recall theo tỉ lệ nhãn vàng tìm được
        vt = next((i + 1 for i, c in enumerate(xh) if c in vang), None)
        mrr += 1 / vt if vt else 0
        theo_loai[q["loai"]]["n"] += 1
        theo_loai[q["loai"]]["r5"] += len(vang & set(xh[:5])) / len(vang)
        if len(vang & set(xh[:5])) < len(vang):
            truot.append((q["id"], q["loai"], q["hoi"][:44],
                          sorted(vang - set(xh[:5])), xh[0] if xh else "—"))
    n = len(qs)
    print(f"\n═══ {bien_the}  (n={n}) ═══")
    for k in K: print(f"  Recall@{k:<2} = {tong[k]/n:.3f}")
    print(f"  MRR      = {mrr/n:.3f}")
    print("  Recall@5 theo loại:", "  ".join(
        f"{l}={v['r5']/v['n']:.2f}({v['n']})" for l, v in sorted(theo_loai.items())))
    return tong[5]/n, truot

if __name__ == "__main__":
    r5, truot = do("BASELINE — BM25 hiện tại (K1=1.5, B=0.5)")
    print(f"\n  ── {len(truot)} câu chưa lấy đủ nhãn vàng trong top-5 ──")
    for t in truot: print(f"    {t[0]} [{t[1]}] {t[2]:46} thiếu={t[3]}  top1={t[4][:40]}")
