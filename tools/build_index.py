#!/usr/bin/env python3
"""
Chia nhỏ (chunk) toàn văn các văn bản trong corpus/ thành đơn vị trích dẫn tự
nhiên của từng loại văn bản, rồi sinh ra:

    chunks/<doc_id>/<chunk_id>.md   – mỗi Điều/mục một file, có front matter
    index/chunks.jsonl              – chỉ mục để truy hồi (retrieval)
    index/documents.json            – sổ đăng ký văn bản
    corpus/<...>/muc-luc.md         – mục lục điều hướng

Hai kiểu cấu trúc, khai báo bằng khóa `cau_truc` trong front matter:

    cau_truc: "dieu"  (mặc định) – Nghị định, Luật, Thông tư…
                                   cắt tại "### Điều 12. Tên điều"
    cau_truc: "muc"              – Quy chuẩn (QCVN), Tiêu chuẩn (TCVN)…
                                   cắt tại "### 1.1 Tên mục"; phần "## 3 TÊN"
                                   không có mục con thì tự nó là một chunk

Phụ lục cắt theo khóa `chia_theo` trong front matter của từng file phụ lục:

    chia_theo: "Mẫu số"   – cắt tại "## Mẫu số 01 — Tên mẫu"
    chia_theo: "Bảng"     – cắt tại "## Bảng A.1 - Tên bảng"
    chia_theo: "H."       – cắt tại "## H.1 Tên mục"
    (không khai báo)      – tự dò "Mẫu số", nếu không có thì giữ nguyên cả file

Chạy lại script này mỗi khi corpus/ thay đổi:

    python3 tools/build_index.py

Không phụ thuộc thư viện ngoài (chỉ dùng thư viện chuẩn của Python).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
CHUNKS = ROOT / "chunks"
INDEX = ROOT / "index"

# --- Cấu trúc "dieu": Nghị định, Luật, Thông tư ------------------------------
RE_DIEU = re.compile(r"^###\s+Điều\s+(\d+)\.\s*(.+?)\s*$")
RE_CHUONG = re.compile(r"^##\s+(Chương\s+[IVXLC]+)\.\s*(.+?)\s*$")
RE_MUC_LA_MA = re.compile(r"^###\s+(Mục\s+\d+)\.\s*(.+?)\s*$")

# --- Cấu trúc "muc": Quy chuẩn, Tiêu chuẩn ----------------------------------
# "## 1 QUY ĐỊNH CHUNG" hoặc "## LỜI NÓI ĐẦU"
RE_PHAN = re.compile(r"^##\s+(?:(\d+(?:\.\d+)*)\s+)?(.+?)\s*$")
# "### 1.1 Phạm vi điều chỉnh"
RE_MUC_SO = re.compile(r"^###\s+(\d+(?:\.\d+)*)\s+(.+?)\s*$")

# --- Phụ lục ----------------------------------------------------------------
RE_H2 = re.compile(r"^##\s+(.+?)\s*$")

# Link ảnh Markdown: ![mô tả](duong-dan.png)
RE_ANH = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def doi_duong_dan_anh(text: str, nguon: Path, dich: Path) -> str:
    """Sửa link ảnh tương đối khi chuyển nội dung từ corpus/ sang chunks/.

    Trong corpus, ảnh được trỏ tương đối theo file nguồn (ví dụ `hinh/h-01.png`).
    File chunk nằm ở thư mục khác nên cùng đường dẫn đó sẽ trỏ hụt. Hàm này tính
    lại đường dẫn tương đối từ vị trí file chunk. Link tuyệt đối hoặc link mạng
    được giữ nguyên.
    """

    def thay(m: re.Match) -> str:
        mo_ta, duong_dan = m.group(1), m.group(2).strip()
        if duong_dan.startswith(("http://", "https://", "data:", "/", "#")):
            return m.group(0)
        moi = os.path.relpath((nguon.parent / duong_dan).resolve(), dich.resolve())
        return f"![{mo_ta}]({Path(moi).as_posix()})"

    return RE_ANH.sub(thay, text)


def read_front_matter(text: str) -> tuple[dict, str]:
    """Tách YAML front matter đơn giản (key: value) khỏi phần thân."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw, body = text[4:end], text[end + 5 :]
    meta: dict = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip().strip('"')
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            parsed = [v.strip().strip('"') for v in inner.split(",") if v.strip()]
            meta[key.strip()] = parsed
        else:
            meta[key.strip()] = value
    return meta, body


