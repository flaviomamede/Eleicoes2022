# Base por seção + testes T1/T2/T3

**Data:** 26/09/2026

## 1. Base larga entregue

Pasta: `dados/base_secoes/`

| Arquivo | Tamanho | Conteúdo |
|---------|--------:|----------|
| `secoes_2022_t1.csv.gz` | 60 MB | 472.028 seções × votos largos (1º turno) |
| `secoes_2022_t2.csv.gz` | 25 MB | 472.028 seções (PRES + GOV) |
| `secoes_2022_t{1,2}.parquet` | 52 / 24 MB | idem |
| `bu2022.sqlite.zip` | 95 MB | tabelas `t1` / `t2` |
| `por_uf/*.parquet` | — | checkpoint retomável (56 arquivos) |
| `dicionario_partidos.csv`, `candidatos_gov_sen.csv` | — | auxiliares |
| `README.md` | — | cabeçalho TSE + validações |

### Validação (sem correção)

| Checagem | 1º turno | 2º turno |
|----------|----------|----------|
| Seções (linhas) | 472.028 | 472.028 |
| `DUPLICADO_ID_SECAO` | 0 | 0 |
| Soma PRES = comparecimento (divergências) | **0** | **0** |
| Lula (PRES_13) | **57.259.504** (= ref.) | **60.345.999** (= ref.) |
| Bolsonaro (PRES_22) | **51.072.345** (= ref.) | **58.206.354** (= ref.) |

Modelo de urna **não** está na base (cruzar por `ID_SECAO`).

Geração: `scripts/gerar_base_secoes.py` (parquet por UF; SP/MG em chunks).

---

## 2. Controles T1 / T2 / T3 (1º turno, blocos partidários, soma 1)

Script: `scripts/calibragem_controles_t1t2t3.py`  
CSVs: `analise/controle_T*.csv`

Previsão Opus: se o Δ for **geográfico**, T1 grande e T2 ~0; se for **marca**, o contrário.

| Teste | O que faz | Erro relativo médio Bolsonaro |
|-------|-----------|------------------------------:|
| **T1** | UE2020 capital → UE2020 interior | **−7,1%** (RN −32%, AL −31%, CE −23%…) |
| **T2** | UE2020 → antigas *no mesmo município* (≥30+30 seções) | **−0,9%** (7 UFs; SP −1,6%) |
| **T3** | antigas → UE2020 (inversa) | **+16%** (espelha o desajuste) |

### T1 — maiores |erro| (mesma marca UE2020)

| UF | Treino (cap.) | Teste (int.) | Erro rel. Bolso | Δ pp Bolso | Erro rel. Lula |
|----|--------------:|-------------:|----------------:|-----------:|---------------:|
| RN | 1414 | 2251 | −32,0% | −14,8 | +35,0% |
| AL | 1598 | 783 | −30,9% | −17,6 | +64,5% |
| PI | 1678 | 2063 | −27,5% | −6,0 | +10,6% |
| SE | 1297 | 1060 | −24,1% | −9,3 | +24,3% |
| CE | 5235 | 4330 | −22,9% | −8,3 | +23,6% |
| MA | 2146 | 4668 | −21,1% | −7,5 | +20,1% |
| PB | 1458 | 3063 | −17,9% | −7,1 | +16,2% |

### Leitura

T1 reproduz Δ grandes **com urnas da mesma marca**. T2, onde há municípios mistos, **colapsa**. Isso favore a hipótese **geográfica** (capital × interior) frente à atribuição do erro à marca da urna (R4 baixo), em linha com a crítica ao relatório de calibragem por UF.

Limitação T2: só 165 municípios (quase só SP) passam o filtro ≥30 seções de cada marca; no Nordeste quase não há mistura intramunicipal — o próprio desenho que tornava o teste UF Positivo→Diebold confuso.

---

## 3. Rede R1–R4 (atualizada)

| Nº | Proposição | Situação |
|----|------------|----------|
| R1 | Tabela JR = taxas reais | Fraca (PP/Republicanos) |
| R2 | Regra UE2020 por UF erra nas antigas | Estabelecida |
| R3 | Hold-out valida aplicação às antigas | Não |
| R4 | Erro de R2 = efeito de marca | **Não sustentada** por T1/T2 neste desenho |
