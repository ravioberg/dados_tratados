# -*- coding: utf-8 -*-
"""
Gera Pagina 3 (Deficiencias e Diagnosticos) no PBIP - formato schema 2.9.0.
Executa com PBI Desktop FECHADO.
"""
import uuid, json
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

def bar_chart(cat_tbl, cat_col, msr_tbl, msr):
    """Gráfico de barras horizontal (barChart) — ideal para muitas categorias."""
    return {
        "visualType": "barChart",
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

# ── Visuais: (x, y, z, w, h, tab, conteudo) ──────────────────────────────────
# Layout: 1280 × 720  |  sidebar esquerda x=5 w=148  |  conteúdo x=158 w=1112
#
# Estrutura:
#   Topo      : título + subtítulo
#   Linha 2   : 3 cards (esq) + donut TipoDeficiencia (dir, alto)
#   Linha 3   : barra horizontal top doenças (esq) + donut continua (dir)
#   Linha 4   : empilhado FaixaEtaria×Deficiência + empilhado FaixaRenda×Deficiência

VISUALS = [
    # ── Slicers (sidebar esquerda) ──
    (  5,  70,  1,  148, 130,  0,
     slicer("Alunos", "TipoDeficiencia")),

    (  5, 205,  2,  148,  80,  1,
     slicer("Alunos", "Sexo")),

    (  5, 290,  3,  148,  90,  2,
     slicer("Alunos", "Cor")),

    (  5, 385,  4,  148, 155,  3,
     slicer("Alunos", "FaixaRenda")),

    (  5, 545,  5,  148,  80,  4,
     slicer("Alunos", "Status")),

    # ── Cabeçalho ──
    (158,   5,  6, 1112,  38,  5,
     textbox("Deficiências e Diagnósticos — IRMR", bold=True, size=20, color="#0D47A1")),

    (158,  45,  7, 1112,  20,  6,
     textbox("Distribuição por tipo de deficiência e diagnóstico específico", size=11, color="#616161")),

    # ── Cards ──
    (158,  70,  8,  220,  85,  7,
     card("_Medidas", "TotalComDeficiencia")),

    (388,  70,  9,  220,  85,  8,
     card("_Medidas", "PctDeficienciaFisica")),

    (618,  70, 10,  220,  85,  9,
     card("_Medidas", "PctDeficienciaIntelectual")),

    # ── Donut TipoDeficiencia (direita, alto — cobre linhas 2 e 3) ──
    (848,  70, 11,  422, 360, 10,
     donut("Alunos", "TipoDeficiencia", "_Medidas", "TotalAlunos")),

    # ── Barras horizontais: top diagnósticos específicos ──
    (158, 165, 12,  680, 265, 11,
     bar_chart("Alunos", "DoencaEspecifica", "_Medidas", "TotalAlunos")),

    # ── Gráficos empilhados (linha inferior) ──
    (158, 440, 13,  550, 258, 12,
     stacked("Alunos", "FaixaEtaria", "TipoDeficiencia", "_Medidas", "TotalAlunos")),

    (718, 440, 14,  552, 258, 13,
     stacked("Alunos", "FaixaRenda", "TipoDeficiencia", "_Medidas", "TotalAlunos")),
]

# ── Adicionar página ao report (sem remover outras) ───────────────────────────

pages = json.loads(PAGES_JSON.read_text(encoding="utf-8"))

# Remove apenas páginas anteriores da Página 3 (mantém Página 2 intacta)
# Para identificar: guarda o ID atual da Página 2 antes de rodar este script
# e não o inclui na lista a remover. Por segurança, remove apenas IDs que
# não sejam o último da lista (que é sempre a Pág 2 gerada por gera_pagina2.py).
if len(pages.get("pageOrder", [])) > 1:
    # mantém só o primeiro ID (Página 2), remove o resto (Página 3 anteriores)
    pag2_id = pages["pageOrder"][0]
    for page_id in list(pages["pageOrder"][1:]):
        pages["pageOrder"].remove(page_id)
        print(f"Removida do pageOrder: {page_id}")

PAGE_ID  = uid()
PAGE_DIR = PAGES_DIR / PAGE_ID
VIS_DIR  = PAGE_DIR / "visuals"
VIS_DIR.mkdir(parents=True)

(PAGE_DIR / "page.json").write_text(json.dumps({
    "$schema": PAGE_SCHEMA,
    "name": PAGE_ID,
    "displayName": "Deficiências e Diagnósticos",
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
