# -*- coding: utf-8 -*-
"""
Injeta a Pagina 2 (Perfil Socioeconomico) no dashboard_socioeconomico.pbix.
Executa com PBI Desktop FECHADO.
"""
import json, zipfile, shutil, uuid
from pathlib import Path

PBIX = Path(r"c:\Users\roberg\OneDrive - Alvarez and Marsal\Desktop\Projeto em Ciencia de Dados III\AP1 Projeto 3\dados_tratados\dashboard_socioeconomico.pbix")

# Fallback se nome tiver acento
if not PBIX.exists():
    PBIX = Path(__file__).parent / "dashboard_socioeconomico.pbix"

BACKUP = PBIX.with_suffix(".pbix.bak")

def uid():
    return uuid.uuid4().hex[:16]

# ── helpers de config ──────────────────────────────────────────────────────────

def pos(w, h, tab=0):
    return [{"id": 0, "position": {"x": 0, "y": 0, "z": 0, "width": w, "height": h, "tabOrder": tab}}]

def vc(x, y, z, w, h, cfg, qry=None):
    obj = {"x": x, "y": y, "z": z, "width": w, "height": h,
           "config": json.dumps(cfg, ensure_ascii=False),
           "filters": "[]"}
    if qry:
        obj["query"] = json.dumps(qry, ensure_ascii=False)
    return obj

def textbox(text, w, h, bold=False, size=14, color="#212121", tab=0):
    style = {"fontSize": f"{size}px", "color": color}
    if bold:
        style["fontWeight"] = "bold"
    return {
        "name": uid(),
        "layouts": pos(w, h, tab),
        "singleVisual": {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": [
                {"textRuns": [{"value": text, "textStyle": style}],
                 "horizontalTextAlignment": "left"}
            ]}}]}
        }
    }

def card(table, measure, title, w, h, tab=0):
    name = uid()
    proj_ref = f"{table}.{measure}"
    return {
        "name": name,
        "layouts": pos(w, h, tab),
        "singleVisual": {
            "visualType": "card",
            "projections": {"Values": [{"queryRef": proj_ref, "active": False}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "t", "Entity": table, "Type": 0}],
                "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}},
                                        "Property": measure}, "Name": proj_ref}]
            },
            "vcObjects": {
                "title": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                }}],
                "labels": [{"properties": {
                    "fontSize": {"expr": {"Literal": {"Value": "24D"}}}
                }}]
            }
        }
    }

def col_chart(cat_tbl, cat_col, msr_tbl, msr, title, w, h, sort_col=None, tab=0):
    src_a = "a"
    select = [
        {"Column": {"Expression": {"SourceRef": {"Source": src_a}}, "Property": cat_col},
         "Name": f"{cat_tbl}.{cat_col}"},
        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": msr},
         "Name": f"{msr_tbl}.{msr}"}
    ]
    proto = {
        "Version": 2,
        "From": [{"Name": src_a, "Entity": cat_tbl, "Type": 0},
                 {"Name": "m", "Entity": msr_tbl, "Type": 0}],
        "Select": select
    }
    if sort_col:
        proto["OrderBy"] = [{"Direction": 1, "Expression": {
            "Column": {"Expression": {"SourceRef": {"Source": src_a}}, "Property": sort_col}
        }}]
    return {
        "name": uid(),
        "layouts": pos(w, h, tab),
        "singleVisual": {
            "visualType": "clusteredColumnChart",
            "projections": {
                "Category": [{"queryRef": f"{cat_tbl}.{cat_col}", "active": False}],
                "Y":        [{"queryRef": f"{msr_tbl}.{msr}",    "active": False}]
            },
            "prototypeQuery": proto,
            "vcObjects": {"title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
            }}]}
        }
    }

def donut(cat_tbl, cat_col, msr_tbl, msr, title, w, h, tab=0):
    return {
        "name": uid(),
        "layouts": pos(w, h, tab),
        "singleVisual": {
            "visualType": "donutChart",
            "projections": {
                "Category": [{"queryRef": f"{cat_tbl}.{cat_col}", "active": False}],
                "Y":        [{"queryRef": f"{msr_tbl}.{msr}",    "active": False}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "a", "Entity": cat_tbl, "Type": 0},
                         {"Name": "m", "Entity": msr_tbl,  "Type": 0}],
                "Select": [
                    {"Column": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": cat_col},
                     "Name": f"{cat_tbl}.{cat_col}"},
                    {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": msr},
                     "Name": f"{msr_tbl}.{msr}"}
                ]
            },
            "vcObjects": {"title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
            }}]}
        }
    }

def stacked(cat_tbl, cat_col, ser_col, msr_tbl, msr, title, w, h,
            ser_tbl=None, sort_col=None, tab=0):
    ser_tbl = ser_tbl or cat_tbl
    ser_src = "b" if ser_tbl != cat_tbl else "a"
    from_list = [{"Name": "a", "Entity": cat_tbl, "Type": 0},
                 {"Name": "m", "Entity": msr_tbl,  "Type": 0}]
    if ser_tbl != cat_tbl:
        from_list.append({"Name": "b", "Entity": ser_tbl, "Type": 0})
    select = [
        {"Column": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": cat_col},
         "Name": f"{cat_tbl}.{cat_col}"},
        {"Column": {"Expression": {"SourceRef": {"Source": ser_src}}, "Property": ser_col},
         "Name": f"{ser_tbl}.{ser_col}"},
        {"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": msr},
         "Name": f"{msr_tbl}.{msr}"}
    ]
    proto = {"Version": 2, "From": from_list, "Select": select}
    if sort_col:
        proto["OrderBy"] = [{"Direction": 1, "Expression": {
            "Column": {"Expression": {"SourceRef": {"Source": "a"}}, "Property": sort_col}
        }}]
    return {
        "name": uid(),
        "layouts": pos(w, h, tab),
        "singleVisual": {
            "visualType": "stackedColumnChart",
            "projections": {
                "Category": [{"queryRef": f"{cat_tbl}.{cat_col}", "active": False}],
                "Series":   [{"queryRef": f"{ser_tbl}.{ser_col}", "active": False}],
                "Y":        [{"queryRef": f"{msr_tbl}.{msr}",     "active": False}]
            },
            "prototypeQuery": proto,
            "vcObjects": {"title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
            }}]}
        }
    }

