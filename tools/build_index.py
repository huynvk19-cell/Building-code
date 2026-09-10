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
# "### 1.1 Phạm vi điều chỉnh" — phần tiêu đề là TÙY CHỌN, vì nhiều quy chuẩn
# đánh số điều khoản mà không đặt tên (ví dụ QCVN 06:2022/BXD mục 4.1 đến 4.35).
# Khi không có tiêu đề, tiêu đề hiển thị được suy ra từ câu đầu của điều khoản —
# đây chỉ là NHÃN để tra cứu, không phải nội dung pháp lý.
# Số hiệu mục, tiêu đề TÙY CHỌN. Hậu tố chữ cái ("1.4.21a") là cách QCVN
# đánh số một điểm được CHÈN THÊM giữa hai điểm cũ — gặp nhiều ở các bản sửa đổi.
RE_MUC_SO = re.compile(r"^###\s+(\d+(?:\.\d+)*[a-z]?)(?:\s+(.+?))?\s*$")

# --- Phụ lục ----------------------------------------------------------------
RE_H2 = re.compile(r"^##\s+(.+?)\s*$")
# Số hiệu mục trong phụ lục: "D.5", "A.1.2.1", "H.2.12.10"…
RE_SO_PHU_LUC = re.compile(r"[A-Z]\.\d+(?:\.\d+)*[a-z]?")

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


def nhan_tu_cau_dau(text: str, gioi_han: int = 70) -> str:
    """Suy một NHÃN ngắn từ câu đầu của điều khoản không có tên trong bản gốc.

    Nhãn này chỉ dùng để hiển thị và tìm kiếm. Trích dẫn pháp lý vẫn dựa vào số
    hiệu mục (ví dụ "mục 4.17 QCVN 06:2022/BXD"), không dựa vào nhãn này.
    """
    for dong in text.splitlines():
        dong = dong.strip()
        if not dong or dong.startswith(("|", ">", "!", "#", "-", "*")):
            continue
        dong = re.sub(r"\*\*|\*|`", "", dong)
        dong = re.sub(r"^\d+(?:\.\d+)*\s*", "", dong).strip()
        if not dong:
            continue
        cau = re.split(r"(?<=[.;:])\s", dong)[0]
        if len(cau) > gioi_han:
            cau = cau[:gioi_han].rsplit(" ", 1)[0] + "…"
        return cau
    return "(không tên)"


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
            if not self.current.get("tieu_de"):
                self.current["tieu_de"] = nhan_tu_cau_dau(text)
                if not self.current.get("slug", "").strip("-"):
                    so = self.current.get("so_hieu_muc") or ""
                    self.current["slug"] = (
                        f"muc-{so.replace('.', '-')}-{slugify(self.current['tieu_de'])}"
                    )
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
    # Tên mục cha gần nhất theo từng độ sâu, để điều khoản con thừa hưởng ngữ
    # cảnh. Ví dụ mục 3.2.9 sẽ mang muc="3.2 Lối ra thoát nạn và lối ra khẩn
    # cấp" — nhờ đó một điều khoản ngắn vẫn tìm được bằng từ khoá của mục cha.
    ten_muc_cha: dict[int, str] = {}

    for line in body.splitlines():
        m = RE_MUC_SO.match(line)
        if m:
            so, tieu_de = m.group(1), m.group(2)
            if not tieu_de:
                # Điều khoản không có tên trong bản gốc: chốt chunk đang mở rồi
                # đặt chỗ, tiêu đề sẽ suy từ câu đầu tiên khi flush.
                tieu_de = ""
            order += 1
            sau = so.count(".") + 1
            if tieu_de:
                ten_muc_cha[sau] = f"{so} {tieu_de}"
            for k in list(ten_muc_cha):
                if k >= sau and not (k == sau and tieu_de):
                    if k > sau:
                        del ten_muc_cha[k]
            cha = next(
                (ten_muc_cha[k] for k in sorted(ten_muc_cha, reverse=True) if k < sau),
                None,
            )
            builder.start(
                chunk_id=f"{doc_id}:muc-{so}",
                loai="muc",
                so_hieu_muc=so,
                sap_xep=(1,) + sort_key(so),
                tieu_de=tieu_de,
                chuong=phan,
                muc=cha,
                slug=f"muc-{so.replace('.', '-')}-{slugify(tieu_de)}",
            )
            continue

        m = RE_PHAN.match(line)
        if m:
            so, tieu_de = m.group(1), m.group(2)
            phan = f"{so} {tieu_de}" if so else tieu_de
            ten_muc_cha.clear()
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
                elif RE_SO_PHU_LUC.fullmatch(dau):
                    # Điều khoản KHÔNG CÓ TÊN trong bản gốc (ví dụ "## D.5"). Trước đây
                    # so_muc bị bỏ trống nên không ghép được với bản sửa đổi.
                    so_muc = dau
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
    # "Sửa đổi 1:2023 QCVN 06:2022/BXD" tự nó đã là tên đầy đủ — thêm "Quy chuẩn
    # kỹ thuật quốc gia (bản sửa đổi) số ..." vào trước sẽ thành một chuỗi vô nghĩa.
    la_quy_chuan = so_hieu.startswith(("QCVN", "TCVN", "Sửa đổi"))
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
        "ngay_hieu_luc": doc_meta.get("ngay_hieu_luc", "CHƯA XÁC ĐỊNH"),
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


