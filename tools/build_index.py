#!/usr/bin/env python3
"""
Chia nhỏ (chunk) toàn văn các văn bản trong corpus/ thành từng Điều / từng Mẫu,
rồi sinh ra:

    chunks/<doc_id>/<chunk_id>.md   – mỗi Điều một file, có front matter
    index/chunks.jsonl              – chỉ mục để truy hồi (retrieval)
    index/documents.json            – sổ đăng ký văn bản
    corpus/<...>/muc-luc.md         – mục lục điều hướng

Chạy lại script này mỗi khi corpus/ thay đổi:

    python3 tools/build_index.py

Không phụ thuộc thư viện ngoài (chỉ dùng thư viện chuẩn của Python).
"""
from __future__ import annotations

import json
import re
import shutil
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
CHUNKS = ROOT / "chunks"
INDEX = ROOT / "index"

# Một Điều bắt đầu bằng "### Điều <số>. <tiêu đề>"
RE_DIEU = re.compile(r"^###\s+Điều\s+(\d+)\.\s*(.+?)\s*$")
RE_CHUONG = re.compile(r"^##\s+(Chương\s+[IVXLC]+)\.\s*(.+?)\s*$")
RE_MUC = re.compile(r"^###\s+(Mục\s+\d+)\.\s*(.+?)\s*$")
# Một Mẫu trong phụ lục biểu mẫu bắt đầu bằng "## Mẫu số NN — <tên>"
RE_MAU = re.compile(r"^##\s+Mẫu\s+số\s+(\d+)\s*[—-]\s*(.+?)\s*$")


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


def split_toan_van(path: Path) -> tuple[dict, list[dict]]:
    """Cắt toàn văn nghị định thành các chunk theo Điều."""
    meta, body = read_front_matter(path.read_text(encoding="utf-8"))
    lines = body.splitlines()

    chunks: list[dict] = []
    chuong = muc = None
    current: dict | None = None
    preamble: list[str] = []

    def flush() -> None:
        if current is not None:
            current["text"] = "\n".join(current["lines"]).strip()
            del current["lines"]
            chunks.append(current)

    for line in lines:
        m_chuong = RE_CHUONG.match(line)
        if m_chuong:
            chuong = f"{m_chuong.group(1)}. {m_chuong.group(2)}"
            muc = None
            if current is not None:
                current["lines"].append("")  # giữ khoảng cách, không nuốt nội dung
            continue

        m_muc = RE_MUC.match(line)
        if m_muc:
            muc = f"{m_muc.group(1)}. {m_muc.group(2)}"
            continue

        m_dieu = RE_DIEU.match(line)
        if m_dieu:
            flush()
            so = int(m_dieu.group(1))
            tieu_de = m_dieu.group(2)
            current = {
                "chunk_id": f"{meta['doc_id']}:dieu-{so:02d}",
                "loai": "dieu",
                "so_dieu": so,
                "tieu_de": tieu_de,
                "chuong": chuong,
                "muc": muc,
                "slug": f"dieu-{so:02d}-{slugify(tieu_de)}",
                "lines": [],
            }
            continue

        if current is None:
            preamble.append(line)
        else:
            current["lines"].append(line)

    flush()

    preamble_text = "\n".join(preamble).strip()
    if preamble_text:
        chunks.insert(
            0,
            {
                "chunk_id": f"{meta['doc_id']}:mo-dau",
                "loai": "mo-dau",
                "so_dieu": 0,
                "tieu_de": "Phần mở đầu và căn cứ ban hành",
                "chuong": None,
                "muc": None,
                "slug": "00-mo-dau-can-cu-ban-hanh",
                "text": preamble_text,
            },
        )
    return meta, chunks


