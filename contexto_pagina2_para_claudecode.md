# Contexto e Roteiro — Página 2: Perfil Socioeconômico (IRMR)
> Gerado a partir da sessão de análise no Claude.ai  
> Disciplina: Projetos de Ciência de Dados III — Ibmec Faria Lima  
> Professor: Fabio Kazuo Ohashi | Semestre: 2026-1

---

## 1. Contexto do Projeto

### Quem é o cliente
O **Instituto Novo Remo Meu Rumo (IRMR)** é uma ONG vinculada ao Hospital das Clínicas que usa o remo adaptado como ferramenta de reabilitação para pessoas com deficiência. Atualmente atende **143 alunos cadastrados** (140 ativos, 3 afastados por cirurgia).

### Qual é o problema
Os patrocinadores do instituto pedem relatórios socioeconômicos periodicamente (idade, sexo, cor, renda, escolaridade, deficiência). Hoje esses relatórios são feitos **manualmente dentro do REDCap**, sem painel visual. O projeto constrói um dashboard Power BI para resolver isso.

### Pipeline de dados
```
REDCap (Hospital das Clínicas)
  → 3 CSVs exportados em 25/03/2026
    → etl_perfil_alunos.py (Python/pandas — ETL já feito)
      → alunos_perfil_limpo.csv  ← NOSSO ARQUIVO DE TRABALHO
        → Power BI Desktop
```

### Divisão de responsabilidades do grupo
O projeto tem 4 páginas planejadas. **Nossa responsabilidade é a Página 2 — Perfil Socioeconômico.**

| Página | Conteúdo | Responsável |
|--------|----------|-------------|
| Página 1 | Visão Geral (KPIs, sexo, cor, faixa etária, status) | Outro grupo |
| **Página 2** | **Perfil Socioeconômico (renda, escola, escolaridade, cruzamentos)** | **Nosso grupo** |
| Página 3 | Perfil Clínico (deficiências, diagnósticos) | Outro grupo |
| Página 4 | Evolução Temporal (entradas e saídas mensais) | Outro grupo |

---

## 2. O Arquivo de Dados

**Arquivo:** `alunos_perfil_limpo.csv`  
**Localização no projeto:** `dados_tratados/alunos_perfil_limpo.csv`  
**Shape:** 143 linhas × 21 colunas

### Colunas disponíveis
```
RecordID, NomeAluno, Status, Sexo, Cor, Idade, FaixaEtaria, FaixaEtariaOrdem,
FaixaRenda, FaixaRendaOrdem, RendaSM_Aprox, TipoInstituicao, NivelEnsino,
AnoEscolar, AnoEscolarOrdem, DeficienciaFisica, DeficienciaIntelectual,
SemDeficiencia, DiagnosticoDiferenciado, DiagnosticoPrincipal, DiagnosticoAgrupado
```

### Colunas-chave da Página 2
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `FaixaRenda` | Texto | Ex: "1 a 2 SM", "Acima de 10 SM" |
| `FaixaRendaOrdem` | Inteiro | 1 a 11; 99 = Sem registro |
| `RendaSM_Aprox` | Decimal | Valor numérico do ponto médio da faixa |
| `TipoInstituicao` | Texto | "Pública", "Particular", "Sem registro" |
| `AnoEscolar` | Texto | Ex: "Fundamental II", "Médio completo" |
| `AnoEscolarOrdem` | Inteiro | 1 a 8; 99 = Sem registro |
| `NivelEnsino` | Texto | Nível geral de ensino |

---

## 3. Conclusões da Análise Exploratória

### 3.1 Renda Familiar
| Ordem | Faixa | Alunos |
|-------|-------|--------|
| 1 | 1 SM | 15 |
| 2 | 1 a 2 SM | **30** ← maior grupo |
| 3 | 2 a 3 SM | 27 |
| 4 | 3 a 4 SM | 24 |
| 5 | 4 a 5 SM | 13 |
| 6 | 5 a 6 SM | 11 |
| 7 | 6 a 7 SM | 4 |
| 8 | 7 a 8 SM | 2 |
| 9 | 8 a 9 SM | 1 |
| 10 | 9 a 10 SM | 7 |
| 11 | Acima de 10 SM | 4 |
| 99 | Sem registro | 5 |

