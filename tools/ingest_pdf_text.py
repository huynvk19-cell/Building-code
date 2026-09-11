#!/usr/bin/env python3
"""Chuyển PDF **có lớp văn bản thật** thành Markdown cho corpus.

Khác `tools/ingest_pdf.py`: script kia dành cho bản SCAN, phải đọc từng ảnh
trang bằng thị giác máy rồi chép tay vì OCR đánh rơi dấu tiếng Việt. Script này
dành cho bản ký số do cơ quan phát hành — chữ nằm sẵn trong PDF, trích ra là
chính xác tuyệt đối, không qua OCR.

**Vẫn phải mở vài trang bằng thị giác máy để đối chiếu** trước khi tin kết quả:
một số PDF có lớp văn bản sai lệch so với hình in.

Việc script làm:
  - bỏ dòng lặp ở đầu/chân trang (tên cơ quan, chữ ký số, số trang trơ trọi);
  - nối các dòng bị ngắt giữa câu thành đoạn văn liền mạch;
  - nhận diện `Chương I` + tiêu đề chương, `Điều 12. Tên điều` và đánh dấu
    theo đúng quy ước tiêu đề mà `tools/build_index.py` cần.

Chạy:
    python3 tools/ingest_pdf_text.py <file.pdf> > /tmp/thu.md
    python3 tools/ingest_pdf_text.py <file.pdf> --phu-luc   # không tách Điều
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import pymupdf
except ImportError:
    sys.exit("Cần PyMuPDF: pip install pymupdf")

# Tiêu đề chương thường bị gom chung một đoạn với tên chương viết HOA.
RE_CHUONG = re.compile(r"^Chương\s+([IVXLC]+)\b\s*(.*)$")
# --- Cấu trúc "muc" của quy chuẩn: 1. TÊN PHẦN / 1.1 Tên mục / 1.1.1 nội dung
RE_PHAN_QC = re.compile(r"^(\d+)\.\s+([A-ZĐÀ-Ỹ][A-ZĐÀ-Ỹ\s,\-()/]{3,})$")
RE_MUC_QC = re.compile(r"^(\d+(?:\.\d+)+)\s+(\S.*)$")
# Số hiệu mục phải có ÍT NHẤT MỘT DẤU CHẤM ("1.1", "2.16.11.3"); số nguyên trơ
# chỉ mở đoạn khi có dấu chấm ngay sau ("1. QUY ĐỊNH CHUNG"). Không siết như vậy
# thì mọi dòng bị ngắt giữa câu mà rơi đúng vào một con số đều thành đoạn mới —
# câu "Một nhà tang lễ phục vụ tối đa" + "250 000 dân;" đã bị cắt làm đôi.
# Quy chuẩn mở đoạn bằng "1.1 " hoặc "1.1.1 " — KHÔNG có dấu chấm cuối số hiệu,
# khác hẳn nghị định ("1. ", "a) "). Dùng riêng cho chế độ --muc.
# Dấu chấm sau số hiệu là TÙY CHỌN: tiêu đề phần viết "1. QUY ĐỊNH CHUNG"
# còn mục con viết "1.1 Phạm vi" — thiếu `\.?` thì tiêu đề phần không mở đoạn
# mới và bị gộp vào đoạn trước, khiến cả cây cấu trúc không nhận được.
# Phần "Giải thích từ ngữ" đặt số hiệu ĐỨNG MỘT MÌNH trên dòng rồi mới tới
# thuật ngữ ở dòng sau, nên phải chấp nhận cả trường hợp không có gì phía sau
# số hiệu — thiếu nhánh `$` thì mất trọn 30 mục định nghĩa 1.4.1 đến 1.4.30.
RE_DAU_DOAN_QC = re.compile(r"^\s*(?:\d+\.\d+(?:\.\d+)*\.?(?:\s+|$)|\d+\.\s|CHÚ THÍCH|B[aả]ng\s+[A-Z]?\.?\d+(?:\.\d+)?[a-zA-Z]?\s*[:\-–—]\s|-\s)")
# Gạch đầu dòng "- " cũng mở đoạn mới: quy chuẩn trình bày phần lớn yêu cầu
# dưới dạng danh sách gạch đầu dòng, gộp cả danh sách vào một đoạn thì mục
# 1.5.3 thành một khối 1 400 ký tự không xuống dòng. Dòng NỐI TIẾP của một
# gạch đầu dòng luôn mở đầu bằng chữ thường nên không bị tách nhầm.
# Số hiệu mục ĐỨNG MỘT MÌNH trên dòng — phần "Giải thích từ ngữ" của
# QCVN 01:2021/BXD in "1.4.1" ở một dòng, thuật ngữ ở dòng kế, định nghĩa
# ở dòng sau nữa.
RE_SO_MUC_TRO = re.compile(r"^(\d+(?:\.\d+)+)\s*$")
# Ký tự đánh dấu "đoạn này ĐÃ ĐƯỢC XÁC ĐỊNH là tiêu đề mục" do `gom_doan` gắn.
# Cần có, vì `gom_doan` quyết định dựa trên DÒNG ĐƠN trong bản in còn
# `dinh_dang_muc` chỉ thấy đoạn ĐÃ NỐI — đo lại độ dài ở đó thì mọi tiêu đề dài
# quá một dòng đều bị loại (đã mất tên mục 2.6 và 2.12.4 vì lỗi này).
DAU_TIEU_DE = "\x00"
# Ký tự đánh dấu "đoạn này là TIÊU ĐỀ BẢNG".
DAU_BANG = "\x01"
# Tiêu đề bảng thật luôn có dấu ngăn sau số hiệu ("Bảng 2.1: Chỉ tiêu…",
# "Bảng G.9 – Hệ số…"). Câu viện dẫn "quy định tại Bảng 2.6;" hay dòng bị ngắt
# trang thành "Bảng 2.2. Đối với khu vực…" KHÔNG có dấu ngăn nên không lọt.
RE_TIEU_DE_BANG_QC = re.compile(
    r"^B[aả]ng\s+[A-Z]?\.?\d+(?:\.\d+)?[a-zA-Z]?\s*[:\-–—]\s*\S")
RE_DIEU = re.compile(r"^Điều\s+(\d+)\.\s*(.*)$")
# Tên điều đang dang dở khi kết thúc bằng dấu phẩy hoặc một từ nối/từ dẫn.
DANG_DO = re.compile(r"(?:,|\b(?:và|khoản|điểm|Điều|tên|của|số|tại|các))\s*$")


def bat_dau_thuong(s: str) -> bool:
    """Chuỗi có mở đầu bằng CHỮ THƯỜNG không?

    Không dùng dải ký tự `[a-zà-ỹ]`: dải đó tính theo mã Unicode nên nuốt trọn
    cả chữ HOA tiếng Việt — "Đ" là U+0110, "Ư" là U+01AF, "Ấ" là U+1EA4, đều
    nằm giữa "à" (U+00E0) và "ỹ" (U+1EF9). Hậu quả đã đo được: tiêu đề
    "1.2 Đối tượng áp dụng" bị coi là dòng nối tiếp và mất tên mục.
    `str.islower()` xử lý đúng theo bảng chữ Unicode.
    """
    return bool(s) and s[:1].islower()



def con_tiep(ten: str, dong_ke: str) -> bool:
    """Tên điều có bị ngắt dòng và còn nối tiếp ở dòng kế không?

    Ba tín hiệu, thử lần lượt:
      1. dòng kế bắt đầu bằng CHỮ THƯỜNG  → chắc chắn là phần nối tiếp
         ("...ngày 19 tháng 6" + "năm 2026 của Chính phủ...");
      2. tên kết thúc bằng dấu phẩy hoặc từ nối ("khoản", "điểm", "và"…);
      3. tên kết thúc bằng CHỮ SỐ *và* dòng kế mở đầu bằng "Điều"
         ("...điểm c khoản 1" + "Điều 44").

    Không dùng riêng "kết thúc bằng chữ số" làm tín hiệu, vì rất nhiều tên điều
    trọn vẹn kết thúc đúng như vậy ("Sửa đổi, bổ sung khoản 5 Điều 31").
    """
    ke = dong_ke.strip()
    if not ke or ke.startswith(("“", '"', "1.", "a)")) or RE_DIEU.match(ke):
        return bool(re.search(r"\d\s*$", ten)) and ke.startswith("Điều")
    if bat_dau_thuong(ke):
        return True
    if DANG_DO.search(ten):
        return True
    return bool(re.search(r"\d\s*$", ten)) and ke.startswith("Điều")
# Dòng rác lặp trên mọi trang của bản ký số.
RE_RAC = re.compile(
    r"^(?:\d{1,3}|Cơ quan phát hành:.*|Người ký:.*|Email:.*|Cơ quan:.*"
    r"|Thời gian ký:.*|CHÍNH PHỦ|_+"
    # Tiêu đề chạy của bản Công báo, lặp ở MỌI trang. Không lọc thì nó nằm
    # lọt giữa câu sau khi nối dòng ("…đảm bảo CÔNG BÁO/Số 599 + 600/Ngày
    # 31-5-2021 QCVN 01:2021/BXD quy định…") — corpus của QCVN 04:2021/BXD
    # đã dính 18 chỗ như vậy. Neo trọn dòng nên số hiệu quy chuẩn nằm GIỮA
    # câu văn không bị đụng tới.
    r"|CÔNG BÁO/.*|QCVN\s+\d+(?:-\d+)?:\d{4}/[A-ZĐ]+)$"
)
# Dòng mở đầu một đoạn mới: "1. ", "a) ", "“1. ", "Chương", "Điều"…
RE_DAU_DOAN = re.compile(
    r"^\s*(?:[“\"]?\d+\.\s|[“\"]?[a-zđ]\)\s|[“\"]?\d+\.\d+\.\s|Chương\s|Điều\s|Mẫu\s"
    r"|Phụ lục\s|Căn cứ\s|Theo đề nghị\s|Chính phủ ban hành\s)"
)


def doc_text(pdf: Path) -> list[str]:
    doc = pymupdf.open(pdf)
    dong: list[str] = []
    for page in doc:
        for l in page.get_text().splitlines():
            l = l.rstrip()
            if not l.strip() or RE_RAC.match(l.strip()):
                continue
            dong.append(l)
    return dong


def la_tieu_de_muc(con_lai: str) -> bool:
    """Phần chữ đứng sau số hiệu mục có phải TIÊU ĐỀ, hay đã là thân điều khoản?

    Ba dấu hiệu loại trừ, mỗi dấu hiệu đều từ một lỗi có thật:
      - dài quá 80 ký tự  → đã là câu quy định, không phải tiêu đề;
      - kết thúc bằng "." hoặc ";" → câu trọn vẹn, không phải tiêu đề;
      - bắt đầu bằng CHỮ THƯỜNG → đây là dòng NỐI TIẾP của câu trước bị ngắt
        trang, không phải mục mới. Chính dấu hiệu này chặn câu "...quy định từ
        điểm 2.7.3 đến điểm 2.7.7 dưới đây;" sinh ra một mục 2.7.3 giả nằm
        ngay trước mục 2.7.3 thật.
    Dấu hai chấm cuối được chấp nhận và cắt bỏ: quy chuẩn hay viết
    "1.5.1 Yêu cầu về dự báo trong đồ án quy hoạch:".
    """
    if not con_lai or len(con_lai) > 80:
        return False
    if con_lai.endswith((".", ";")):
        return False
    return not bat_dau_thuong(con_lai)


def gom_doan(dong: list[str], dau_doan: re.Pattern | None = None,
             tach_tieu_de_muc: bool = False) -> list[str]:
    """Nối dòng bị ngắt giữa câu; giữ nguyên ranh giới đoạn.

    `dau_doan` cho phép truyền quy tắc nhận biết đầu đoạn riêng: nghị định và
    quy chuẩn đánh số khác nhau ("1. " so với "1.1 "), dùng chung một quy tắc
    thì quy chuẩn sẽ bị gom cả tiêu đề lẫn thân vào một đoạn.

    `tach_tieu_de_muc` dành cho quy chuẩn: trong bản in, tiêu đề mục là MỘT
    DÒNG RIÊNG ("1.1 Phạm vi điều chỉnh") và thân bắt đầu ở dòng kế. Nối hai
    dòng đó rồi mới tách thì không còn ranh giới nào để tách — tiêu đề bị nuốt
    trọn vào thân và mọi mục đều mất tên. Đây là ràng buộc y hệt ràng buộc đã
    phải đặt cho tên Điều của nghị định.
    """
    dau_doan = dau_doan or RE_DAU_DOAN
    doan: list[str] = []
    dem: list[str] = []
    bo_qua: set[int] = set()

    def chot():
        if dem:
            doan.append(" ".join(x.strip() for x in dem).strip())
            dem.clear()

    gom_tieu_de = False
    for idx, l in enumerate(dong):
        if idx in bo_qua:
            continue
        st = l.strip()
        ke = dong[idx + 1] if idx + 1 < len(dong) else ""
        if tach_tieu_de_muc:
            def thu_tieu_de(so: str, ten: str, tu: int):
                """Dựng tiêu đề mục, nối các dòng nó tràn sang — hoặc từ chối.

                Tiêu đề dài bị bản in ngắt giữa chừng ("…bố cục các công" +
                "trình đối với các khu vực phát triển mới"), và dòng nối tiếp
                luôn mở đầu bằng chữ thường. Nhưng chỉ dựa vào dấu hiệu đó thì
                nối vô hạn: điều khoản KHÔNG CÓ TÊN như mục 3.1 cũng mở đầu
                bằng chữ hoa rồi chạy suốt nhiều câu, và đã bị nuốt trọn 496 ký
                tự vào tiêu đề. Vì vậy dựng xong phải KIỂM TRA LẠI: quá 120 ký
                tự, hoặc kết thúc bằng dấu chấm câu, thì đó là thân điều khoản
                chứ không phải tên mục — trả về None để dòng được xử lý bình
                thường.
                """
                j, het = tu, []
                while j + 1 < len(dong) and bat_dau_thuong(dong[j + 1].strip()):
                    j += 1
                    ten = f"{ten} {dong[j].strip()}"
                    het.append(j)
                ten = ten.rstrip(":").strip()
                if len(ten) > 120 or ten.endswith((".", ";")):
                    return None
                return f"{so} {ten}", het

            if RE_TIEU_DE_BANG_QC.match(st):
                # Tiêu đề bảng phải đứng riêng một dòng, nếu không nó dính liền
                # phần chữ trong ô bảng và `tools/chen_anh_bang.py` không nhận
                # ra để gắn ảnh.
                chot()
                ten, j = st, idx
                while j + 1 < len(dong) and bat_dau_thuong(dong[j + 1].strip()):
                    j += 1
                    ten = f"{ten} {dong[j].strip()}"
                    bo_qua.add(j)
                doan.append(DAU_BANG + ten)
                continue

            kq = None
            m = RE_SO_MUC_TRO.match(st)
            if m:
                # Số hiệu trơ: thuật ngữ nằm ở dòng kế, lấy làm tiêu đề.
                ke_st = ke.strip()
                chot()
                if la_tieu_de_muc(ke_st):
                    kq = thu_tieu_de(m.group(1), ke_st, idx + 1)
                if kq:
                    doan.append(DAU_TIEU_DE + kq[0])
                    bo_qua.update(kq[1])
                    bo_qua.add(idx + 1)
                else:
                    doan.append(m.group(1))
                continue
            m = RE_MUC_QC.match(st)
            if m and la_tieu_de_muc(m.group(2).strip()):
                kq = thu_tieu_de(m.group(1), m.group(2).strip(), idx)
                if kq:
                    chot()
                    doan.append(DAU_TIEU_DE + kq[0])
                    bo_qua.update(kq[1])
                    continue
        if RE_DIEU.match(st):
            chot()
            dem.append(l)
            if con_tiep(st, ke):
                gom_tieu_de = True      # tên điều bị ngắt dòng, còn nối tiếp
            else:
                chot()
            continue
        if gom_tieu_de:
            dem.append(l)
            if not con_tiep(" ".join(x.strip() for x in dem), ke):
                chot()
                gom_tieu_de = False
            continue
        if dau_doan.match(l) or RE_CHUONG.match(st):
            chot()
        dem.append(l)
        # Đoạn kết thúc rõ ràng bằng dấu chấm + ngoặc kép đóng.
        if l.rstrip().endswith(("”.", '".')):
            chot()
    chot()
    return doan


LA_MA = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV"]


def dinh_dang(doan: list[str], la_phu_luc: bool) -> list[str]:
    """Nhận diện tiêu đề Chương/Điều.

    Ràng buộc then chốt: **số Chương và số Điều phải tăng liên tiếp**. Không có
    ràng buộc này thì mọi DẪN CHIẾU CHÉO trong thân văn bản đều bị nhận nhầm
    thành tiêu đề — đã gặp thật: câu "...tên Chương III; tên Điều 23..." của
    Điều 8 sinh ra một "Chương III" giả, và "khoản 4 Điều 42." sinh ra một
    "Điều 42" giả nằm lọt giữa Điều 9.
    """
    ra: list[str] = []
    cho_chuong = 0   # chỉ số chương kế tiếp trong LA_MA
    cho_dieu = 1     # số Điều kế tiếp
    i = 0
    while i < len(doan):
        d = doan[i]
        m = RE_CHUONG.match(d.strip())
        if m and not la_phu_luc and cho_chuong < len(LA_MA) \
                and m.group(1) == LA_MA[cho_chuong]:
            cho_chuong += 1
            ten = re.sub(r"\s+", " ", m.group(2)).strip()
            j = i + 1
            # Tên chương có thể tràn sang đoạn sau nếu bị ngắt trang.
            while not ten and j < len(doan) and not RE_DIEU.match(doan[j]):
                ten = re.sub(r"\s+", " ", doan[j]).strip()
                j += 1
            ra += ["", f"## Chương {m.group(1)}. {ten}", ""]
            i = j
            continue
        m = RE_DIEU.match(d)
        if m and not la_phu_luc and int(m.group(1)) == cho_dieu:
            cho_dieu += 1
            so, ten = m.group(1), m.group(2).strip()
            if "“" in ten:
                ten, phan_du = ten.split("“", 1)
                doan.insert(i + 1, "“" + phan_du)
                ten = ten.strip()
            # Tên điều có thể tràn sang đoạn sau nếu chưa kết thúc bằng dấu câu.
            # Tên điều bị ngắt dòng thì nối tiếp; NHƯNG phải dừng khi gặp nội
            # dung được sửa đổi (mở bằng dấu ngoặc kép “), và chỉ nối khi tên
            # thật sự đang DANG DỞ. Không có điều kiện "dang dở" thì tên điều
            # nuốt luôn phần thân — đã gặp thật với Điều 38: tên hút mất câu
            # "Bãi bỏ điểm i, điểm k khoản 2..." làm thân chunk rỗng và bị loại.
            while (ten and not ten.endswith((".", ":")) and DANG_DO.search(ten)
                   and i + 1 < len(doan)):
                ke = doan[i + 1].strip()
                if RE_DIEU.match(ke) or ke.startswith(("1.", "“", '"', "a)")):
                    break
                ten = f"{ten} {ke}"
                i += 1
            ra += ["", f"### Điều {so}. {ten.rstrip('.').strip()}", ""]
            i += 1
            continue
        ra.append(re.sub(r"\s+", " ", d).strip())
        ra.append("")
        i += 1
    return ra


def hop_le_tiep(cu: tuple[int, ...], moi: tuple[int, ...]) -> bool:
    """Số hiệu `moi` có đứng ngay sau `cu` trong một dàn bài hợp lệ không?

    Chỉ hai bước hợp lệ:
      - xuống một cấp, bắt đầu từ 1   (2.9.3 → 2.9.3.1);
      - tăng 1 ở một cấp bất kỳ rồi dừng  (2.9.3.4 → 2.9.4, 1.4.30 → 1.5).

    Ràng buộc này chặt hơn "phải tăng dần" và cần đúng mức đó: bảng chiều rộng
    đường của QCVN 01:2021/BXD có ô "2.400 - 4 000", và quy tắc tăng dần đã
    nhận nó thành mục 2.400 rồi chặn mất toàn bộ 67 mục còn lại của phần 2.
    """
    if not cu:
        return True
    if len(moi) == len(cu) + 1 and moi[:-1] == cu and moi[-1] == 1:
        return True
    k = len(moi) - 1
    return k < len(cu) and moi[:k] == cu[:k] and moi[k] == cu[k] + 1


def dinh_dang_muc(doan: list[str]) -> list[str]:
    """Cấu trúc quy chuẩn: "1. QUY ĐỊNH CHUNG" / "1.1 Phạm vi" / "1.1.1 nội dung".

    Ràng buộc chống nhận nhầm dẫn chiếu chéo: số phần phải tăng liên tiếp, và
    số mục phải thuộc đúng phần đang mở. Trong quy chuẩn, dẫn chiếu kiểu
    "quy định tại 2.4.1" nằm GIỮA câu nên đã bị loại sẵn nhờ neo đầu dòng;
    ràng buộc số thứ tự chặn nốt các trường hợp dòng thân bắt đầu bằng số.

    Mục cấp N.M vừa có thể là TIÊU ĐỀ ("2.1 Yêu cầu chung") vừa có thể mang
    luôn nội dung. Phân biệt bằng: tiêu đề thì ngắn và không kết thúc bằng dấu
    chấm câu.
    """
    ra: list[str] = []
    cho_phan = 1
    da_nhan: tuple[int, ...] = ()
    for d in doan:
        da_biet_tieu_de = d.startswith(DAU_TIEU_DE)
        if d.startswith(DAU_BANG):
            ten_bang = re.sub(r"\s+", " ", d[1:]).strip()
            ra += ["", f"**{ten_bang}**", ""]
            continue
        st = d.lstrip(DAU_TIEU_DE).strip()
        m = RE_PHAN_QC.match(st)
        if m and int(m.group(1)) == cho_phan:
            cho_phan += 1
            da_nhan = ()
            ra += ["", f"## {m.group(1)} {m.group(2).strip()}", ""]
            continue
        m = RE_MUC_QC.match(st) or RE_SO_MUC_TRO.match(st)
        if m and int(m.group(1).split(".")[0]) < cho_phan:
            so = m.group(1)
            con_lai = (m.group(2).strip() if m.re is RE_MUC_QC else "")
            # Dòng thân bị ngắt trang có thể mở đầu bằng số hiệu mục
            # ("...từ điểm 2.7.3" xuống dòng thành "2.7.3 đến điểm 2.7.7
            # dưới đây;"). Chữ thường ngay sau số hiệu là dấu hiệu chắc chắn
            # của phần NỐI TIẾP, không phải mục mới.
            if con_lai and bat_dau_thuong(con_lai):
                ra += [re.sub(r"\s+", " ", st), ""]
                continue
            khoa = tuple(int(x) for x in so.split("."))
            if not hop_le_tiep(da_nhan, khoa):
                ra += [re.sub(r"\s+", " ", st), ""]
                continue
            da_nhan = khoa
            if not con_lai:
                ra += ["", f"### {so}", ""]
            elif da_biet_tieu_de or la_tieu_de_muc(con_lai):
                ra += ["", f"### {so} {con_lai.rstrip(':').strip()}", ""]
            else:
                ra += ["", f"### {so}", "", con_lai, ""]
            continue
        ra += [re.sub(r"\s+", " ", st), ""]
    return ra


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--phu-luc", action="store_true",
                    help="phụ lục: không tách Chương/Điều, chỉ làm sạch đoạn")
    ap.add_argument("--muc", action="store_true",
                    help="quy chuẩn: tách theo 1. PHẦN / 1.1 mục / 1.1.1 điều khoản")
    args = ap.parse_args()

    if not args.pdf.exists():
        sys.exit(f"Không thấy tệp: {args.pdf}")
    doan = gom_doan(doc_text(args.pdf),
                    RE_DAU_DOAN_QC if args.muc else None,
                    tach_tieu_de_muc=args.muc)
    out = dinh_dang_muc(doan) if args.muc else dinh_dang(doan, args.phu_luc)
    text = "\n".join(out)
    print(re.sub(r"\n{3,}", "\n\n", text).strip())


if __name__ == "__main__":
    main()
