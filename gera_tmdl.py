# -*- coding: utf-8 -*-
"""
Gera arquivos TMDL para o modelo semântico.
Fonte: pasta com arquivos PERFILALUNOSIRMR (suporte a múltiplos meses futuros).
Todo tratamento é feito dentro do Power Query M — sem CSV intermediário.
Executa com PBI Desktop FECHADO.
"""
import uuid
from pathlib import Path

BASE       = Path(__file__).parent
SM_DEF     = BASE / "socioeconomico.SemanticModel" / "definition"
TABLES_DIR = SM_DEF / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

def uid():
    return str(uuid.uuid4())

# ─── M Query template (___FOLDER___ será substituído pelo caminho real) ────────

M_TEMPLATE = """let
    FolderPath = "___FOLDER___",
    AllFiles = Folder.Files(FolderPath),
    PerfisFiles = Table.SelectRows(AllFiles, each Text.Contains([Name], "PERFILALUNOSIRMR") and Text.EndsWith([Name], ".csv")),
    WithParsed = Table.AddColumn(PerfisFiles, "Parsed", each
        let
            Nome = [Name],
            Partes = Text.Split(Nome, "_"),
            DatePart = List.First(List.Select(Partes, each Text.Length(_) = 10)),
            SnapDate = try Date.FromText(DatePart) otherwise null,
            CSV = Csv.Document([Content], [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            Headers = Table.PromoteHeaders(CSV, [PromoteAllScalars=true]),
            WithDate = Table.AddColumn(Headers, "DataSnapshot", each SnapDate)
        in
            WithDate
    ),
    Combined = Table.Combine(WithParsed[Parsed]),
    ComStatus = Table.AddColumn(Combined, "Status", each
        let s = Text.Trim([#"Ativo ou inativo?"])
        in if s = "ATIVO" then "Ativo"
        else if Text.StartsWith(s, "AFAST") then "Afastado"
        else if s = "INATIVO" then "Inativo"
        else s
    ),
    ComFaixaRenda = Table.AddColumn(ComStatus, "FaixaRenda", each
        let r = Text.Trim([#"Renda familiar em salários mínimos:"])
        in if r = "1 Salário Mínimo" then "1 SM"
        else if r = "De 1 a 2 Salários Mínimos" then "1 a 2 SM"
        else if r = "De 2 a 3 Salários Mínimos" then "2 a 3 SM"
        else if r = "De 3 a 4 Salários Mínimos" then "3 a 4 SM"
        else if r = "De 4 a 5 Salários Mínimos" then "4 a 5 SM"
        else if r = "De 5 a 6 Salários Mínimos" then "5 a 6 SM"
        else if r = "De 6 a 7 Salários Mínimos" then "6 a 7 SM"
        else if r = "De 7 a 8 Salários Mínimos" then "7 a 8 SM"
        else if r = "De 8 a 9 Salários Mínimos" then "8 a 9 SM"
        else if r = "De 9 a 10 Salários Mínimos" then "9 a 10 SM"
        else if r = "Acima de 10 Salários Mínimos" then "Acima de 10 SM"
        else "Sem registro"
    ),
    ComFaixaRendaOrdem = Table.AddColumn(ComFaixaRenda, "FaixaRendaOrdem", each
        let r = [FaixaRenda]
        in if r = "1 SM" then 1 else if r = "1 a 2 SM" then 2
        else if r = "2 a 3 SM" then 3 else if r = "3 a 4 SM" then 4
        else if r = "4 a 5 SM" then 5 else if r = "5 a 6 SM" then 6
        else if r = "6 a 7 SM" then 7 else if r = "7 a 8 SM" then 8
        else if r = "8 a 9 SM" then 9 else if r = "9 a 10 SM" then 10
        else if r = "Acima de 10 SM" then 11 else 12
    ),
    ComRendaSM = Table.AddColumn(ComFaixaRendaOrdem, "RendaSM_Aprox", each
        let r = [FaixaRenda]
        in if r = "1 SM" then 1.0 else if r = "1 a 2 SM" then 1.5
        else if r = "2 a 3 SM" then 2.5 else if r = "3 a 4 SM" then 3.5
        else if r = "4 a 5 SM" then 4.5 else if r = "5 a 6 SM" then 5.5
        else if r = "6 a 7 SM" then 6.5 else if r = "7 a 8 SM" then 7.5
        else if r = "8 a 9 SM" then 8.5 else if r = "9 a 10 SM" then 9.5
        else if r = "Acima de 10 SM" then 12.0 else null
    ),
    ComInstituicao = Table.AddColumn(ComRendaSM, "TipoInstituicao", each
        let inst = Text.Trim([#"Instituição PÚBLICA ou PARTICULAR"])
        in if Text.Contains(inst, "PÚBLICO") then "Pública"
        else if Text.Contains(inst, "PARTICULAR") then "Particular"
        else "Sem registro"
    ),
    ComAnoEscolar = Table.AddColumn(ComInstituicao, "AnoEscolar", each
        let a = Text.Trim([#"Ano escolar que cursou ou está cursando:"])
        in if Text.Contains(a, "FUNDAMENTAL II") then "Fund. II"
        else if Text.Contains(a, "FUNDAMENTAL I") then "Fund. I"
        else if Text.Contains(a, "FUNDAMENTAL INCOMPLETO") then "Fund. incoml."
        else if a = "Cursando ENSINO MÉDIO" then "Médio (curs.)"
        else if a = "ENSINO MÉDIO INCOMPLETO" then "Médio incoml."
        else if a = "ENSINO MÉDIO COMPLETO" then "Médio compl."
        else if a = "ENSINO SUPERIOR INCOMPLETO" then "Superior incoml."
        else if a = "ENSINO SUPERIOR COMPLETO" then "Superior compl."
        else "Sem registro"
    ),
    ComAnoEscolarOrdem = Table.AddColumn(ComAnoEscolar, "AnoEscolarOrdem", each
        let a = [AnoEscolar]
        in if a = "Fund. I" then 1 else if a = "Fund. II" then 2
        else if a = "Fund. incoml." then 3 else if a = "Médio (curs.)" then 4
        else if a = "Médio incoml." then 5 else if a = "Médio compl." then 6
        else if a = "Superior incoml." then 7 else if a = "Superior compl." then 8
        else 9
    ),
    ComFaixaEtaria = Table.AddColumn(ComAnoEscolarOrdem, "FaixaEtaria", each
        let idade = try Number.From([#"Idade do aluno"]) otherwise null
        in if idade = null then "Sem registro"
        else if idade <= 12 then "0-12 anos"
        else if idade <= 17 then "13-17 anos"
        else if idade <= 25 then "18-25 anos"
        else if idade <= 39 then "26-39 anos"
        else "40+ anos"
    ),
    ComFaixaEtariaOrdem = Table.AddColumn(ComFaixaEtaria, "FaixaEtariaOrdem", each
        let f = [FaixaEtaria]
        in if f = "0-12 anos" then 1 else if f = "13-17 anos" then 2
        else if f = "18-25 anos" then 3 else if f = "26-39 anos" then 4
        else if f = "40+ anos" then 5 else 6
    ),
    ComDefFisica = Table.AddColumn(ComFaixaEtariaOrdem, "DeficienciaFisica", each
        [#"O aluno tem diagnóstico de alguma doença? (choice=Deficiência Física)"] = "Checked"
    ),
    ComDefInt = Table.AddColumn(ComDefFisica, "DeficienciaIntelectual", each
        [#"O aluno tem diagnóstico de alguma doença? (choice=Deficiência Intelectual)"] = "Checked"
    ),
    ComSemDef = Table.AddColumn(ComDefInt, "SemDeficiencia", each
        [#"O aluno tem diagnóstico de alguma doença? (choice=Sem deficiência)"] = "Checked"
    ),
    ComDiagDif = Table.AddColumn(ComSemDef, "DiagnosticoDiferenciado", each
        [#"O aluno tem diagnóstico de alguma doença? (choice=Diagnóstico diferenciado)"] = "Checked"
    ),
    ComTipoDeficiencia = Table.AddColumn(ComDiagDif, "TipoDeficiencia", each
        if [SemDeficiencia] then "Sem Deficiência"
        else if [DeficienciaFisica] then "Deficiência Física"
        else if [DeficienciaIntelectual] then "Deficiência Intelectual"
        else if [DiagnosticoDiferenciado] then "Diagnóstico Diferenciado"
        else "Sem registro"
    ),
    ComDoenca = Table.AddColumn(ComTipoDeficiencia, "DoencaEspecifica", each
        let d = Text.Upper(Text.Trim([#"Qual doença?"]))
        in if d = "" or d = "SEM DEFICIÊNCIA" then "Sem Deficiência"
        else if d = "LEGG-CALVE-PERTHES" then "Legg-Calvé-Perthes"
        else if d = "MIELOMENINGOCELE" or d = "MENINGOMIELOCELE" then "Mielomeningocele"
        else if Text.StartsWith(d, "PARALISIA CEREBRAL") then "Paralisia Cerebral"
        else if Text.Contains(d, "SÍNDROME DE DOWN") or Text.Contains(d, "SINDROME DE DOWN") then "Síndrome de Down"
        else if Text.StartsWith(d, "TRANSTORNO DO ESPECTRO AUTISTA") then "TEA"
        else if d = "DEFICIÊNCIA INTELECTUAL" or d = "REBAIXAMENTO INTELECTUAL BAIXO" then "Def. Intelectual"
        else Text.Proper(d)
    ),
    ComCor = Table.AddColumn(ComDoenca, "CorLimpa", each
        if Text.Trim([Cor]) = "" then "Sem registro" else Text.Trim([Cor])
    ),
    Selecionado = Table.SelectColumns(ComCor, {
        "Record ID", "NOME DO ALUNO", "Status", "Sexo", "CorLimpa", "Idade do aluno",
        "FaixaEtaria", "FaixaEtariaOrdem",
        "FaixaRenda", "FaixaRendaOrdem", "RendaSM_Aprox",
        "TipoInstituicao", "AnoEscolar", "AnoEscolarOrdem",
        "DeficienciaFisica", "DeficienciaIntelectual", "SemDeficiencia", "DiagnosticoDiferenciado",
        "TipoDeficiencia", "DoencaEspecifica", "DataSnapshot"
    }),
    Renomeado = Table.RenameColumns(Selecionado, {
        {"Record ID", "RecordID"},
        {"NOME DO ALUNO", "NomeAluno"},
        {"Idade do aluno", "Idade"},
        {"CorLimpa", "Cor"}
    }),
    Tipado = Table.TransformColumnTypes(Renomeado, {
        {"RecordID", Int64.Type},
        {"NomeAluno", type text},
        {"Status", type text},
        {"Sexo", type text},
        {"Cor", type text},
        {"Idade", Int64.Type},
        {"FaixaEtaria", type text},
        {"FaixaEtariaOrdem", Int64.Type},
        {"FaixaRenda", type text},
        {"FaixaRendaOrdem", Int64.Type},
        {"RendaSM_Aprox", type number},
        {"TipoInstituicao", type text},
        {"AnoEscolar", type text},
        {"AnoEscolarOrdem", Int64.Type},
        {"DeficienciaFisica", type logical},
        {"DeficienciaIntelectual", type logical},
        {"SemDeficiencia", type logical},
        {"DiagnosticoDiferenciado", type logical},
        {"TipoDeficiencia", type text},
        {"DoencaEspecifica", type text},
        {"DataSnapshot", type date}
    })
in
    Tipado"""