**Conclusão:** ~75% dos alunos têm renda familiar de até 4 SM. Perfil de baixa renda muito marcado.

### 3.2 Tipo de Instituição
| Instituição | Alunos | % |
|-------------|--------|---|
| Pública | 94 | 65,7% |
| Particular | 40 | 28,0% |
| Sem registro | 9 | 6,3% |

### 3.3 Escolaridade
| Ordem | Nível | Alunos |
|-------|-------|--------|
| 1 | Fundamental I | 30 |
| 2 | Fundamental II | **50** ← maior grupo |
| 3 | Fundamental incompleto | 1 |
| 4 | Cursando Médio | 3 |
| 5 | Médio incompleto | 17 |
| 6 | Médio completo | 26 |
| 7 | Superior incompleto | 4 |
| 8 | Superior completo | 2 |
| 99 | Sem registro | 10 |

### 3.4 Cruzamentos já explorados

**Renda × Tipo de Instituição** — padrão claro:
- Até 2 SM → quase todos em escola pública (15 de 15 com 1 SM vão para pública)
- A partir de 9 SM → todos em escola particular
- Zona de transição entre 3–6 SM

**Renda × Tipo de Deficiência:**
- Deficiência física se concentra nas rendas mais baixas (1–3 SM)
- Alunos sem deficiência têm renda mais distribuída

### 3.5 Valores ausentes a tratar
| Coluna | Sem registro |
|--------|-------------|
| FaixaRenda | 5 alunos |
| TipoInstituicao | 9 alunos |
| AnoEscolar | 10 alunos |

> **Decisão necessária:** definir se "Sem registro" aparece nos gráficos ou é filtrado por padrão.

---

## 4. Objetivos da Página 2 (definidos no Projeto_BI_Parte_A.md)

### Perguntas que o dashboard deve responder
1. Qual é o perfil socioeconômico predominante dos alunos atendidos pelo IRMR?
2. Existe relação entre a faixa de renda e o tipo de instituição de ensino frequentada?
3. Qual a distribuição de escolaridade dos alunos?
4. Como se distribui a renda familiar entre alunos com e sem deficiência?
5. Quais faixas etárias e tipos de deficiência são mais representadas entre alunos de baixa renda?
6. A proporção entre ensino público e particular varia conforme o diagnóstico?

### KPIs planejados para a Página 2
- Distribuição por faixa de renda familiar
- Proporção escola pública vs. particular
- Distribuição por nível de escolaridade
- Cruzamento: Renda × Tipo de instituição
- Cruzamento: Renda × Tipo de deficiência
- Cruzamento: Faixa etária × Escolaridade

---

## 5. Medidas DAX — Página 2

### O que são medidas DAX
DAX (Data Analysis Expressions) é a linguagem de fórmulas do Power BI. As medidas são cálculos dinâmicos que recalculam automaticamente conforme o usuário aplica filtros. São o equivalente às fórmulas do Excel, mas aplicadas a tabelas inteiras e compatíveis com filtros interativos.

### Medidas a criar

```dax
-- Medida base (compartilhada com Página 1)
TotalAlunos = COUNTROWS(Alunos)

-- Instituição
AlunosEscolaPublica =
CALCULATE([TotalAlunos], Alunos[TipoInstituicao] = "Pública")

AlunosEscolaParticular =
CALCULATE([TotalAlunos], Alunos[TipoInstituicao] = "Particular")

PctEscolaPublica =
DIVIDE([AlunosEscolaPublica], [TotalAlunos])

-- Renda
RendaMediaSM =
AVERAGE(Alunos[RendaSM_Aprox])

AlunosBaixaRenda =
CALCULATE([TotalAlunos], Alunos[FaixaRendaOrdem] <= 3)
-- captura: 1 SM, 1 a 2 SM, 2 a 3 SM

PctBaixaRenda =
DIVIDE([AlunosBaixaRenda], [TotalAlunos])

-- Essencial para cruzamentos (respeita filtros)
PctSobreTotal =
DIVIDE([TotalAlunos], CALCULATE([TotalAlunos], ALL(Alunos)))
```

### Formatos a aplicar nas medidas
| Medida | Formato |
|--------|---------|
| TotalAlunos, AlunosEscolaPublica, AlunosEscolaParticular, AlunosBaixaRenda | Número inteiro |
| RendaMediaSM | Decimal, 1 casa (`0,0`) |
| PctEscolaPublica, PctBaixaRenda, PctSobreTotal | Porcentagem, 1 decimal |

