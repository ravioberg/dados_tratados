# -*- coding: utf-8 -*-
"""
Injeta Pagina 2 (Perfil Socioeconomico) em socioeconomico.pbix criado pelo PBI Desktop.
Usa binary patching — apenas o Report/Layout e alterado; todos os outros bytes
(DataModel, SecurityBindings, etc.) sao copiados exatamente como o PBI criou.
"""
import struct, zipfile, zlib, json, uuid
from pathlib import Path

BASE = Path(__file__).parent
SRC  = BASE / "socioeconomico.pbix"        # arquivo criado pelo PBI Desktop (blank)
OUT  = BASE / "dashboard_socioeconomico.pbix"

assert SRC.exists(), "socioeconomico.pbix nao encontrado!"

# ── helpers visuais ───────────────────────────────────────────────────────────
def uid(): return uuid.uuid4().hex[:16]

def pos(w, h, tab=0):
    return [{"id": 0, "position": {"x": 0, "y": 0, "z": 0,
             "width": w, "height": h, "tabOrder": tab}}]

def vc(x, y, z, w, h, cfg):
    return {"x": x, "y": y, "z": z, "width": w, "height": h,
            "config": json.dumps(cfg, ensure_ascii=False), "filters": "[]"}

def textbox(text, w, h, bold=False, size=14, color="#212121"):
    style = {"fontSize": f"{size}px", "color": color}
    if bold: style["fontWeight"] = "bold"
    return {"name": uid(), "layouts": pos(w, h),
            "singleVisual": {"visualType": "textbox",
                "objects": {"general": [{"properties": {"paragraphs": [
                    {"textRuns": [{"value": text, "textStyle": style}],
                     "horizontalTextAlignment": "left"}]}}]}}}

def card(tbl, msr, title, w, h):
    ref = f"{tbl}.{msr}"
    return {"name": uid(), "layouts": pos(w, h), "singleVisual": {
        "visualType": "card",
        "projections": {"Values": [{"queryRef": ref, "active": False}]},
        "prototypeQuery": {"Version": 2,
            "From": [{"Name": "t", "Entity": tbl, "Type": 0}],
            "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}},
                                    "Property": msr}, "Name": ref}]},
        "vcObjects": {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
            "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}}],
            "labels": [{"properties": {
                "fontSize": {"expr": {"Literal": {"Value": "24D"}}}}}]}}}

def col_chart(cat_tbl, cat_col, msr_tbl, msr, title, w, h, sort_col=None):
    select = [
        {"Column": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": cat_col},
         "Name": f"{cat_tbl}.{cat_col}"},
        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": msr},
         "Name": f"{msr_tbl}.{msr}"}]
    proto = {"Version": 2,
             "From": [{"Name": "a", "Entity": cat_tbl, "Type": 0},
                      {"Name": "m", "Entity": msr_tbl, "Type": 0}],
             "Select": select}
    if sort_col:
        proto["OrderBy"] = [{"Direction": 1, "Expression": {
            "Column": {"Expression": {"SourceRef": {"Source": "a"}},
                       "Property": sort_col}}}]
    return {"name": uid(), "layouts": pos(w, h), "singleVisual": {
        "visualType": "clusteredColumnChart",
        "projections": {
            "Category": [{"queryRef": f"{cat_tbl}.{cat_col}", "active": False}],
            "Y":        [{"queryRef": f"{msr_tbl}.{msr}",    "active": False}]},
        "prototypeQuery": proto,
        "vcObjects": {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}}}]}}}

def donut(cat_tbl, cat_col, msr_tbl, msr, title, w, h):
    return {"name": uid(), "layouts": pos(w, h), "singleVisual": {
        "visualType": "donutChart",
        "projections": {
            "Category": [{"queryRef": f"{cat_tbl}.{cat_col}", "active": False}],
            "Y":        [{"queryRef": f"{msr_tbl}.{msr}",    "active": False}]},
        "prototypeQuery": {"Version": 2,
            "From": [{"Name": "a", "Entity": cat_tbl, "Type": 0},
                     {"Name": "m", "Entity": msr_tbl, "Type": 0}],
            "Select": [
                {"Column": {"Expression": {"SourceRef": {"Source": "a"}},
                            "Property": cat_col}, "Name": f"{cat_tbl}.{cat_col}"},
                {"Measure": {"Expression": {"SourceRef": {"Source": "m"}},
                             "Property": msr}, "Name": f"{msr_tbl}.{msr}"}]},
        "vcObjects": {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}}}]}}}