# ─── Colunas da tabela Alunos ─────────────────────────────────────────────────

COLUMNS = [
    ("RecordID",               "int64",    {}),
    ("NomeAluno",              "string",   {}),
    ("Status",                 "string",   {}),
    ("Sexo",                   "string",   {}),
    ("Cor",                    "string",   {}),
    ("Idade",                  "int64",    {}),
    ("FaixaEtaria",            "string",   {"sortByColumn": "FaixaEtariaOrdem"}),
    ("FaixaEtariaOrdem",       "int64",    {}),
    ("FaixaRenda",             "string",   {"sortByColumn": "FaixaRendaOrdem"}),
    ("FaixaRendaOrdem",        "int64",    {}),
    ("RendaSM_Aprox",          "double",   {}),
    ("TipoInstituicao",        "string",   {}),
    ("AnoEscolar",             "string",   {"sortByColumn": "AnoEscolarOrdem"}),
    ("AnoEscolarOrdem",        "int64",    {}),
    ("DeficienciaFisica",      "boolean",  {}),
    ("DeficienciaIntelectual", "boolean",  {}),
    ("SemDeficiencia",         "boolean",  {}),
    ("DiagnosticoDiferenciado","boolean",  {}),
    ("TipoDeficiencia",        "string",   {}),
    ("DoencaEspecifica",       "string",   {}),
    ("DataSnapshot",           "dateTime", {}),
]

