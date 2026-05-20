# -*- coding: utf-8 -*-
"""
Injeta tabelas Alunos e _Medidas no SemanticModel do PBIP socioeconomico.
Executa com PBI Desktop FECHADO.
"""
import uuid
from pathlib import Path

BASE       = Path(__file__).parent
SM_DEF     = BASE / "socioeconomico.SemanticModel" / "definition"
TABLES_DIR = SM_DEF / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = str(BASE / "alunos_perfil_limpo.csv")

def uid():
    return str(uuid.uuid4())

# ─── Alunos.tmdl ─────────────────────────────────────────────────────────────

COLUMNS = [
    ("RecordID",               "int64",   {}),
    ("NomeAluno",              "string",  {}),
    ("Status",                 "string",  {}),
    ("Sexo",                   "string",  {}),
    ("Cor",                    "string",  {}),
    ("Idade",                  "int64",   {}),
    ("FaixaEtaria",            "string",  {}),
    ("FaixaEtariaOrdem",       "int64",   {}),
    ("FaixaRenda",             "string",  {"sortByColumn": "FaixaRendaOrdem"}),
    ("FaixaRendaOrdem",        "int64",   {}),
    ("RendaSM_Aprox",          "double",  {}),
    ("TipoInstituicao",        "string",  {}),
    ("NivelEnsino",            "string",  {}),
    ("AnoEscolar",             "string",  {"sortByColumn": "AnoEscolarOrdem"}),
    ("AnoEscolarOrdem",        "int64",   {}),
    ("DeficienciaFisica",      "boolean", {}),
    ("DeficienciaIntelectual", "boolean", {}),
    ("SemDeficiencia",         "boolean", {}),
    ("DiagnosticoDiferenciado","boolean", {}),
    ("DiagnosticoPrincipal",   "string",  {}),
    ("DiagnosticoAgrupado",    "string",  {}),
]

def build_alunos():
    T  = "\t"
    TT = "\t\t"
    lines = [
        f"table Alunos",
        f"{T}lineageTag: {uid()}",
        "",
    ]

    for col_name, dtype, props in COLUMNS:
        lines += [
            f"{T}column {col_name}",
            f"{TT}dataType: {dtype}",
            f"{TT}lineageTag: {uid()}",
            f"{TT}sourceColumn: {col_name}",
        ]
        if "sortByColumn" in props:
            lines.append(f"{TT}sortByColumn: {props['sortByColumn']}")
        lines.append("")

    # Partition M
    lines += [
        f"{T}partition Alunos = m",
        f"{TT}mode: import",
        f"{TT}source =",
        f"{TT}\t\tlet",
        f'{TT}\t\t    Source = Csv.Document(File.Contents("{CSV_PATH}"), [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        f'{TT}\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'{TT}\t\t    #"Changed Types" = Table.TransformColumnTypes(#"Promoted Headers", {{',
        f'{TT}\t\t        {{"RecordID", Int64.Type}},',
        f'{TT}\t\t        {{"NomeAluno", type text}},',
        f'{TT}\t\t        {{"Status", type text}},',
        f'{TT}\t\t        {{"Sexo", type text}},',
        f'{TT}\t\t        {{"Cor", type text}},',
        f'{TT}\t\t        {{"Idade", Int64.Type}},',
        f'{TT}\t\t        {{"FaixaEtaria", type text}},',
        f'{TT}\t\t        {{"FaixaEtariaOrdem", Int64.Type}},',
        f'{TT}\t\t        {{"FaixaRenda", type text}},',
        f'{TT}\t\t        {{"FaixaRendaOrdem", Int64.Type}},',
        f'{TT}\t\t        {{"RendaSM_Aprox", type number}},',
        f'{TT}\t\t        {{"TipoInstituicao", type text}},',
        f'{TT}\t\t        {{"NivelEnsino", type text}},',
        f'{TT}\t\t        {{"AnoEscolar", type text}},',
        f'{TT}\t\t        {{"AnoEscolarOrdem", Int64.Type}},',
        f'{TT}\t\t        {{"DeficienciaFisica", type logical}},',
        f'{TT}\t\t        {{"DeficienciaIntelectual", type logical}},',
        f'{TT}\t\t        {{"SemDeficiencia", type logical}},',
        f'{TT}\t\t        {{"DiagnosticoDiferenciado", type logical}},',
        f'{TT}\t\t        {{"DiagnosticoPrincipal", type text}},',
        f'{TT}\t\t        {{"DiagnosticoAgrupado", type text}}',
        f'{TT}\t\t    }})',
        f'{TT}\t\tin',
        f'{TT}\t\t    #"Changed Types"',
        "",
        f"{T}annotation PBI_ResultType = Table",
        "",
    ]
    return "\n".join(lines)


# ─── _Medidas.tmdl ────────────────────────────────────────────────────────────

MEASURES = [
    ("TotalAlunos",
     "COUNTROWS(Alunos)",
     "#,0"),
    ("AlunosEscolaPublica",
     'CALCULATE([TotalAlunos], Alunos[TipoInstituicao] = "Pública")',
     "#,0"),
    ("AlunosEscolaParticular",
     'CALCULATE([TotalAlunos], Alunos[TipoInstituicao] = "Particular")',
     "#,0"),
    ("PctEscolaPublica",
     "DIVIDE([AlunosEscolaPublica], [TotalAlunos])",
     "0.0%"),
    ("RendaMediaSM",
     "AVERAGE(Alunos[RendaSM_Aprox])",
     "0.0"),
    ("AlunosBaixaRenda",
     "CALCULATE([TotalAlunos], Alunos[FaixaRendaOrdem] <= 3)",
     "#,0"),
    ("PctBaixaRenda",
     "DIVIDE([AlunosBaixaRenda], [TotalAlunos])",
     "0.0%"),
    ("PctSobreTotal",
     "DIVIDE([TotalAlunos], CALCULATE([TotalAlunos], ALL(Alunos)))",
     "0.0%"),
]

def build_medidas():
    T  = "\t"
    TT = "\t\t"
    lines = [
        "table _Medidas",
        f"{T}lineageTag: {uid()}",
        "",
    ]
    for name, expr, fmt in MEASURES:
        lines += [
            f"{T}measure {name} = {expr}",
            f"{TT}lineageTag: {uid()}",
            f"{TT}formatString: {fmt}",
            "",
        ]
    lines += [
        f"{T}partition _Medidas = calculated",
        f'{TT}source = {{""}}',
        "",
        f'{T}annotation PBI_Id = {uid()}',
        "",
    ]
    return "\n".join(lines)


# ─── Gravar ───────────────────────────────────────────────────────────────────

alunos_path  = TABLES_DIR / "Alunos.tmdl"
medidas_path = TABLES_DIR / "_Medidas.tmdl"

alunos_path.write_text(build_alunos(),  encoding="utf-8")
medidas_path.write_text(build_medidas(), encoding="utf-8")

print(f"Criado: {alunos_path.relative_to(BASE)}")
print(f"Criado: {medidas_path.relative_to(BASE)}")
print()
print("Colunas na tabela Alunos:", len(COLUMNS), "(TipoDeficiencia: adicionar manualmente no PBI)")
print("Medidas em _Medidas:", len(MEASURES))
print()
print("Abra socioeconomico.pbip no Power BI Desktop.")
print("Se pedir para atualizar dados, clique em Atualizar.")
