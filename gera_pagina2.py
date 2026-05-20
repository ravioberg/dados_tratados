# -*- coding: utf-8 -*-
"""
Gera Pagina 2 (Perfil Socioeconomico) no PBIP - formato schema 2.9.0 correto.
Executa com PBI Desktop FECHADO.
"""
import uuid, json, shutil
from pathlib import Path

BASE       = Path(__file__).parent
PAGES_DIR  = BASE / "socioeconomico.Report" / "definition" / "pages"
PAGES_JSON = PAGES_DIR / "pages.json"

VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"
PAGE_SCHEMA   = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"

def uid():
    return uuid.uuid4().hex[:20]

# ── helpers de campo ──────────────────────────────────────────────────────────

def col_field(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}

def msr_field(entity, prop):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}

def proj(field, query_ref, native_ref, active=False):
    p = {"field": field, "queryRef": query_ref, "nativeQueryRef": native_ref}
    if active:
        p["active"] = True
    return p

# ── helpers de visual ─────────────────────────────────────────────────────────

def textbox(text, bold=False, size=14, color="#212121"):
    style = {"fontSize": f"{size}px", "color": color}
    if bold:
        style["fontWeight"] = "bold"
    return {
        "visualType": "textbox",
        "objects": {"general": [{"properties": {"paragraphs": [
            {"textRuns": [{"value": text, "textStyle": style}],
             "horizontalTextAlignment": "left"}
        ]}}]}
    }

def card(tbl, msr):
    f = msr_field(tbl, msr)
    return {
        "visualType": "card",
        "query": {"queryState": {
            "Values": {"projections": [proj(f, f"{tbl}.{msr}", msr)]}
        }}
    }

def col_chart(cat_tbl, cat_col, msr_tbl, msr):
    return {
        "visualType": "clusteredColumnChart",
        "query": {"queryState": {
            "Category": {"projections": [proj(col_field(cat_tbl, cat_col),
                                              f"{cat_tbl}.{cat_col}", cat_col, active=True)]},
            "Y":        {"projections": [proj(msr_field(msr_tbl, msr),
                                              f"{msr_tbl}.{msr}", msr)]}
        }}
    }

def donut(cat_tbl, cat_col, msr_tbl, msr):
    return {
        "visualType": "donutChart",
        "query": {"queryState": {
            "Category": {"projections": [proj(col_field(cat_tbl, cat_col),
                                              f"{cat_tbl}.{cat_col}", cat_col, active=True)]},
            "Y":        {"projections": [proj(msr_field(msr_tbl, msr),
                                              f"{msr_tbl}.{msr}", msr)]}
        }}
    }

def stacked(cat_tbl, cat_col, ser_col, msr_tbl, msr):
    return {
        "visualType": "columnChart",
        "query": {"queryState": {
            "Category": {"projections": [proj(col_field(cat_tbl, cat_col),
                                              f"{cat_tbl}.{cat_col}", cat_col, active=True)]},
            "Series":   {"projections": [proj(col_field(cat_tbl, ser_col),
                                              f"{cat_tbl}.{ser_col}", ser_col)]},
            "Y":        {"projections": [proj(msr_field(msr_tbl, msr),
                                              f"{msr_tbl}.{msr}", msr)]}
        }}
    }

def slicer(tbl, col):
    return {
        "visualType": "slicer",
        "query": {"queryState": {
            "Values": {"projections": [proj(col_field(tbl, col),
                                           f"{tbl}.{col}", col, active=True)]}
        }}
    }

# ── 13 visuais: (x, y, z, w, h, tab, conteudo) ───────────────────────────────

VISUALS = [
    (158,   5,  1, 1112,  38,  0,
     textbox("Perfil Socioeconômico dos Alunos — IRMR", bold=True, size=20, color="#0D47A1")),

    (158,  45,  2, 1112,  26,  1,
     textbox("Distribuição por renda, instituição e escolaridade  ·  n = 143", size=11, color="#616161")),

    (158,  80,  3,  220,  85,  2,
     card("_Medidas", "AlunosBaixaRenda")),

    (388,  80,  4,  220,  85,  3,
     card("_Medidas", "PctBaixaRenda")),

    (618,  80,  5,  220,  85,  4,
     card("_Medidas", "PctEscolaPublica")),

    (158, 174,  6,  580, 198,  5,
     col_chart("Alunos", "FaixaRenda", "_Medidas", "TotalAlunos")),

    (748, 174,  7,  522, 198,  6,
     donut("Alunos", "TipoInstituicao", "_Medidas", "TotalAlunos")),

    (158, 380,  8, 1112, 152,  7,
     stacked("Alunos", "FaixaRenda", "TipoInstituicao", "_Medidas", "TotalAlunos")),

    (158, 540,  9,  546, 172,  8,
     col_chart("Alunos", "AnoEscolar", "_Medidas", "TotalAlunos")),

    (714, 540, 10,  556, 172,  9,
     stacked("Alunos", "FaixaEtaria", "TipoInstituicao", "_Medidas", "TotalAlunos")),

    (  5,  80, 11,  148, 260, 10,
     slicer("Alunos", "FaixaRenda")),

    (  5, 348, 12,  148, 110, 11,
     slicer("Alunos", "TipoInstituicao")),

    (  5, 466, 13,  148, 130, 12,
     slicer("Alunos", "FaixaEtaria")),
]

# ── remover pagina antiga, criar nova ─────────────────────────────────────────

pages = json.loads(PAGES_JSON.read_text(encoding="utf-8"))

# apagar pastas de paginas geradas anteriormente (nao a Page 1 original)
ORIGINAL_PAGE = "9962dea5a562b53f6bd9"
for page_id in list(pages.get("pageOrder", [])):
    if page_id != ORIGINAL_PAGE:
        pages["pageOrder"].remove(page_id)
        print(f"Removida do pageOrder: {page_id}")

# nova pagina
PAGE_ID  = uid()
PAGE_DIR = PAGES_DIR / PAGE_ID
VIS_DIR  = PAGE_DIR / "visuals"
VIS_DIR.mkdir(parents=True)

(PAGE_DIR / "page.json").write_text(json.dumps({
    "$schema": PAGE_SCHEMA,
    "name": PAGE_ID,
    "displayName": "Perfil Socioeconômico",
    "displayOption": "FitToPage",
    "height": 720,
    "width": 1280
}, ensure_ascii=False, indent=2), encoding="utf-8")

for x, y, z, w, h, tab, content in VISUALS:
    vid = uid()
    vis_dir = VIS_DIR / vid
    vis_dir.mkdir()
    (vis_dir / "visual.json").write_text(json.dumps({
        "$schema": VISUAL_SCHEMA,
        "name": vid,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": tab},
        "visual": content
    }, ensure_ascii=False, indent=2), encoding="utf-8")

pages["pageOrder"].append(PAGE_ID)
PAGES_JSON.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Pagina criada: {PAGE_ID}")
print(f"Visuais: {len(VISUALS)}")
print("Abra socioeconomico.pbip no Power BI Desktop.")