def build_alunos():
    T  = "\t"
    TT = "\t\t"
    indent = "\t\t\t\t"   # 4 tabs — nível do bloco M no TMDL

    m_query = M_TEMPLATE.replace("___FOLDER___", str(BASE))
    m_indented = "\n".join(
        indent + line if line.strip() else ""
        for line in m_query.splitlines()
    )

    lines = [
        "table Alunos",
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

    lines += [
        f"{T}partition Alunos = m",
        f"{TT}mode: import",
        f"{TT}source =",
        m_indented,
        "",
        f"{T}annotation PBI_ResultType = Table",
        "",
    ]
    return "\n".join(lines)


# ─── Medidas DAX ─────────────────────────────────────────────────────────────

MEASURES = [
    # Página 2 — Perfil Socioeconômico
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

    # Página 3 — Deficiências e Diagnósticos
    ("TotalComDeficiencia",
     'CALCULATE([TotalAlunos], Alunos[TipoDeficiencia] <> "Sem Deficiência")',
     "#,0"),
    ("PctDeficienciaFisica",
     'DIVIDE(CALCULATE([TotalAlunos], Alunos[TipoDeficiencia] = "Deficiência Física"), [TotalAlunos])',
     "0.0%"),
    ("PctDeficienciaIntelectual",
     'DIVIDE(CALCULATE([TotalAlunos], Alunos[TipoDeficiencia] = "Deficiência Intelectual"), [TotalAlunos])',
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

alunos_path.write_text(build_alunos(),   encoding="utf-8")
medidas_path.write_text(build_medidas(), encoding="utf-8")

print(f"Criado: {alunos_path.relative_to(BASE)}")
print(f"Criado: {medidas_path.relative_to(BASE)}")
print()
print(f"Colunas Alunos : {len(COLUMNS)}")
print(f"Medidas        : {len(MEASURES)}")
print()
print("Abra socioeconomico.pbip no Power BI Desktop.")
print("Se pedir para atualizar dados, clique em Atualizar.")