def stacked(cat_tbl, cat_col, ser_col, msr_tbl, msr, title, w, h, sort_col=None):
    from_list = [{"Name": "a", "Entity": cat_tbl, "Type": 0},
                 {"Name": "m", "Entity": msr_tbl, "Type": 0}]
    select = [
        {"Column": {"Expression": {"SourceRef": {"Source": "a"}},
                    "Property": cat_col}, "Name": f"{cat_tbl}.{cat_col}"},
        {"Column": {"Expression": {"SourceRef": {"Source": "a"}},
                    "Property": ser_col}, "Name": f"{cat_tbl}.{ser_col}"},
        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}},
                     "Property": msr}, "Name": f"{msr_tbl}.{msr}"}]
    proto = {"Version": 2, "From": from_list, "Select": select}
    if sort_col:
        proto["OrderBy"] = [{"Direction": 1, "Expression": {
            "Column": {"Expression": {"SourceRef": {"Source": "a"}},
                       "Property": sort_col}}}]
    return {"name": uid(), "layouts": pos(w, h), "singleVisual": {
        "visualType": "stackedColumnChart",
        "projections": {
            "Category": [{"queryRef": f"{cat_tbl}.{cat_col}", "active": False}],
            "Series":   [{"queryRef": f"{cat_tbl}.{ser_col}", "active": False}],
            "Y":        [{"queryRef": f"{msr_tbl}.{msr}",     "active": False}]},
        "prototypeQuery": proto,
        "vcObjects": {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}}}]}}}

def slicer(tbl, col, title, w, h):
    return {"name": uid(), "layouts": pos(w, h), "singleVisual": {
        "visualType": "slicer",
        "projections": {"Values": [{"queryRef": f"{tbl}.{col}", "active": False}]},
        "prototypeQuery": {"Version": 2,
            "From": [{"Name": "a", "Entity": tbl, "Type": 0}],
            "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "a"}},
                                   "Property": col}, "Name": f"{tbl}.{col}"}]},
        "vcObjects": {"title": [{"properties": {
            "show": {"expr": {"Literal": {"Value": "true"}}},
            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}}}]}}}

# ── montar Pagina 2 ───────────────────────────────────────────────────────────
containers = []
z_order = 1

def add(x, y, w, h, cfg):
    global z_order
    containers.append(vc(x, y, z_order, w, h, cfg))
    z_order += 1

add(158,  5, 1112, 38, textbox("Perfil Socioeconômico dos Alunos — IRMR", 1112, 38, bold=True, size=20, color="#0D47A1"))
add(158, 45, 1112, 26, textbox("Distribuição por renda, instituição e escolaridade  ·  n = 143", 1112, 26, size=11, color="#616161"))
add(158,  80,  220, 85, card("_Medidas", "AlunosBaixaRenda",  "Alunos até 3 SM",        220, 85))
add(388,  80,  220, 85, card("_Medidas", "PctBaixaRenda",     "% Baixa renda (<=3 SM)", 220, 85))
add(618,  80,  220, 85, card("_Medidas", "PctEscolaPublica",  "% Escola pública",       220, 85))
add(158, 174,  580, 198, col_chart("Alunos", "FaixaRenda", "_Medidas", "TotalAlunos",
    "Renda familiar (em salários mínimos)", 580, 198, sort_col="FaixaRendaOrdem"))
add(748, 174,  522, 198, donut("Alunos", "TipoInstituicao", "_Medidas", "TotalAlunos",
    "Tipo de instituição de ensino", 522, 198))
add(158, 380, 1112, 152, stacked("Alunos", "FaixaRenda", "TipoInstituicao", "_Medidas", "TotalAlunos",
    "Renda familiar × Tipo de instituição", 1112, 152, sort_col="FaixaRendaOrdem"))
add(158, 540,  546, 172, col_chart("Alunos", "AnoEscolar", "_Medidas", "TotalAlunos",
    "Nível de escolaridade", 546, 172, sort_col="AnoEscolarOrdem"))
add(714, 540,  556, 172, stacked("Alunos", "FaixaRenda", "TipoDeficiencia", "_Medidas", "PctSobreTotal",
    "Renda familiar × Tipo de deficiência", 556, 172, sort_col="FaixaRendaOrdem"))
add(  5,  80,  148, 260, slicer("Alunos", "FaixaRenda",      "Renda",        148, 260))
add(  5, 348,  148, 110, slicer("Alunos", "TipoInstituicao", "Instituição",  148, 110))
add(  5, 466,  148, 130, slicer("Alunos", "FaixaEtaria",     "Faixa Etária", 148, 130))