---

## 6. Roteiro de Execução no Power BI (com Claude Code)

> Siga esta ordem exata. Cada tarefa pode ser dada como prompt ao Claude Code no VS Code.

---

### TAREFA 1 — Verificar o arquivo CSV
**O que fazer:** confirmar que o arquivo está correto antes de importar no Power BI.

**Prompt para o Claude Code:**
```
Leia o arquivo dados_tratados/alunos_perfil_limpo.csv e me mostre:
1. Shape (linhas × colunas)
2. Valores únicos das colunas: FaixaRenda, TipoInstituicao, AnoEscolar
3. Contagem de valores "Sem registro" em cada uma dessas colunas
4. Confirme que FaixaRendaOrdem e AnoEscolarOrdem estão como inteiros
```

---

### TAREFA 2 — Criar o arquivo de medidas DAX em texto
**O que fazer:** gerar um arquivo `.txt` com todas as medidas prontas para copiar no Power BI.

**Prompt para o Claude Code:**
```
Crie um arquivo chamado medidas_dax_pagina2.txt com todas as medidas DAX
da Página 2 do dashboard do IRMR, incluindo comentários explicando cada uma.
Baseie-se nas colunas do arquivo alunos_perfil_limpo.csv.
```

---

### TAREFA 3 — Gerar análise exploratória visual (opcional mas útil)
**O que fazer:** gerar gráficos em Python para validar os dados antes de montar o Power BI.

**Prompt para o Claude Code:**
```
Usando o arquivo dados_tratados/alunos_perfil_limpo.csv, crie um script Python
chamado eda_pagina2.py que gere os seguintes gráficos com matplotlib/seaborn
e salve como PNG:
1. Barras: distribuição por FaixaRenda (ordenada por FaixaRendaOrdem)
2. Barras: distribuição por TipoInstituicao
3. Barras: distribuição por AnoEscolar (ordenada por AnoEscolarOrdem)
4. Barras empilhadas: FaixaRenda × TipoInstituicao
5. Barras empilhadas: FaixaRenda × TipoDeficiencia (Física / Intelectual / Sem Deficiência)
```

---

### TAREFA 4 — Construir a Página 2 no Power BI (manual, seguindo o guia)

Com o arquivo `.pbix` da Página 1 já aberto (criado pelo outro grupo), adicionar nova página:

**Passo 4.1 — Nova página**
- Clique no `+` na barra de páginas (embaixo) → renomeie para `Perfil Socioeconômico`

**Passo 4.2 — Criar as medidas DAX**
- Painel Dados → botão direito em `_Medidas` → Nova medida
- Criar cada medida da seção 5 deste documento

**Passo 4.3 — Cabeçalho**
- Caixa de texto: `Perfil Socioeconômico dos Alunos` (tamanho 24, negrito)
- Caixa de texto menor: `Distribuição por renda, instituição e escolaridade · n=143` (tamanho 11, cinza)

**Passo 4.4 — Faixa de KPIs (3 cards)**
| Card | Medida | Rótulo |
|------|--------|--------|
| 1 | `[AlunosBaixaRenda]` | "Alunos até 3 SM" |
| 2 | `[PctBaixaRenda]` | "% Baixa renda (≤3 SM)" |
| 3 | `[PctEscolaPublica]` | "% Escola pública" |

**Passo 4.5 — Gráfico 1: Renda Familiar**
- Visual: Gráfico de colunas agrupadas
- Eixo X: `FaixaRenda` | Eixo Y: `[TotalAlunos]`
- ⚠️ Sort by Column: `FaixaRenda` ordenado por `FaixaRendaOrdem` (já configurado na Etapa 3 do guia v1)
- Título: `Renda familiar (em salários mínimos)`

**Passo 4.6 — Gráfico 2: Tipo de Instituição**
- Visual: Gráfico de rosca (Donut)
- Legenda: `TipoInstituicao` | Valores: `[TotalAlunos]`
- Título: `Tipo de instituição de ensino`

**Passo 4.7 — Gráfico 3: Escolaridade**
- Visual: Gráfico de colunas agrupadas
- Eixo X: `AnoEscolar` | Eixo Y: `[TotalAlunos]`
- ⚠️ Sort by Column: `AnoEscolar` ordenado por `AnoEscolarOrdem`
- Formatar → Eixo X → girar rótulos 45°
- Título: `Nível de escolaridade`

