#!/usr/bin/env python3
"""
Tìm kiếm từ khóa (BM25) trên index/chunks.jsonl — không cần vector database.

    python3 tools/search.py "điều kiện cấp chứng chỉ hành nghề hạng I"
    python3 tools/search.py --gon "nhà thầu nước ngoài thu hồi giấy phép"
    python3 tools/search.py --doc qcvn-10-2025-bca --loai bang "karaoke tầng hầm"
    python3 tools/search.py --json "mã định danh quy hoạch"   # cho agent/script đọc

Mặc định in TOÀN VĂN chunk. Trước đây mặc định là trích đoạn 320 ký tự, nhưng
đoạn đó hay bị cắt ngang một khoản nên người đọc dễ kết luận thiếu vế. Với văn
bản pháp luật, đọc thiếu nửa điều khoản nguy hiểm hơn là đọc dài. Dùng `--gon`
khi chỉ cần lướt xem có gì.

Vì sao BM25 mà không phải embedding? Văn bản pháp luật dùng thuật ngữ rất cố
định ("chứng chỉ hành nghề", "chủ nhiệm", "hạng II"), nên so khớp từ khóa đã cho
kết quả tốt. Đo trên eval/bo_cau_hoi.jsonl: câu hỏi diễn đạt đời thường vẫn đạt
Recall@5 cao. Khi kho lớn tới hàng trăm văn bản thì mới nên cân nhắc bổ sung tìm
kiếm ngữ nghĩa — và phải đo trước khi đổi.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "index" / "chunks.jsonl"

K1 = 1.5   # tham số bão hòa tần suất từ của BM25
# Tham số chuẩn hóa theo độ dài. Thấp hơn mặc định 0,75 vì kho có các chunk dài
# rất khác nhau: một Điều luật vài trăm ký tự nằm cạnh Bảng A.1 dài 14 000 ký
# tự. Bảng tra cứu dài là bản chất của nó, không phải "loãng", nên phạt độ dài
# nhẹ tay hơn. Đo trên truy vấn thật: 0,5 đưa được bảng tra cứu đúng lên top-2,
# còn 0,75 thì đẩy nó ra ngoài.
B = 0.5

# KHÔNG CÓ NGƯỠNG TIN CẬY TỰ ĐỘNG — đây là kết luận có đo, không phải thiếu sót.
#
# Đã thử hai tín hiệu để hệ thống tự nhận biết câu hỏi nằm ngoài phạm vi corpus,
# đo trên 10 câu hỏi thuộc lĩnh vực kho không hề có (tải trọng gió, chống sét,
# hệ số truyền nhiệt, chứng chỉ hành nghề kiến trúc...):
#
#   1. Ngưỡng theo điểm BM25. Phân bố chồng lấn hoàn toàn: câu NGOÀI phạm vi đạt
#      tới 20,77 điểm, trong khi câu CÓ đáp án thật thấp nhất chỉ 4,16. Không tồn
#      tại ngưỡng nào tách được hai nhóm.
#   2. Ngưỡng theo độ phủ từ khoá hiếm. Còn tệ hơn — câu ngoài phạm vi phủ 0,50
#      đến 1,00 còn câu có đáp án tụt xuống 0,00, vì câu hỏi ngoài phạm vi vẫn
#      dùng toàn từ vựng xây dựng có sẵn trong kho ("nhà cao tầng", "công trình").
#
# Một nhãn tin cậy sai còn nguy hiểm hơn không có nhãn, vì nó tạo cảm giác an
# toàn giả. Vì vậy công cụ này chỉ in ra SỐ LIỆU THÔ để người/agent đọc tự đánh
# giá, và CLAUDE.md quy định quy trình kiểm chứng bắt buộc trước khi kết luận.
NGUONG_TIN_CAY = None

# Tiêu đề chunk được nhân trọng số khi lập chỉ mục: một Điều nói "về" cái gì thì
# tiêu đề của nó là tín hiệu mạnh hơn một lần nhắc bất kỳ trong thân bài.
TRONG_SO_TIEU_DE = 3

# Từ dừng: quá phổ biến trong văn bản pháp luật nên không giúp phân biệt.
STOPWORDS = {
    "và", "của", "các", "có", "được", "cho", "trong", "theo", "này", "tại",
    "với", "là", "khi", "hoặc", "về", "đối", "một", "những", "từ", "đến",
    "quy", "định", "thì", "để", "không", "phải", "sau", "trên", "như", "nếu",
    "do", "bằng", "còn", "đã", "sẽ", "mà", "nhưng", "vào", "ra", "ở", "cũng",
}

# Đơn vị và toán tử chỉ có 1 ký tự nhưng mang nghĩa — không được loại bỏ.
GIU_MOT_KY_TU = {"m", "%", ">=", "<="}

RE_DIEU = re.compile(r"\bđiều\s+(\d+)")
RE_MUC = re.compile(r"\bmục\s+([0-9]+(?:\.[0-9]+)*|[a-z]\.[0-9]+)")
RE_BANG = re.compile(r"\bbảng\s+([a-z]?\.?[0-9]+(?:\.[0-9]+)*)")
RE_HAU_TO_VB = re.compile(r"\b(bxd|bca|nđ-cp|nd-cp)\b")


def strip_accents(text: str) -> str:
    text = text.replace("đ", "d").replace("Đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def tokenize(text: str, fold_accents: bool = False) -> list[str]:
    """Tách từ, giữ nguyên nghĩa của dữ liệu định lượng.

    Bản đầu tiên của hàm này làm hỏng đúng nhóm dữ liệu quan trọng nhất với
    văn bản kỹ thuật:

        "1,20 m"    -> ['20']      mất cả phần nguyên lẫn đơn vị
        "500 m²"    -> ['500']     mất đơn vị diện tích
        "≥ 1200"    -> ['1200']    mất toán tử so sánh
        "mục 2.4.1" -> ['mục']     mất toàn bộ số hiệu

    Bốn phép chuẩn hoá dưới đây vá lại từng lỗi đó.
    """
    text = text.lower()
    if fold_accents:
        text = strip_accents(text)
    # "1 200" (khoảng trắng phân nhóm nghìn) -> "1200"
    text = re.sub(r"(?<=\d)[  ](?=\d{3}\b)", "", text)
    # "0,45" (dấu phẩy thập phân kiểu Việt) -> "0.45"
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    # Toán tử so sánh và số mũ đơn vị thành token đọc được
    text = (text.replace("≥", " >= ").replace("≤", " <= ")
                .replace("²", "2").replace("³", "3"))
    tho = re.findall(r"[0-9]+(?:\.[0-9]+)*|>=|<=|%|[0-9a-zà-ỹ]+", text)
    return [w for w in tho
            if w not in STOPWORDS and (len(w) > 1 or w in GIU_MOT_KY_TU)]


def tokenize_cu(text: str, fold_accents: bool = False) -> list[str]:
    """Tokenizer đời đầu — giữ lại để đối chứng trong eval, đừng dùng để tra cứu."""
    text = text.lower()
    if fold_accents:
        text = strip_accents(text)
    return [w for w in re.findall(r"[0-9a-zà-ỹ]+", text)
            if w not in STOPWORDS and len(w) > 1]


def truong_lap_chi_muc(r: dict) -> str:
    """Ghép các trường của chunk thành văn bản để lập chỉ mục."""
    return " ".join([
        *([r["tieu_de"]] * TRONG_SO_TIEU_DE),
        r.get("chuong") or "", r.get("muc") or "", r["trich_dan"], r["text"],
    ])


def load_index(path: Path = INDEX_PATH) -> list[dict]:
    if not path.exists():
        sys.exit(f"Chưa có chỉ mục: {path}\nHãy chạy trước: python3 tools/build_index.py")
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_bm25(records, fold_accents=False, tokfn=None, truong=None):
    tokfn = tokfn or tokenize
    truong = truong or truong_lap_chi_muc
    docs = [Counter(tokfn(truong(r), fold_accents)) for r in records]
    lengths = [sum(d.values()) for d in docs]
    avg_len = (sum(lengths) / len(lengths)) if lengths else 0.0
    df: Counter = Counter()
    for d in docs:
        df.update(d.keys())
    n = len(docs)
    idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
    return docs, avg_len, idf


def score(query_terms, doc, avg_len, idf) -> float:
    doc_len = sum(doc.values()) or 1
    total = 0.0
    for term in query_terms:
        tf = doc.get(term, 0)
        if not tf:
            continue
        denom = tf + K1 * (1 - B + B * doc_len / avg_len)
        total += idf.get(term, 0.0) * tf * (K1 + 1) / denom
    return total


def diem_cau_truc(r: dict, cau: str) -> float:
    """Cộng điểm khi truy vấn gọi đích danh một đơn vị của văn bản.

    "Điều 33 quy định gì" phải trả về Điều 33, không phải một Điều khác cũng
    nhắc tới số 33. BM25 thuần không phân biệt được số hiệu với số bất kỳ.
    """
    bonus = 0.0
    c = cau.lower()
    m = RE_DIEU.search(c)
    if m and r["loai_chunk"] == "dieu" and str(r.get("so_hieu_muc")) == m.group(1):
        bonus += 12
    m = RE_MUC.search(c)
    if m and str(r.get("so_hieu_muc") or "").lower() == m.group(1):
        bonus += 12
    m = RE_BANG.search(c)
    if m and m.group(1).upper().lstrip(".") in r["tieu_de"].upper():
        bonus += 10
    for hau_to in RE_HAU_TO_VB.findall(c):
        if hau_to in ("bxd", "bca") and r["doc_id"].endswith(hau_to):
            bonus += 6
        if hau_to in ("nđ-cp", "nd-cp") and "nd-cp" in r["doc_id"]:
            bonus += 6
    return bonus


# Hệ số nhân điểm cho chunk của tài liệu THAM KHẢO (hỏi đáp nghiệp vụ).
#
# Vì sao cần: tài liệu tham khảo là văn xuôi dài, dày từ khoá đời thường, nói
# đúng những chủ đề mà quy chuẩn nói bằng ngôn ngữ pháp lý cô đọng. Để nguyên
# trọng số thì nó lấn át chính điều khoản mà nó đang giải thích — đo được:
# thêm 133 chunk hỏi đáp làm Recall@3 tụt từ 0.774 xuống 0.728 trên bộ 165 câu.
#
# Vì sao hạ trọng số là đúng chứ không phải mẹo: khi cùng một truy vấn khớp cả
# điều khoản gốc lẫn lời giải thích về điều khoản đó, thứ người dùng cần trước
# là ĐIỀU KHOẢN. Lời giải thích chỉ có giá trị đi kèm.
#
# Giá trị chọn bằng cách quét dải và đo, xem eval/README.md.
HE_SO_THAM_KHAO = float(os.environ.get("HE_SO_THAM_KHAO", "0.90"))


# Hệ số cho tín hiệu VỊ TRÍ GẦN NHAU của các từ truy vấn trong chunk.
#
# Vì sao có tín hiệu này: BM25 chỉ đếm tần suất từ, không biết các từ đó nằm
# cạnh nhau hay rải rác khắp một chunk dài. Điều khoản pháp luật phát biểu quy
# định một cách cô đọng, nên các từ của câu hỏi thường nằm sát nhau; còn chunk
# dài trùng nhiều từ nhưng rải rác thường chỉ nhắc tới chủ đề chứ không quy
# định về nó.
#
# Đo được, không phải cảm tính: KHÔNG câu nào trong bộ đánh giá thất bại vì
# BM25 tìm không ra chunk vàng — mọi chunk vàng đều được tìm thấy, chỉ bị xếp
# hạng thấp (Recall@50 = 0.949 trong khi Recall@5 = 0.836). Nghĩa là việc cần
# làm là XẾP HẠNG LẠI, không phải đổi cách tìm.
#
# Giá trị 2.0 chọn bằng quét dải 0 → 3.5; vùng 1.0–2.5 là một MẶT PHẲNG cho
# cùng mức cải thiện (Recall@5 0.836 → 0.867), nên đây là tín hiệu thật chứ
# không phải khớp nhiễu của bộ đo.
HE_SO_GAN_NHAU = float(os.environ.get("HE_SO_GAN_NHAU", "2.0"))
# Chỉ xếp hạng lại trong NHÓM ĐẦU. Đã quét 10/15/20/30/50/100: giá trị 10 tốt
# nhất trên MỌI chỉ số. Xếp lại sâu hơn làm Recall@10 tụt, vì tín hiệu gần nhau
# đủ mạnh để đẩy một chunk vàng đang ở hạng 6–10 rơi xuống dưới 10 — được ở
# hạng 5 thì mất ở hạng 10.
SO_UNG_VIEN_XEP_LAI = 10


def diem_gan_nhau(query_terms, toks) -> float:
    """Cửa sổ NGẮN NHẤT chứa được nhiều từ truy vấn nhất, chuẩn hoá theo số từ.

    Trả về 0 khi chunk chứa dưới hai từ khác nhau của truy vấn — khi đó không
    có khái niệm "gần nhau".
    """
    vi_tri: dict[str, list[int]] = {}
    q = set(query_terms)
    for i, t in enumerate(toks):
        if t in q:
            vi_tri.setdefault(t, []).append(i)
    if len(vi_tri) < 2:
        return 0.0
    moc = sorted((i, t) for t, ds in vi_tri.items() for i in ds)
    can = len(vi_tri)
    tot = 0.0
    for a in range(len(moc)):
        thay = set()
        for b in range(a, len(moc)):
            thay.add(moc[b][1])
            if len(thay) == can:
                rong = moc[b][0] - moc[a][0] + 1
                tot = max(tot, can / (1 + rong / can))
                break
    return tot


def xep_hang(cau, records, docs, avg_len, idf, tokfn=None, dung_boost=True,
             truong=None):
    """Trả về [(điểm, chunk)] đã sắp giảm dần, bỏ các chunk điểm 0."""
    tokfn = tokfn or tokenize
    qt = tokfn(cau)
    ra = []
    for d, r in zip(docs, records):
        s = score(qt, d, avg_len, idf)
        if dung_boost:
            s += diem_cau_truc(r, cau)
        if r.get("gia_tri_phap_ly"):
            s *= HE_SO_THAM_KHAO
        if s > 0:
            ra.append((s, r))
    ra.sort(key=lambda x: x[0], reverse=True)

    # Xếp hạng lại nhóm đầu bằng tín hiệu vị trí gần nhau.
    if HE_SO_GAN_NHAU and ra:
        truong = truong or truong_lap_chi_muc
        dau = ra[:SO_UNG_VIEN_XEP_LAI]
        dau = [(s + HE_SO_GAN_NHAU * diem_gan_nhau(qt, tokfn(truong(r))), r)
               for s, r in dau]
        dau.sort(key=lambda x: x[0], reverse=True)
        ra = dau + ra[SO_UNG_VIEN_XEP_LAI:]
    return ra


def canh_bao_trung_so_hieu(hits, records) -> str | None:
    """Cảnh báo khi truy vấn có thể đang trỏ tới nhiều văn bản cùng số hiệu.

    Kho có QCVN 10:2024/BXD (tiếp cận cho người khuyết tật) và QCVN 10:2025/BCA
    (phòng cháy chữa cháy). Nếu kết quả chỉ nghiêng về một văn bản trong khi
    người hỏi không nói rõ đuôi, họ rất dễ nhận nhầm câu trả lời của văn bản kia
    mà không có dấu hiệu nào để nghi ngờ.
    """
    goc = {}
    for r in records:
        goc.setdefault(r["so_hieu"].split("/")[0].strip(), set()).add(r["so_hieu"])
    trung = {k: v for k, v in goc.items() if len(v) > 1}
    if not trung:
        return None
    co_trong_kq = {r["so_hieu"] for _, r in hits[:10]}
    for goc_chung, ho in trung.items():
        neu_lien_quan = ho & co_trong_kq
        if neu_lien_quan and len(neu_lien_quan) < len(ho):
            thieu = sorted(ho - neu_lien_quan)
            return (f"Kho có {len(ho)} văn bản cùng số hiệu gốc \"{goc_chung}\": "
                    f"{', '.join(sorted(ho))}. Kết quả dưới đây chỉ đến từ "
                    f"{', '.join(sorted(neu_lien_quan))}. "
                    f"Nếu bạn đang hỏi về {', '.join(thieu)} thì hãy ghi rõ đuôi "
                    f"văn bản trong câu hỏi.")
    return None


def snippet(text: str, query_terms: list[str], width: int = 320) -> str:
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
        description="Tìm kiếm trong kho văn bản xây dựng (BM25).")
    parser.add_argument("query", nargs="+", help="Câu hỏi hoặc từ khóa")
    parser.add_argument("--k", type=int, default=5, help="Số kết quả (mặc định 5)")
    parser.add_argument("--doc", help="Chỉ tìm trong một văn bản (doc_id)")
    parser.add_argument("--loai", help="Lọc loại chunk: dieu | muc | phan | bang | bieu-mau | phu-luc")
    parser.add_argument("--gon", action="store_true",
                        help="Chỉ in trích đoạn thay vì toàn văn (mặc định in toàn văn)")
    parser.add_argument("--json", action="store_true", help="Xuất JSON cho script/agent")
    parser.add_argument("--khong-dau", action="store_true",
                        help="Bỏ dấu khi so khớp (gõ 'chung chi hanh nghe' vẫn ra kết quả)")
    parser.add_argument("--tokenizer-cu", action="store_true",
                        help="Dùng tokenizer đời đầu để đối chứng (không khuyến nghị)")
    args = parser.parse_args()

    records = load_index()
    tong_so_vb = len({r["doc_id"] for r in records})
    if args.doc:
        records = [r for r in records if r["doc_id"] == args.doc]
    if args.loai:
        records = [r for r in records if r["loai_chunk"] == args.loai]
    if not records:
        sys.exit("Không có chunk nào khớp bộ lọc.")

    tokfn = tokenize_cu if args.tokenizer_cu else tokenize
    docs, avg_len, idf = build_bm25(records, args.khong_dau, tokfn=tokfn)
    query = " ".join(args.query)
    query_terms = tokfn(query, args.khong_dau)
    if not query_terms:
        sys.exit("Câu truy vấn rỗng sau khi loại từ dừng.")

    hits_full = xep_hang(query, records, docs, avg_len, idf, tokfn,
                         dung_boost=not args.tokenizer_cu)
    hits = hits_full[: args.k]
    canh_bao = canh_bao_trung_so_hieu(hits_full, load_index())

    if args.json:
        print(json.dumps({
            "truy_van": query,
            "canh_bao": canh_bao,
            "luu_y": "Điểm số chỉ đo mức trùng từ khoá, KHÔNG đo mức liên quan. "
                     "Điểm cao không bảo đảm chunk có quy định về việc được hỏi. "
                     "Phải tự đọc nội dung để xác nhận trước khi kết luận.",
            "ket_qua": [{
                "diem": round(s, 3), "trich_dan": r["trich_dan"],
                "tieu_de": r["tieu_de"], "chuong": r["chuong"],
                "duong_dan": r["duong_dan"],
                "sua_doi_boi": r.get("sua_doi_boi") or [],
                "gia_tri_phap_ly": r.get("gia_tri_phap_ly") or "",
                "hop_nhat_tu": r.get("hop_nhat_tu") or [],
                "trang_thai": r.get("trang_thai") or "",
                "vien_dan_da_bi_thay_the": r.get("vien_dan_da_bi_thay_the") or [],
                "vien_dan_ngoai_kho": r.get("vien_dan_ngoai_kho") or [],
                "noi_dung": snippet(r["text"], query_terms) if args.gon else r["text"],
            } for s, r in hits],
        }, ensure_ascii=False, indent=2))
        return

    if not hits:
        print(f'Không có chunk nào chứa từ khóa của: "{query}"')
        print(f'\nKho hiện có {tong_so_vb} văn bản, {len(records)} chunk. '
              f'Kết quả rỗng nghĩa là KHÔNG CHUNK NÀO CHỨA TỪ KHÓA NÀY,\n'
              f'KHÔNG có nghĩa là "pháp luật không quy định". Hãy thử từ khóa '
              f'khác, hoặc kết luận rằng\nvấn đề này nằm ngoài phạm vi các văn '
              f'bản đang có trong kho.')
        return

    if canh_bao:
        print(f"⚠️  {canh_bao}\n")

    print(f'Kết quả cho: "{query}"  ({len(hits)}/{len(records)} chunk)')
    print("    Điểm số chỉ đo mức trùng từ khoá, KHÔNG đo mức liên quan — hãy đọc "
          "nội dung để tự xác nhận.\n")
    for rank, (s, r) in enumerate(hits, 1):
        print(f"[{rank}] {r['trich_dan']}  (điểm {s:.2f})")
        for sd in r.get("sua_doi_boi") or []:
            print(f"    ⚠️  ĐÃ BỊ SỬA ĐỔI bởi {sd['so_hieu']} "
                  f"(hiệu lực {sd['ngay_hieu_luc']}) — ĐỌC CẢ HAI TRƯỚC KHI TRẢ LỜI")
            print(f"       → {sd['duong_dan']}")
        if r.get("trang_thai") == "KHUNG RỖNG":
            print("    📭  KHUNG RỖNG — kho CHƯA CÓ NỘI DUNG của văn bản này.")
            print("       Chỉ có tên, số hiệu, ngày ban hành. Không trích được điều khoản nào.")
            print("       Phải nói thẳng với người dùng là kho thiếu và đề nghị cung cấp bản gốc.")
        if r.get("hop_nhat_tu"):
            goc = ", ".join(r["hop_nhat_tu"])
            print( "    🧩  VĂN BẢN HỢP NHẤT — bản ghép, KHÔNG tự nó là văn bản quy "
                   "phạm pháp luật.")
            print(f"       Trích dẫn phải nêu văn bản gốc: {goc}.")
            print( "       Nội dung ở đây đã vá sẵn các lần sửa đổi; đọc ghi chú "
                   "trong ngoặc để biết chỗ nào do văn bản nào sửa.")
        if r.get("gia_tri_phap_ly"):
            print(f"    🛑  {r['gia_tri_phap_ly']} — KHÔNG ĐƯỢC dùng làm căn cứ "
                  f"pháp lý.")
            print( "       Đây là cách cơ quan quản lý ĐANG HIỂU quy định, không "
                   "phải bản thân quy định.")
            print( "       Phải trích văn bản quy phạm pháp luật mà nó viện dẫn, "
                   "và nói rõ đây là tài liệu tham khảo.")
        for vd in r.get("vien_dan_da_bi_thay_the") or []:
            print(f"    ⚠️  Viện dẫn {vd['so_hieu']} — kho xác định văn bản này ĐÃ BỊ "
                  f"THAY THẾ bởi {vd['thay_the_boi']}.")
        if r.get("vien_dan_ngoai_kho"):
            print(f"    ⚠️  Viện dẫn văn bản KHÔNG CÓ TRONG KHO: "
                  f"{', '.join(r['vien_dan_ngoai_kho'])}")
            print( "       Không tự kiểm chứng được nội dung lẫn hiệu lực của các "
                   "văn bản này.")
        print(f"    {r['tieu_de']}")
        if r["chuong"]:
            print(f"    {r['chuong']}")
        print(f"    → {r['duong_dan']}")
        print()
        body = snippet(r["text"], query_terms) if args.gon else r["text"]
        for line in body.splitlines():
            print(f"    {line}")
        print()


if __name__ == "__main__":
    # Cho phép `search.py ... | head` mà không vỡ: khi đầu đọc đóng ống sớm,
    # Python ném BrokenPipeError lúc dọn dẹp. Trả về mã thoát 141 như shell.
    try:
        main()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(141)
    except KeyboardInterrupt:
        sys.exit(130)
