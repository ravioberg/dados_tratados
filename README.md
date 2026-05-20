# Dashboard Socioeconômico — IRMR

Projeto Power BI em formato PBIP para análise do perfil socioeconômico dos alunos.

## Estrutura

```
dados_tratados/
├── alunos_perfil_limpo.csv          # base de dados (143 alunos)
├── gera_tmdl.py                     # gera o modelo de dados (tabelas + medidas DAX)
├── gera_pagina2.py                  # gera a Página 2 com todos os visuais
├── eda_pagina2.py                   # análise exploratória dos dados
├── graficos_eda/                    # gráficos gerados pelo EDA
├── socioeconomico.pbip              # arquivo principal do projeto Power BI
├── socioeconomico.Report/           # definição do relatório (páginas e visuais)
└── socioeconomico.SemanticModel/    # modelo de dados (TMDL)
```

## Como usar

> **Power BI Desktop deve estar FECHADO ao rodar os scripts.**

### 1. Gerar o modelo de dados

```bash
python gera_tmdl.py
```

Cria/atualiza os arquivos TMDL em `socioeconomico.SemanticModel/definition/tables/`:
- `Alunos.tmdl` — tabela principal com 21 colunas, carregada do CSV
- `_Medidas.tmdl` — 8 medidas DAX (TotalAlunos, PctBaixaRenda, PctEscolaPublica, etc.)

### 2. Gerar a Página 2

```bash
python gera_pagina2.py
```

Cria a página "Perfil Socioeconômico" com 13 visuais posicionados no canvas de 1280×720.

### 3. Abrir no Power BI Desktop

Abra `socioeconomico.pbip` — o modelo e os visuais já estarão configurados.

---

## Método PBIP (lições aprendidas)

O formato `.pbip` é editável externamente, ao contrário do `.pbix`. Cada visual é um arquivo `visual.json` separado.

### Schema de visual (2.9.0)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json",
  "name": "<id>",
  "position": { "x": 158, "y": 80, "z": 3, "height": 85, "width": 220, "tabOrder": 2 },
  "visual": {
    "visualType": "card",
    "query": {
      "queryState": {
        "Values": { "projections": [{ "field": ..., "queryRef": "Tabela.Medida", "nativeQueryRef": "Medida" }] }
      }
    }
  }
}
```

### Tipos de visual (nomes corretos no PBIP)

| Visual | `visualType` |
|--------|-------------|
| Card clássico | `card` |
| Coluna agrupada | `clusteredColumnChart` |
| Coluna empilhada | `columnChart` ⚠️ (não `stackedColumnChart`) |
| Barra horizontal | `barChart` |
| Rosca | `donutChart` |
| Segmentação | `slicer` |
| Caixa de texto | `textbox` |

> `stackedColumnChart` não é reconhecido como visual nativo — causa erro "CustomVisualNotFound".

### Formato de campo (field)

```python
# Coluna
{"Column": {"Expression": {"SourceRef": {"Entity": "Alunos"}}, "Property": "FaixaRenda"}}

# Medida
{"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas"}}, "Property": "TotalAlunos"}}
```

### Roles por tipo de visual

| Role | Uso |
|------|-----|
| `Category` | Eixo X (coluna) |
| `Y` | Eixo Y (medida) |
| `Series` | Segmentação por cor (empilhado) |
| `Values` | Card, slicer |

### Observações importantes

- `calculatedColumn` não é suportado no TMDL nesta versão do schema — colunas calculadas precisam ser criadas manualmente no Power BI Desktop
- Em pastas sincronizadas com OneDrive, `shutil.rmtree` pode falhar por permissão — o script remove páginas antigas do `pageOrder` sem deletar as pastas físicas
- O `sortByColumn` no TMDL funciona normalmente para ordenar categorias (ex: FaixaRenda por FaixaRendaOrdem)

---

## Medidas DAX

| Medida | Fórmula |
|--------|---------|
| TotalAlunos | `COUNTROWS(Alunos)` |
| AlunosEscolaPublica | `CALCULATE(COUNTROWS(Alunos), Alunos[TipoInstituicao]="Pública")` |
| PctEscolaPublica | `DIVIDE([AlunosEscolaPublica], [TotalAlunos])` |
| AlunosBaixaRenda | `CALCULATE(COUNTROWS(Alunos), Alunos[FaixaRenda] IN {"1 SM","1 a 2 SM","2 a 3 SM"})` |
| PctBaixaRenda | `DIVIDE([AlunosBaixaRenda], [TotalAlunos])` |
| RendaMediaSM | `AVERAGE(Alunos[RendaMedia])` |
| PctSobreTotal | `DIVIDE(COUNTROWS(Alunos), CALCULATE(COUNTROWS(Alunos), ALL(Alunos)))` |