def noi_sua_doi(all_chunks: list[dict], documents: list[dict]) -> int:
    """Gắn cờ cho những chunk của văn bản GỐC đã bị một văn bản SỬA ĐỔI đụng tới.

    Một bản sửa đổi (ví dụ Sửa đổi 1:2023 QCVN 06:2022/BXD) khai `sua_doi_cho`
    trong front matter và cắt chunk theo đúng số hiệu mục mà nó sửa. Nhờ vậy có
    thể ghép hai bên theo `so_hieu_muc`.

    Việc này quan trọng vì kho giữ NGUYÊN VĂN bản gốc — không được sửa chữ trong
    đó. Nếu không có cờ này, người tra mục 3.2.8 sẽ đọc bản 2022 và tưởng đó là
    quy định đang có hiệu lực, trong khi nó đã bị thay từ 01/12/2023.
    """
    # doc_id bản sửa đổi -> số hiệu của văn bản gốc mà nó sửa
    sua_cho: dict[str, str] = {}
    for doc in documents:
        goc = doc.get("_sua_doi_cho") or []
        if goc:
            sua_cho[doc["doc_id"]] = goc[0]

    if not sua_cho:
        return 0

    # (số hiệu văn bản gốc, số hiệu mục) -> danh sách chunk sửa đổi
    ban_do: dict[tuple[str, str], list[dict]] = {}
    for c in all_chunks:
        goc = sua_cho.get(c["doc_id"])
        if goc and c.get("so_hieu_muc"):
            ban_do.setdefault((goc, c["so_hieu_muc"]), []).append(c)

    def to_hon(so: str) -> list[str]:
        """'A.1.2.1' -> ['A.1.2.1', 'A.1.2', 'A.1'] — từ hẹp tới rộng."""
        phan = so.split(".")
        return [".".join(phan[: i + 1]) for i in range(len(phan) - 1, 0, -1)]

    # Bản gốc có thể cắt THÔ hơn bản sửa đổi: sửa đổi nhắm A.1.2.1 nhưng bản gốc
    # chỉ có một chunk A.1. Khi đó gắn cờ vào chunk cha gần nhất, để người tra A.1
    # vẫn thấy cảnh báo. Không làm ngược lại (không kéo cờ xuống các mục con).
    co_san = {(c["so_hieu"], c["so_hieu_muc"]) for c in all_chunks if c.get("so_hieu_muc")}
    for (goc_so, so), hits in list(ban_do.items()):
        if (goc_so, so) in co_san:
            continue
        for cha in to_hon(so):
            if (goc_so, cha) in co_san:
                ban_do.setdefault((goc_so, cha), []).extend(hits)
                break

    dem = 0
    for c in all_chunks:
        if c["doc_id"] in sua_cho or not c.get("so_hieu_muc"):
            continue
        hits = ban_do.get((c["so_hieu"], c["so_hieu_muc"]))
        if not hits:
            continue
        c["sua_doi_boi"] = [
            {
                "so_hieu": h["so_hieu"],
                "chunk_id": h["chunk_id"],
                "ngay_hieu_luc": h["ngay_hieu_luc"],
                "duong_dan": h["duong_dan"],
            }
            for h in hits
        ]
        dem += 1
    return dem


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
                        "ngay_ban_hanh": doc_meta.get("ngay_ban_hanh", ""),
                        "ngay_hieu_luc": doc_meta.get("ngay_hieu_luc", "CHƯA XÁC ĐỊNH"),
                        "het_hieu_luc": doc_meta.get("het_hieu_luc", ""),
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
                "ngay_hieu_luc": doc_meta.get("ngay_hieu_luc", "CHƯA XÁC ĐỊNH"),
                "can_cu_hieu_luc": doc_meta.get("can_cu_hieu_luc", ""),
                "thay_the": doc_meta.get("thay_the", []),
                "het_hieu_luc": doc_meta.get("het_hieu_luc", ""),
                "sua_doi_boi": doc_meta.get("sua_doi_boi", []),
                "dieu_khoan_chuyen_tiep": doc_meta.get("dieu_khoan_chuyen_tiep", ""),
                "linh_vuc": doc_meta.get("linh_vuc", []),
                "nguon": doc_meta.get("nguon", ""),
                "cau_truc": doc_meta.get("cau_truc", "dieu"),
                "sua_doi_cho": doc_meta.get("sua_doi_cho", []),
                "_sua_doi_cho": doc_meta.get("sua_doi_cho", []),
                "toan_van": str(toan_van.relative_to(ROOT)),
                "so_don_vi": don_vi,
                "so_chunk": len(doc_chunks),
            }
        )
        write_muc_luc(doc_dir, doc_meta, doc_chunks)

    da_gan = noi_sua_doi(all_chunks, documents)
    for doc in documents:
        doc.pop("_sua_doi_cho", None)

    with (INDEX / "chunks.jsonl").open("w", encoding="utf-8") as fh:
        for record in all_chunks:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    (INDEX / "documents.json").write_text(
        json.dumps(documents, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Đã xử lý {len(documents)} văn bản, {len(all_chunks)} chunk.")
    if da_gan:
        print(f"  ⚠ {da_gan} chunk của văn bản gốc đã được gắn cờ ĐÃ BỊ SỬA ĐỔI.")
    for doc in documents:
        don_vi = "Điều" if doc["cau_truc"] == "dieu" else "mục"
        print(f"  - {doc['so_hieu']}: {doc['so_don_vi']} {don_vi}, {doc['so_chunk']} chunk")


if __name__ == "__main__":
    main()
