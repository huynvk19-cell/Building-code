#!/usr/bin/env python3
"""
Tìm kiếm từ khóa (BM25) trên index/chunks.jsonl — không cần vector database.

    python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề hạng I"
    python3 tools/search.py --k 3 --full "nhà thầu nước ngoài thu hồi giấy phép"
    python3 tools/search.py --doc 212-2026-nd-cp --loai dieu "khảo sát địa chất"
    python3 tools/search.py --json "mã định danh quy hoạch"   # cho agent/script đọc

Vì sao BM25 mà không phải embedding? Văn bản pháp luật dùng thuật ngữ rất cố
định ("chứng chỉ hành nghề", "chủ nhiệm", "hạng II"), nên so khớp từ khóa đã
cho kết quả tốt mà không cần hạ tầng gì thêm. Khi kho tài liệu lớn lên tới
hàng trăm văn bản thì mới nên bổ sung tìm kiếm ngữ nghĩa.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index" / "chunks.jsonl"

K1 = 1.5   # tham số bão hòa tần suất từ của BM25
B = 0.75   # tham số chuẩn hóa theo độ dài văn bản

# Từ dừng: quá phổ biến trong văn bản pháp luật nên không giúp phân biệt.
STOPWORDS = {
    "và", "của", "các", "có", "được", "cho", "trong", "theo", "này", "tại",
    "với", "là", "khi", "hoặc", "về", "đối", "một", "những", "từ", "đến",
    "quy", "định", "thì", "để", "không", "phải", "sau", "trên", "như", "nếu",
    "do", "bằng", "còn", "đã", "sẽ", "mà", "nhưng", "vào", "ra", "ở", "cũng",
}


def strip_accents(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def tokenize(text: str, fold_accents: bool = False) -> list[str]:
    text = text.lower()
    if fold_accents:
        text = strip_accents(text)
    words = re.findall(r"[0-9a-zà-ỹ]+", text)
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def load_index(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(
            f"Chưa có chỉ mục: {path}\nHãy chạy trước: python3 tools/build_index.py"
        )
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_bm25(records: list[dict], fold_accents: bool) -> tuple[list[Counter], float, dict]:
    docs = [
        Counter(tokenize(f"{r['tieu_de']} {r['text']}", fold_accents)) for r in records
    ]
    lengths = [sum(d.values()) for d in docs]
    avg_len = (sum(lengths) / len(lengths)) if lengths else 0.0
    df: Counter = Counter()
    for d in docs:
        df.update(d.keys())
    n = len(docs)
    idf = {
        term: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()
    }
    return docs, avg_len, idf


def score(query_terms: list[str], doc: Counter, avg_len: float, idf: dict) -> float:
    doc_len = sum(doc.values()) or 1
    total = 0.0
    for term in query_terms:
        tf = doc.get(term, 0)
        if not tf:
            continue
        denom = tf + K1 * (1 - B + B * doc_len / avg_len)
        total += idf.get(term, 0.0) * tf * (K1 + 1) / denom
    return total


def snippet(text: str, query_terms: list[str], width: int = 320) -> str:
    """Cắt đoạn quanh vị trí xuất hiện đầu tiên của một từ khóa."""
    lowered = strip_accents(text.lower())
    best = -1
    for term in query_terms:
        pos = lowered.find(strip_accents(term))
        if pos != -1 and (best == -1 or pos < best):
            best = pos
    if best == -1:
        best = 0
    start = max(0, best - width // 3)
    end = min(len(text), start + width)
    body = " ".join(text[start:end].split())
    return ("… " if start else "") + body + (" …" if end < len(text) else "")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tìm kiếm trong kho văn bản xây dựng (BM25)."
    )
    parser.add_argument("query", nargs="+", help="Câu hỏi hoặc từ khóa")
    parser.add_argument("--k", type=int, default=5, help="Số kết quả (mặc định 5)")
    parser.add_argument("--doc", help="Chỉ tìm trong một văn bản (doc_id)")
    parser.add_argument(
        "--loai", help="Lọc theo loại chunk: dieu | phu-luc | bieu-mau | mo-dau"
    )
    parser.add_argument(
        "--full", action="store_true", help="In toàn văn chunk thay vì trích đoạn"
    )
    parser.add_argument("--json", action="store_true", help="Xuất JSON cho script/agent")
    parser.add_argument(
        "--khong-dau",
        action="store_true",
        help="Bỏ dấu khi so khớp (gõ 'chung chi hanh nghe' vẫn ra kết quả)",
    )
    args = parser.parse_args()

    records = load_index(INDEX_PATH)
    if args.doc:
        records = [r for r in records if r["doc_id"] == args.doc]
    if args.loai:
        records = [r for r in records if r["loai_chunk"] == args.loai]
    if not records:
        sys.exit("Không có chunk nào khớp bộ lọc.")

    docs, avg_len, idf = build_bm25(records, args.khong_dau)
    query = " ".join(args.query)
    query_terms = tokenize(query, args.khong_dau)
    if not query_terms:
        sys.exit("Câu truy vấn rỗng sau khi loại từ dừng.")

    ranked = sorted(
        (
            (score(query_terms, doc, avg_len, idf), rec)
            for doc, rec in zip(docs, records)
        ),
        key=lambda pair: pair[0],
        reverse=True,
    )
    hits = [(s, r) for s, r in ranked if s > 0][: args.k]

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "diem": round(s, 3),
                        "trich_dan": r["trich_dan"],
                        "tieu_de": r["tieu_de"],
                        "chuong": r["chuong"],
                        "duong_dan": r["duong_dan"],
                        "noi_dung": r["text"] if args.full else snippet(r["text"], query_terms),
                    }
                    for s, r in hits
                ],
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if not hits:
        print(f'Không tìm thấy kết quả cho: "{query}"')
        return

    print(f'Kết quả cho: "{query}"  ({len(hits)}/{len(records)} chunk)\n')
    for rank, (s, r) in enumerate(hits, 1):
        print(f"[{rank}] {r['trich_dan']}  (điểm {s:.2f})")
        print(f"    {r['tieu_de']}")
        if r["chuong"]:
            print(f"    {r['chuong']}")
        print(f"    → {r['duong_dan']}")
        print()
        body = r["text"] if args.full else snippet(r["text"], query_terms)
        for line in body.splitlines():
            print(f"    {line}")
        print()


if __name__ == "__main__":
    main()