def slugify(text: str, max_len: int = 60) -> str:
    """'Điều kiện năng lực' -> 'dieu-kien-nang-luc' (bỏ dấu tiếng Việt)."""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:max_len].rstrip("-")


def yaml_value(value) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(f'"{v}"' for v in value) + "]"
    return f'"{value}"'


class ChunkBuilder:
    """Gom dòng vào chunk hiện tại, chốt lại khi gặp tiêu đề mới."""

    def __init__(self) -> None:
        self.chunks: list[dict] = []
        self.current: dict | None = None

    def start(self, **fields) -> None:
        self.flush()
        self.current = {**fields, "lines": []}

    def add(self, line: str) -> None:
        if self.current is not None:
            self.current["lines"].append(line)

    def flush(self) -> None:
        if self.current is None:
            return
        text = "\n".join(self.current.pop("lines")).strip()
        if text:
            self.current["text"] = text
            self.chunks.append(self.current)
        self.current = None


def split_dieu(meta: dict, body: str) -> list[dict]:
    """Cắt toàn văn nghị định thành các chunk theo Điều."""
    doc_id = meta["doc_id"]
    builder = ChunkBuilder()
    chuong = muc = None
    preamble: list[str] = []

    for line in body.splitlines():
        m = RE_CHUONG.match(line)
        if m:
            chuong = f"{m.group(1)}. {m.group(2)}"
            muc = None
            builder.add("")
            continue

        m = RE_MUC_LA_MA.match(line)
        if m:
            muc = f"{m.group(1)}. {m.group(2)}"
            continue

        m = RE_DIEU.match(line)
        if m:
            so, tieu_de = int(m.group(1)), m.group(2)
            builder.start(
                chunk_id=f"{doc_id}:dieu-{so:02d}",
                loai="dieu",
                so_hieu_muc=str(so),
                sap_xep=(1, so),
                tieu_de=tieu_de,
                chuong=chuong,
                muc=muc,
                slug=f"dieu-{so:02d}-{slugify(tieu_de)}",
            )
            continue

        if builder.current is None:
            preamble.append(line)
        else:
            builder.add(line)

    builder.flush()
    chunks = builder.chunks

    preamble_text = "\n".join(preamble).strip()
    if preamble_text:
        chunks.insert(
            0,
            {
                "chunk_id": f"{doc_id}:mo-dau",
                "loai": "mo-dau",
                "so_hieu_muc": None,
                "sap_xep": (0, 0),
                "tieu_de": "Phần mở đầu và căn cứ ban hành",
                "chuong": None,
                "muc": None,
                "slug": "00-mo-dau-can-cu-ban-hanh",
                "text": preamble_text,
            },
        )
    return chunks


def sort_key(so_hieu: str | None) -> tuple:
    """'1.10' xếp sau '1.2' (so sánh từng số, không so chuỗi)."""
    if not so_hieu:
        return (0,)
    return tuple(int(p) for p in so_hieu.split(".") if p.isdigit())