def slicer(table, col, title, w, h, tab=0):
    return {
        "name": uid(),
        "layouts": pos(w, h, tab),
        "singleVisual": {
            "visualType": "slicer",
            "projections": {"Values": [{"queryRef": f"{table}.{col}", "active": False}]},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "a", "Entity": table, "Type": 0}],
                "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "a"}},
                                       "Property": col}, "Name": f"{table}.{col}"}]
            },
            "vcObjects": {"title": [{"properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}
            }}]}
        }
    }


# ── Montar containers da Pagina 2 ─────────────────────────────────────────────
#
#  Canvas 1280 x 720
#  Sidebar esquerda (slicers): x=5, w=148
#  Conteudo principal: x=158, w=1112
#
containers = []
z = 1
tab = 0

def add(x, y, w, h, cfg):
    global z, tab
    containers.append(vc(x, y, z, w, h, cfg))
    z += 1; tab += 1

# Cabecalho
add(158,  5, 1112, 38, textbox("Perfil Socioeconômico dos Alunos — IRMR",                      1112, 38, bold=True,  size=20, color="#0D47A1"))
add(158, 45, 1112, 26, textbox("Distribuição por renda, instituição e escolaridade  ·  n = 143", 1112, 26, bold=False, size=11, color="#616161"))

# Cards KPI (3 cards lado a lado)
add(158,  80, 220, 85, card("_Medidas", "AlunosBaixaRenda",    "Alunos até 3 SM",       220, 85))
add(388,  80, 220, 85, card("_Medidas", "PctBaixaRenda",       "% Baixa renda (<=3 SM)", 220, 85))
add(618,  80, 220, 85, card("_Medidas", "PctEscolaPublica",    "% Escola pública",       220, 85))

# Grafico 1: Renda Familiar (colunas agrupadas)
add(158, 174, 580, 198,
    col_chart("Alunos", "FaixaRenda", "_Medidas", "TotalAlunos",
              "Renda familiar (em salários mínimos)", 580, 198, sort_col="FaixaRendaOrdem"))

# Grafico 2: Tipo de Instituicao (donut)
add(748, 174, 522, 198,
    donut("Alunos", "TipoInstituicao", "_Medidas", "TotalAlunos",
          "Tipo de instituição de ensino", 522, 198))

# Grafico 4: Renda x Instituicao (barras empilhadas — cruzamento principal)
add(158, 380, 1112, 152,
    stacked("Alunos", "FaixaRenda", "TipoInstituicao", "_Medidas", "TotalAlunos",
            "Renda familiar × Tipo de instituição", 1112, 152, sort_col="FaixaRendaOrdem"))

# Grafico 3: Escolaridade (colunas agrupadas)
add(158, 540, 546, 172,
    col_chart("Alunos", "AnoEscolar", "_Medidas", "TotalAlunos",
              "Nível de escolaridade", 546, 172, sort_col="AnoEscolarOrdem"))

# Grafico 5: Renda x Deficiencia (barras empilhadas)
add(714, 540, 556, 172,
    stacked("Alunos", "FaixaRenda", "TipoDeficiencia", "_Medidas", "PctSobreTotal",
            "Renda familiar × Tipo de deficiência", 556, 172, sort_col="FaixaRendaOrdem"))

# Slicers (sidebar esquerda)
add(  5,  80, 148, 260, slicer("Alunos", "FaixaRenda",      "Renda",        148, 260))
add(  5, 348, 148, 110, slicer("Alunos", "TipoInstituicao", "Instituição",  148, 110))
add(  5, 466, 148, 130, slicer("Alunos", "FaixaEtaria",     "Faixa Etária", 148, 130))


# ── Construir a nova secao (pagina) ──────────────────────────────────────────
pagina2 = {
    "id": 1,
    "name": uid(),
    "displayName": "Perfil Socioeconômico",
    "filters": "[]",
    "ordinal": 1,
    "visualContainers": containers,
    "config": "{}",
    "displayOption": 1,
    "width": 1280,
    "height": 720
}


# ── Ler, modificar e regravar o .pbix ────────────────────────────────────────
print(f"PBIX: {PBIX}")
print(f"Existe: {PBIX.exists()}")

# Backup
shutil.copy2(PBIX, BACKUP)
print(f"Backup: {BACKUP.name}")

# Ler o ZIP
TEMP = PBIX.with_suffix(".pbix.tmp")
with zipfile.ZipFile(PBIX, "r") as zin, zipfile.ZipFile(TEMP, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "Report/Layout":
            layout = json.loads(data.decode("utf-16-le"))
            # Adicionar pagina 2
            layout["sections"].append(pagina2)
            new_data = json.dumps(layout, ensure_ascii=False).encode("utf-16-le")
            zout.writestr(item, new_data)
            print(f"Layout atualizado: {len(layout['sections'])} paginas")
        else:
            zout.writestr(item, data)

# Substituir original pelo modificado
PBIX.unlink()
TEMP.rename(PBIX)
print(f"\nSucesso! {PBIX.name} atualizado ({PBIX.stat().st_size // 1024} KB)")
print(f"Pagina 2 tem {len(containers)} visuais")