pagina2 = {
    "id": 1, "name": uid(), "displayName": "Perfil Socioeconômico",
    "filters": "[]", "ordinal": 1, "visualContainers": containers,
    "config": "{}", "displayOption": 1, "width": 1280, "height": 720
}

# ── binary patching ───────────────────────────────────────────────────────────
print(f"Fonte: {SRC.name}  ({SRC.stat().st_size // 1024} KB)")

with open(SRC, "rb") as f:
    orig = bytearray(f.read())

with zipfile.ZipFile(SRC, "r") as z:
    info     = z.getinfo("Report/Layout")
    raw_json = z.read("Report/Layout")

layout = json.loads(raw_json.decode("utf-16-le"))
print(f"Layout original: {len(layout['sections'])} pagina(s)")
layout["sections"].append(pagina2)

new_json_bytes  = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")
comp = zlib.compressobj(6, zlib.DEFLATED, -15)
new_compressed  = comp.compress(new_json_bytes) + comp.flush()
new_crc         = zlib.crc32(new_json_bytes) & 0xFFFFFFFF
new_comp_size   = len(new_compressed)
new_uncomp_size = len(new_json_bytes)
old_comp_size   = info.compress_size
size_diff       = new_comp_size - old_comp_size

print(f"Layout: {old_comp_size} B -> {new_comp_size} B  (diff {size_diff:+d})")

h = info.header_offset
assert orig[h:h+4] == b"PK\x03\x04"
fname_len  = struct.unpack_from("<H", orig, h+26)[0]
extra_len  = struct.unpack_from("<H", orig, h+28)[0]
data_start = h + 30 + fname_len + extra_len
data_end   = data_start + old_comp_size

flags  = struct.unpack_from("<H", orig, h+6)[0]
has_dd = bool(flags & 0x08)
dd_end = data_end
if has_dd:
    dd_end = data_end + (16 if orig[data_end:data_end+4] == b"PK\x07\x08" else 12)

header = bytearray(orig[h:data_start])
struct.pack_into("<I", header, 14, new_crc)
struct.pack_into("<I", header, 18, new_comp_size)
struct.pack_into("<I", header, 22, new_uncomp_size)

new_bytes  = bytearray()
new_bytes += orig[:h]
new_bytes += header
new_bytes += new_compressed

if has_dd:
    dd  = bytearray(orig[data_end:dd_end])
    off = 4 if orig[data_end:data_end+4] == b"PK\x07\x08" else 0
    struct.pack_into("<I", dd, off,   new_crc)
    struct.pack_into("<I", dd, off+4, new_comp_size)
    struct.pack_into("<I", dd, off+8, new_uncomp_size)
    new_bytes += dd

new_bytes += orig[dd_end:]

# EOCD
eocd_sig = b"PK\x05\x06"
eocd_pos = next(i for i in range(len(new_bytes)-22, max(0, len(new_bytes)-65578), -1)
                if new_bytes[i:i+4] == eocd_sig)
old_cd_offset = struct.unpack_from("<I", new_bytes, eocd_pos+16)[0]
struct.pack_into("<I", new_bytes, eocd_pos+16, old_cd_offset + size_diff)

# Central Directory
pos_cd = old_cd_offset + size_diff
layout_done = False
while new_bytes[pos_cd:pos_cd+4] == b"PK\x01\x02":
    fl = struct.unpack_from("<H", new_bytes, pos_cd+28)[0]
    el = struct.unpack_from("<H", new_bytes, pos_cd+30)[0]
    cl = struct.unpack_from("<H", new_bytes, pos_cd+32)[0]
    try:    fname = new_bytes[pos_cd+46:pos_cd+46+fl].decode("utf-8")
    except: fname = new_bytes[pos_cd+46:pos_cd+46+fl].decode("latin-1")

    if fname == "Report/Layout":
        struct.pack_into("<I", new_bytes, pos_cd+16, new_crc)
        struct.pack_into("<I", new_bytes, pos_cd+20, new_comp_size)
        struct.pack_into("<I", new_bytes, pos_cd+24, new_uncomp_size)
        layout_done = True
    elif layout_done:
        old_off = struct.unpack_from("<I", new_bytes, pos_cd+42)[0]
        struct.pack_into("<I", new_bytes, pos_cd+42, old_off + size_diff)

    pos_cd += 46 + fl + el + cl

with open(OUT, "wb") as f:
    f.write(new_bytes)

print(f"\nGravado: {OUT.name}  ({len(new_bytes)//1024} KB)")
print(f"Paginas: {len(layout['sections'])}  |  Visuais na P2: {len(containers)}")
print("Abre o dashboard_socioeconomico.pbix no Power BI Desktop!")