def split_muc(meta: dict, body: str) -> list[dict]:
    """Cắt toàn văn quy chuẩn/tiêu chuẩn thành chunk theo mục (1.1, 2.3...)."""
    doc_id = meta["doc_id"]
    builder = ChunkBuilder()
    phan = None
    preamble: list[str] = []
    order = 0

    for line in body.splitlines():
        m = RE_MUC_SO.match(line)
        if m:
            so, tieu_de = m.group(1), m.group(2)
            order += 1
            builder.start(
                chunk_id=f"{doc_id}:muc-{so}",
                loai="muc",
                so_hieu_muc=so,
                sap_xep=(1,) + sort_key(so),
                tieu_de=tieu_de,
                chuong=phan,
                muc=None,
                slug=f"muc-{so.replace('.', '-')}-{slugify(tieu_de)}",
            )
            continue

        m = RE_PHAN.match(line)
        if m:
            so, tieu_de = m.group(1), m.group(2)
            phan = f"{so} {tieu_de}" if so else tieu_de
            order += 1
            # Phần này tự thành một chunk nếu bên dưới không có mục con nào;
            # ChunkBuilder tự bỏ chunk rỗng khi flush.
            builder.start(
                chunk_id=f"{doc_id}:phan-{so or slugify(tieu_de, 20)}",
                loai="phan",
                so_hieu_muc=so,
                sap_xep=(1,) + (sort_key(so) if so else (order,)),
                tieu_de=tieu_de,
                chuong=phan,
                muc=None,
                slug=f"phan-{so or slugify(tieu_de, 30)}-{slugify(tieu_de)}",
            )
            continue

        if builder.current is None:
            preamble.append(line)
        else:
            builder.add(line)

    builder.flush()
    chunks = builder.chunks

    preamble_text = "\n".join(preamble).strip()
    if preamble_text:
        chunks.insert(
            0,
            {
                "chunk_id": f"{doc_id}:mo-dau",
                "loai": "mo-dau",
                "so_hieu_muc": None,
                "sap_xep": (0, 0),
                "tieu_de": "Phần mở đầu",
                "chuong": None,
                "muc": None,
                "slug": "00-mo-dau",
                "text": preamble_text,
            },
        )
    return chunks


def split_toan_van(path: Path) -> tuple[dict, list[dict]]:
    meta, body = read_front_matter(path.read_text(encoding="utf-8"))
    if meta.get("cau_truc") == "muc":
        return meta, split_muc(meta, body)
    return meta, split_dieu(meta, body)


def split_phu_luc(path: Path, thu_tu: int = 0) -> tuple[dict, list[dict]]:
    """Phụ lục: cắt theo `chia_theo`, mặc định giữ nguyên cả phụ lục."""
    meta, body = read_front_matter(path.read_text(encoding="utf-8"))
    doc_id = meta["doc_id"]
    phan = meta.get("phan", path.stem)
    phan_slug = slugify(phan)
    lines = body.splitlines()

    prefix = meta.get("chia_theo")
    if prefix is None and any(
        RE_H2.match(l) and RE_H2.match(l).group(1).startswith("Mẫu số") for l in lines
    ):
        prefix = "Mẫu số"

    loai_theo_prefix = {"Mẫu số": "bieu-mau", "Bảng": "bang"}

    def matches(line: str) -> str | None:
        m = RE_H2.match(line)
        if m and prefix and m.group(1).startswith(prefix):
            return m.group(1)
        return None

    if not prefix or not any(matches(l) for l in lines):
        return meta, [
            {
                "chunk_id": f"{doc_id}:{phan_slug}",
                "loai": "phu-luc",
                "so_hieu_muc": None,
                "sap_xep": (2, thu_tu, 0),
                "tieu_de": meta.get("tieu_de", phan),
                "chuong": phan,
                "muc": None,
                "slug": f"{phan_slug}-{slugify(meta.get('tieu_de', ''))}",
                "text": body.strip(),
            }
        ]

    builder = ChunkBuilder()
    header: list[str] = []
    order = 0

    for line in lines:
        heading = matches(line)
        if heading is not None:
            order += 1
            loai = loai_theo_prefix.get(prefix, "muc")
            so_muc, tieu_de = None, heading
            if loai == "muc":
                # "H.1 Yêu cầu thiết kế…" -> so_muc="H.1", tieu_de="Yêu cầu thiết kế…"
                dau, _, con_lai = heading.partition(" ")
                if con_lai:
                    so_muc, tieu_de = dau, con_lai
            builder.start(
                chunk_id=f"{doc_id}:{phan_slug}-{slugify(heading, 40)}",
                loai=loai,
                so_hieu_muc=so_muc,
                sap_xep=(2, thu_tu, order),
                tieu_de=tieu_de,
                chuong=phan,
                muc=None,
                slug=f"{phan_slug}-{order:02d}-{slugify(heading)}",
            )
            builder.add(line)
            continue
        if builder.current is None:
            header.append(line)
        else:
            builder.add(line)

    builder.flush()
    chunks = builder.chunks

    header_text = "\n".join(header).strip()
    if header_text:
        chunks.insert(
            0,
            {
                "chunk_id": f"{doc_id}:{phan_slug}-gioi-thieu",
                "loai": "phu-luc",
                "so_hieu_muc": None,
                "sap_xep": (2, thu_tu, -1),
                "tieu_de": f"{phan} — {meta.get('tieu_de', '')}",
                "chuong": phan,
                "muc": None,
                "slug": f"{phan_slug}-00-gioi-thieu",
                "text": header_text,
            },
        )
    return meta, chunks