def split_phu_luc(path: Path) -> tuple[dict, list[dict]]:
    """Phụ lục: tách theo Mẫu nếu có, ngược lại giữ nguyên cả phụ lục làm 1 chunk."""
    meta, body = read_front_matter(path.read_text(encoding="utf-8"))
    phan = meta.get("phan", path.stem)
    phan_slug = slugify(phan)

    if not any(RE_MAU.match(line) for line in body.splitlines()):
        return meta, [
            {
                "chunk_id": f"{meta['doc_id']}:{phan_slug}",
                "loai": "phu-luc",
                "so_dieu": None,
                "tieu_de": meta.get("tieu_de", phan),
                "chuong": phan,
                "muc": None,
                "slug": f"{phan_slug}-{slugify(meta.get('tieu_de', ''))}",
                "text": body.strip(),
            }
        ]

    chunks: list[dict] = []
    header: list[str] = []
    current: dict | None = None

    def flush() -> None:
        if current is not None:
            current["text"] = "\n".join(current["lines"]).strip()
            del current["lines"]
            chunks.append(current)

    for line in body.splitlines():
        m_mau = RE_MAU.match(line)
        if m_mau:
            flush()
            so = int(m_mau.group(1))
            tieu_de = m_mau.group(2)
            current = {
                "chunk_id": f"{meta['doc_id']}:{phan_slug}-mau-{so:02d}",
                "loai": "bieu-mau",
                "so_dieu": None,
                "tieu_de": f"Mẫu số {so:02d} — {tieu_de}",
                "chuong": phan,
                "muc": None,
                "slug": f"{phan_slug}-mau-{so:02d}-{slugify(tieu_de)}",
                "lines": [line],
            }
            continue
        if current is None:
            header.append(line)
        else:
            current["lines"].append(line)
    flush()

    header_text = "\n".join(header).strip()
    if header_text:
        chunks.insert(
            0,
            {
                "chunk_id": f"{meta['doc_id']}:{phan_slug}-danh-muc",
                "loai": "phu-luc",
                "so_dieu": None,
                "tieu_de": f"{phan} — Danh mục biểu mẫu",
                "chuong": phan,
                "muc": None,
                "slug": f"{phan_slug}-00-danh-muc",
                "text": header_text,
            },
        )
    return meta, chunks


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
    if chunk.get("so_dieu"):
        fm["so_dieu"] = chunk["so_dieu"]
    if chunk.get("chuong"):
        fm["chuong"] = chunk["chuong"]
    if chunk.get("muc"):
        fm["muc"] = chunk["muc"]

    lines = ["---"]
    lines += [f"{k}: {yaml_value(v)}" for k, v in fm.items()]
    lines.append("---")
    lines.append("")

    trich_dan = citation(doc_meta, chunk)
    lines.append(f"> **Trích dẫn:** {trich_dan}")
    lines.append("")
    if chunk["loai"] == "dieu":
        lines.append(f"# Điều {chunk['so_dieu']}. {chunk['tieu_de']}")
        lines.append("")
    lines.append(chunk["text"])
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def citation(doc_meta: dict, chunk: dict) -> str:
    so_hieu = doc_meta.get("so_hieu", doc_meta["doc_id"])
    if chunk["loai"] == "dieu":
        return f"Điều {chunk['so_dieu']} Nghị định số {so_hieu}"
    if chunk["loai"] in {"phu-luc", "bieu-mau"}:
        return f"{chunk['tieu_de']}, {chunk.get('chuong') or ''} Nghị định số {so_hieu}".replace(" ,", ",")
    return f"Nghị định số {so_hieu}"


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
        sources = {toan_van: chunks}

        for phu_luc in sorted((doc_dir / "phu-luc").glob("*.md")):
            _, pl_chunks = split_phu_luc(phu_luc)
            sources[phu_luc] = pl_chunks

        doc_chunks: list[dict] = []
        for source, source_chunks in sources.items():
            for chunk in source_chunks:
                path = write_chunk_file(doc_meta, chunk, source)
                record = {
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": doc_meta["doc_id"],
                    "so_hieu": doc_meta.get("so_hieu", ""),
                    "loai_chunk": chunk["loai"],
                    "so_dieu": chunk.get("so_dieu"),
                    "tieu_de": chunk["tieu_de"],
                    "chuong": chunk.get("chuong"),
                    "muc": chunk.get("muc"),
                    "trich_dan": citation(doc_meta, chunk),
                    "duong_dan": str(path.relative_to(ROOT)),
                    "nguon": str(source.relative_to(ROOT)),
                    "so_ky_tu": len(chunk["text"]),
                    "text": chunk["text"],
                }
                doc_chunks.append(record)
        doc_chunks.sort(key=lambda c: (c["loai_chunk"] != "mo-dau", c["chunk_id"]))
        all_chunks.extend(doc_chunks)

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
                "toan_van": str(toan_van.relative_to(ROOT)),
                "so_dieu": sum(1 for c in doc_chunks if c["loai_chunk"] == "dieu"),
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
        print(f"  - {doc['so_hieu']}: {doc['so_dieu']} Điều, {doc['so_chunk']} chunk")


def write_muc_luc(doc_dir: Path, doc_meta: dict, chunks: list[dict]) -> None:
    lines = [
        f"# Mục lục — {doc_meta.get('loai_van_ban', '')} số {doc_meta.get('so_hieu', '')}",
        "",
        f"*{doc_meta.get('tieu_de', '')}*",
        "",
        "> File này được sinh tự động bởi `tools/build_index.py` — đừng sửa tay.",
        "",
    ]
    chuong_hien_tai = object()
    for chunk in chunks:
        if chunk["loai_chunk"] == "mo-dau":
            continue
        if chunk["chuong"] != chuong_hien_tai:
            chuong_hien_tai = chunk["chuong"]
            lines += ["", f"## {chuong_hien_tai or 'Khác'}", ""]
        rel = Path("..") / ".." / ".." / chunk["duong_dan"]
        nhan = (
            f"Điều {chunk['so_dieu']}. {chunk['tieu_de']}"
            if chunk["loai_chunk"] == "dieu"
            else chunk["tieu_de"]
        )
        lines.append(f"- [{nhan}]({rel.as_posix()})")
    lines.append("")
    (doc_dir / "muc-luc.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
