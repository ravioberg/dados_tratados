# -*- coding: utf-8 -*-
"""
Analise Exploratoria Visual - Pagina 2: Perfil Socioeconomico (IRMR)
Gera 5 graficos PNG para validar os dados antes de montar o Power BI.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

# ── Configurações gerais ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "alunos_perfil_limpo.csv"
OUT_DIR  = BASE_DIR / "graficos_eda"
OUT_DIR.mkdir(exist_ok=True)

PALETTE_INST = {"Pública": "#2196F3", "Particular": "#FF9800", "Sem registro": "#BDBDBD"}
PALETTE_DEF  = {
    "Deficiência Física":       "#1976D2",
    "Deficiência Intelectual":  "#F57C00",
    "Sem Deficiência":          "#43A047",
    "Outro":                    "#9E9E9E",
}
COR_PRINCIPAL = "#1565C0"

sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({"figure.dpi": 150, "savefig.bbox": "tight"})

df = pd.read_csv(CSV_PATH)

# Coluna auxiliar TipoDeficiencia
def classifica_deficiencia(row):
    if row["SemDeficiencia"]:
        return "Sem Deficiência"
    elif row["DeficienciaFisica"]:
        return "Deficiência Física"
    elif row["DeficienciaIntelectual"]:
        return "Deficiência Intelectual"
    return "Outro"

df["TipoDeficiencia"] = df.apply(classifica_deficiencia, axis=1)


# ── Gráfico 1: Distribuição por FaixaRenda ───────────────────────────────────
def grafico1_renda():
    ordem = (
        df[["FaixaRenda", "FaixaRendaOrdem"]]
        .drop_duplicates()
        .sort_values("FaixaRendaOrdem")["FaixaRenda"]
        .tolist()
    )
    contagem = df.groupby("FaixaRenda").size().reindex(ordem)

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(range(len(contagem)), contagem.values, color=COR_PRINCIPAL, edgecolor="white")
    ax.set_xticks(range(len(contagem)))
    ax.set_xticklabels(contagem.index, rotation=35, ha="right")
    ax.set_xlabel("Faixa de Renda Familiar")
    ax.set_ylabel("Número de Alunos")
    ax.set_title("Renda Familiar (em salários mínimos)", fontsize=14, fontweight="bold")

    for bar, val in zip(bars, contagem.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha="center", va="bottom", fontsize=9)

    ax.annotate("n = 143 alunos", xy=(0.98, 0.97), xycoords="axes fraction",
                ha="right", va="top", fontsize=9, color="gray")
    fig.savefig(OUT_DIR / "grafico1_renda_familiar.png")
    plt.close(fig)
    print("OK: Grafico 1 salvo")


# ── Gráfico 2: Distribuição por TipoInstituição ──────────────────────────────
def grafico2_instituicao():
    contagem = df["TipoInstituicao"].value_counts()
    cores    = [PALETTE_INST.get(k, "#90A4AE") for k in contagem.index]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        contagem.values,
        labels=contagem.index,
        autopct="%1.1f%%",
        colors=cores,
        startangle=90,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for t in autotexts:
        t.set_fontsize(11)
    ax.set_title("Tipo de Instituição de Ensino", fontsize=14, fontweight="bold", pad=20)

    legenda = [f"{k}: {v}" for k, v in zip(contagem.index, contagem.values)]
    ax.legend(legenda, loc="lower center", bbox_to_anchor=(0.5, -0.1),
              ncol=len(contagem), fontsize=9)
    fig.savefig(OUT_DIR / "grafico2_tipo_instituicao.png")
    plt.close(fig)
    print("OK: Grafico 2 salvo")


# ── Gráfico 3: Distribuição por AnoEscolar ───────────────────────────────────
def grafico3_escolaridade():
    ordem = (
        df[["AnoEscolar", "AnoEscolarOrdem"]]
        .drop_duplicates()
        .sort_values("AnoEscolarOrdem")["AnoEscolar"]
        .tolist()
    )
    contagem = df.groupby("AnoEscolar").size().reindex(ordem)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(contagem)), contagem.values, color="#00838F", edgecolor="white")
    ax.set_xticks(range(len(contagem)))
    ax.set_xticklabels(contagem.index, rotation=40, ha="right")
    ax.set_xlabel("Nível de Escolaridade")
    ax.set_ylabel("Número de Alunos")
    ax.set_title("Distribuição por Nível de Escolaridade", fontsize=14, fontweight="bold")

    for bar, val in zip(bars, contagem.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                str(val), ha="center", va="bottom", fontsize=9)

    ax.annotate("n = 143 alunos", xy=(0.98, 0.97), xycoords="axes fraction",
                ha="right", va="top", fontsize=9, color="gray")
    fig.savefig(OUT_DIR / "grafico3_escolaridade.png")
    plt.close(fig)
    print("OK: Grafico 3 salvo")


# ── Gráfico 4: Renda × TipoInstituição (barras empilhadas) ───────────────────
def grafico4_renda_x_inst():
    ordem_renda = (
        df[["FaixaRenda", "FaixaRendaOrdem"]]
        .drop_duplicates()
        .sort_values("FaixaRendaOrdem")["FaixaRenda"]
        .tolist()
    )
    cross = (
        df.groupby(["FaixaRenda", "TipoInstituicao"])
        .size()
        .unstack(fill_value=0)
        .reindex(ordem_renda)
    )
    cores = [PALETTE_INST.get(c, "#90A4AE") for c in cross.columns]

    fig, ax = plt.subplots(figsize=(12, 5))
    cross.plot(kind="bar", stacked=True, ax=ax, color=cores, edgecolor="white", width=0.7)
    ax.set_xlabel("Faixa de Renda Familiar")
    ax.set_ylabel("Número de Alunos")
    ax.set_title("Renda Familiar × Tipo de Instituição de Ensino", fontsize=14, fontweight="bold")
    ax.set_xticklabels(cross.index, rotation=35, ha="right")
    ax.legend(title="Instituição", bbox_to_anchor=(1.01, 1), loc="upper left")
    fig.savefig(OUT_DIR / "grafico4_renda_x_instituicao.png")
    plt.close(fig)
    print("OK: Grafico 4 salvo")


# ── Gráfico 5: Renda × TipoDeficiência (barras empilhadas) ───────────────────
def grafico5_renda_x_def():
    ordem_renda = (
        df[["FaixaRenda", "FaixaRendaOrdem"]]
        .drop_duplicates()
        .sort_values("FaixaRendaOrdem")["FaixaRenda"]
        .tolist()
    )
    ordem_def = ["Deficiência Física", "Deficiência Intelectual", "Sem Deficiência", "Outro"]
    cross = (
        df.groupby(["FaixaRenda", "TipoDeficiencia"])
        .size()
        .unstack(fill_value=0)
        .reindex(ordem_renda)
    )
    # Garantir ordem das colunas
    cols = [c for c in ordem_def if c in cross.columns]
    cross = cross[cols]
    cores = [PALETTE_DEF[c] for c in cols]

    fig, ax = plt.subplots(figsize=(12, 5))
    cross.plot(kind="bar", stacked=True, ax=ax, color=cores, edgecolor="white", width=0.7)
    ax.set_xlabel("Faixa de Renda Familiar")
    ax.set_ylabel("Número de Alunos")
    ax.set_title("Renda Familiar × Tipo de Deficiência", fontsize=14, fontweight="bold")
    ax.set_xticklabels(cross.index, rotation=35, ha="right")
    ax.legend(title="Tipo de Deficiência", bbox_to_anchor=(1.01, 1), loc="upper left")
    fig.savefig(OUT_DIR / "grafico5_renda_x_deficiencia.png")
    plt.close(fig)
    print("OK: Grafico 5 salvo")


# ── Executar todos ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Lendo {CSV_PATH.name} — {len(df)} linhas")
    grafico1_renda()
    grafico2_instituicao()
    grafico3_escolaridade()
    grafico4_renda_x_inst()
    grafico5_renda_x_def()
    print(f"\nTodos os gráficos salvos em: {OUT_DIR}")