def citation(doc_meta: dict, chunk: dict) -> str:
    """Chuỗi trích dẫn chuẩn cho từng loại văn bản."""
    so_hieu = doc_meta.get("so_hieu", doc_meta["doc_id"])
    loai = doc_meta.get("loai_van_ban", "")
    la_quy_chuan = so_hieu.startswith(("QCVN", "TCVN"))
    ten_vb = so_hieu if la_quy_chuan else f"{loai} số {so_hieu}"

    if chunk["loai"] == "dieu":
        return f"Điều {chunk['so_hieu_muc']} {ten_vb}"
    if chunk["loai"] in {"muc", "phan"}:
        if chunk["so_hieu_muc"]:
            return f"mục {chunk['so_hieu_muc']} {ten_vb}"
        return f"{chunk['tieu_de']} {ten_vb}"
    if chunk["loai"] == "bang":
        return f"{chunk['tieu_de']}, {chunk.get('chuong') or ''} {ten_vb}".replace(" ,", ",")
    if chunk["loai"] in {"phu-luc", "bieu-mau", "bang"}:
        phan = chunk.get("chuong") or ""
        return f"{chunk['tieu_de']}, {phan} {ten_vb}".replace(" ,", ",")
    return ten_vb


def write_chunk_file(doc_meta: dict, chunk: dict, source: Path) -> Path:
    out_dir = CHUNKS / doc_meta["doc_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{chunk['slug']}.md"

    fm = {
        "chunk_id": chunk["chunk_id"],
        "doc_id": doc_meta["doc_id"],
        "so_hieu": doc_meta.get("so_hieu", ""),
        "loai_van_ban": doc_meta.get("loai_van_ban", ""),
        "ngay_ban_hanh": doc_meta.get("ngay_ban_hanh", ""),
        "loai_chunk": chunk["loai"],
        "tieu_de": chunk["tieu_de"],
        "nguon": str(source.relative_to(ROOT)),
    }
    if chunk.get("so_hieu_muc"):
        fm["so_hieu_muc"] = chunk["so_hieu_muc"]
    if chunk.get("chuong"):
        fm["chuong"] = chunk["chuong"]
    if chunk.get("muc"):
        fm["muc"] = chunk["muc"]

    lines = ["---"]
    lines += [f"{k}: {yaml_value(v)}" for k, v in fm.items()]
    lines += ["---", "", f"> **Trích dẫn:** {citation(doc_meta, chunk)}", ""]
    if chunk["loai"] == "dieu":
        lines += [f"# Điều {chunk['so_hieu_muc']}. {chunk['tieu_de']}", ""]
    elif chunk["loai"] in {"muc", "phan"} and chunk.get("so_hieu_muc"):
        lines += [f"# {chunk['so_hieu_muc']} {chunk['tieu_de']}", ""]
    lines += [doi_duong_dan_anh(chunk["text"], source, out_dir), ""]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def write_muc_luc(doc_dir: Path, doc_meta: dict, chunks: list[dict]) -> None:
    ten = doc_meta.get("so_hieu", "")
    if not ten.startswith(("QCVN", "TCVN")):
        ten = f"{doc_meta.get('loai_van_ban', '')} số {ten}"
    lines = [
        f"# Mục lục — {ten}",
        "",
        f"*{doc_meta.get('tieu_de', '')}*",
        "",
        "> File này được sinh tự động bởi `tools/build_index.py` — đừng sửa tay.",
        "",
    ]
    nhom_hien_tai = object()
    for chunk in chunks:
        if chunk["loai_chunk"] == "mo-dau":
            continue
        if chunk["chuong"] != nhom_hien_tai:
            nhom_hien_tai = chunk["chuong"]
            lines += ["", f"## {nhom_hien_tai or 'Khác'}", ""]
        rel = Path("..") / ".." / ".." / chunk["duong_dan"]
        if chunk["loai_chunk"] == "dieu":
            nhan = f"Điều {chunk['so_hieu_muc']}. {chunk['tieu_de']}"
        elif chunk.get("so_hieu_muc"):
            nhan = f"{chunk['so_hieu_muc']} {chunk['tieu_de']}"
        else:
            nhan = chunk["tieu_de"]
        lines.append(f"- [{nhan}]({rel.as_posix()})")
    lines.append("")
    (doc_dir / "muc-luc.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if CHUNKS.exists():
        shutil.rmtree(CHUNKS)
    CHUNKS.mkdir(parents=True, exist_ok=True)
    INDEX.mkdir(parents=True, exist_ok=True)

    documents: list[dict] = []
    all_chunks: list[dict] = []

    for toan_van in sorted(CORPUS.rglob("toan-van.md")):
        doc_dir = toan_van.parent
        doc_meta, chunks = split_toan_van(toan_van)
        sources: list[tuple[Path, list[dict]]] = [(toan_van, chunks)]

        for thu_tu, phu_luc in enumerate(sorted((doc_dir / "phu-luc").glob("*.md"))):
            _, pl_chunks = split_phu_luc(phu_luc, thu_tu)
            sources.append((phu_luc, pl_chunks))

        doc_chunks: list[dict] = []
        for source, source_chunks in sources:
            for chunk in source_chunks:
                path = write_chunk_file(doc_meta, chunk, source)
                doc_chunks.append(
                    {
                        "chunk_id": chunk["chunk_id"],
                        "doc_id": doc_meta["doc_id"],
                        "so_hieu": doc_meta.get("so_hieu", ""),
                        "loai_chunk": chunk["loai"],
                        "so_hieu_muc": chunk.get("so_hieu_muc"),
                        "tieu_de": chunk["tieu_de"],
                        "chuong": chunk.get("chuong"),
                        "muc": chunk.get("muc"),
                        "trich_dan": citation(doc_meta, chunk),
                        "duong_dan": str(path.relative_to(ROOT)),
                        "nguon": str(source.relative_to(ROOT)),
                        "so_ky_tu": len(chunk["text"]),
                        "_sap_xep": chunk["sap_xep"],
                        "text": chunk["text"],
                    }
                )
        doc_chunks.sort(key=lambda c: c["_sap_xep"])
        for c in doc_chunks:
            del c["_sap_xep"]
        all_chunks.extend(doc_chunks)

        don_vi = sum(1 for c in doc_chunks if c["loai_chunk"] in {"dieu", "muc", "phan"})
        documents.append(
            {
                "doc_id": doc_meta["doc_id"],
                "so_hieu": doc_meta.get("so_hieu", ""),
                "loai_van_ban": doc_meta.get("loai_van_ban", ""),
                "tieu_de": doc_meta.get("tieu_de", ""),
                "co_quan_ban_hanh": doc_meta.get("co_quan_ban_hanh", ""),
                "ngay_ban_hanh": doc_meta.get("ngay_ban_hanh", ""),
                "linh_vuc": doc_meta.get("linh_vuc", []),
                "nguon": doc_meta.get("nguon", ""),
                "cau_truc": doc_meta.get("cau_truc", "dieu"),
                "toan_van": str(toan_van.relative_to(ROOT)),
                "so_don_vi": don_vi,
                "so_chunk": len(doc_chunks),
            }
        )
        write_muc_luc(doc_dir, doc_meta, doc_chunks)

    with (INDEX / "chunks.jsonl").open("w", encoding="utf-8") as fh:
        for record in all_chunks:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    (INDEX / "documents.json").write_text(
        json.dumps(documents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Đã xử lý {len(documents)} văn bản, {len(all_chunks)} chunk.")
    for doc in documents:
        don_vi = "Điều" if doc["cau_truc"] == "dieu" else "mục"
        print(f"  - {doc['so_hieu']}: {doc['so_don_vi']} {don_vi}, {doc['so_chunk']} chunk")


if __name__ == "__main__":
    main()