**Passo 4.8 — Gráfico 4: Renda × Instituição (cruzamento principal)**
- Visual: Gráfico de colunas empilhadas (Stacked column)
- Eixo X: `FaixaRenda` | Legenda: `TipoInstituicao` | Valores: `[TotalAlunos]`
- Título: `Renda familiar × Tipo de instituição`

**Passo 4.9 — Gráfico 5: Renda × Deficiência**
- Visual: Gráfico de colunas empilhadas
- Eixo X: `FaixaRenda` | Legenda: criar coluna calculada `TipoDeficiencia`* | Valores: `[PctSobreTotal]`
- Título: `Renda familiar × Tipo de deficiência`

> *Coluna calculada `TipoDeficiencia` — criar via Nova Coluna na tabela Alunos:
> ```dax
> TipoDeficiencia =
> IF(Alunos[SemDeficiencia] = TRUE, "Sem Deficiência",
>    IF(Alunos[DeficienciaFisica] = TRUE, "Deficiência Física",
>       IF(Alunos[DeficienciaIntelectual] = TRUE, "Deficiência Intelectual",
>          "Outro")))
> ```

**Passo 4.10 — Slicers laterais**
| Slicer | Campo | Estilo |
|--------|-------|--------|
| Renda | `FaixaRenda` | Lista vertical |
| Instituição | `TipoInstituicao` | Botões (Tile) |
| Faixa Etária | `FaixaEtaria` | Lista vertical |

---

### TAREFA 5 — Validação final (checklist)

**Prompt para o Claude Code:**
```
Analise o arquivo dados_tratados/alunos_perfil_limpo.csv e valide:
1. O gráfico de renda vai mostrar as faixas na ordem correta (1 SM → Acima de 10 SM)?
   Confirme os valores de FaixaRendaOrdem para cada FaixaRenda.
2. O gráfico de escolaridade vai mostrar na ordem correta (Fundamental I → Superior)?
   Confirme os valores de AnoEscolarOrdem para cada AnoEscolar.
3. Quantos alunos teriam "Sem registro" em cada dimensão — devo filtrar ou exibir?
4. A coluna calculada TipoDeficiencia vai funcionar com as colunas booleanas do CSV?
```

---

## 7. Layout sugerido da Página 2

```
┌─────────────────────────────────────────────────────────────────┐
│  Perfil Socioeconômico dos Alunos — IRMR                        │
│  Distribuição por renda, instituição e escolaridade · n=143     │
├─────────────────────────────────────────────────────────────────┤
│  [72 alunos]        [50,3%]              [65,7%]                │
│  Alunos até 3 SM    % Baixa renda        % Escola pública       │
├──────────────────────────────────────┬──────────────────────────┤
│  Renda familiar (colunas)            │  Tipo de instituição     │
│  1SM → Acima 10SM (ordenado)         │  (donut: Púb vs Part)    │
├──────────────────────────────────────┴──────────────────────────┤
│  Renda × Instituição (colunas empilhadas — cruzamento principal)│
├──────────────────────────────────────┬──────────────────────────┤
│  Escolaridade (colunas ordenadas)    │  Renda × Deficiência     │
│                                      │  (colunas empilhadas)    │
└──────────────────────────────────────┴──────────────────────────┘
         ↑ slicers na lateral esquerda: Renda | Instituição | Faixa Etária
```

---

## 8. Referências dos arquivos do projeto

| Arquivo | Conteúdo |
|---------|----------|
| `dados_tratados/alunos_perfil_limpo.csv` | Base de dados principal (143 alunos × 21 colunas) |
| `Projeto_BI_Parte_A.md` | Documento completo do projeto (requisitos, KPIs, ata de reunião) |
| `guia_powerbi_v1.md` | Guia técnico de construção da Página 1 (referência de estilo) |
| `etl_perfil_alunos.py` | Script Python do ETL (gerou o CSV limpo a partir do REDCap) |
| `dashboard_irmr_v1.pbix` | Arquivo Power BI da Página 1 (base para adicionar a Página 2) |

---

*Documento gerado em 19/05/2026 — Claude.ai (claude-sonnet-4-6)*
