# Base de seções — Boletim de Urna TSE 2022

Gerada por `scripts/gerar_base_secoes.py` (parquet por UF + concatenação).

## Cabeçalho real

Codificação: **latin-1**. Separador: **`;`**.

Colunas (45):

```
DT_GERACAO
HH_GERACAO
ANO_ELEICAO
CD_TIPO_ELEICAO
NM_TIPO_ELEICAO
CD_PLEITO
DT_PLEITO
NR_TURNO
CD_ELEICAO
DS_ELEICAO
SG_UF
CD_MUNICIPIO
NM_MUNICIPIO
NR_ZONA
NR_SECAO
NR_LOCAL_VOTACAO
CD_CARGO_PERGUNTA
DS_CARGO_PERGUNTA
NR_PARTIDO
SG_PARTIDO
NM_PARTIDO
DT_BU_RECEBIDO
QT_APTOS
QT_COMPARECIMENTO
QT_ABSTENCOES
CD_TIPO_URNA
DS_TIPO_URNA
CD_TIPO_VOTAVEL
DS_TIPO_VOTAVEL
NR_VOTAVEL
NM_VOTAVEL
QT_VOTOS
NR_URNA_EFETIVADA
CD_CARGA_1_URNA_EFETIVADA
CD_CARGA_2_URNA_EFETIVADA
CD_FLASHCARD_URNA_EFETIVADA
DT_CARGA_URNA_EFETIVADA
DS_CARGO_PERGUNTA_SECAO
DS_AGREGADAS
DT_ABERTURA
DT_ENCERRAMENTO
QT_ELEITORES_BIOMETRIA_NH
DT_EMISSAO_BU
NR_JUNTA_APURADORA
NR_TURMA_APURADORA
```

## DS_TIPO_VOTAVEL

| Valor | Ocorrências |
|-------|------------:|
| Nominal | 61261334 |
| Legenda | 5670385 |
| Nulo | 3047343 |
| Branco | 2992761 |

Outros tipos → `*_OUTROS_TIPOS`: (nenhum).

## DS_TIPO_URNA

| Valor | Ocorrências |
|-------|------------:|
| APURADA | 72971818 |
| ANULADA | 5 |

## Chave

`ID_SECAO = SG_UF_CD_MUNICIPIO_NR_ZONA_NR_SECAO` (inteiros sem zero à esquerda).
`NR_LOCAL_VOTACAO` nos metadados. Duplicados de ID (locais distintos) mantidos com `DUPLICADO_ID_SECAO=1`.

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `secoes_2022_t1.csv.gz` / `_t2.csv.gz` | base larga |
| `secoes_2022_t1.parquet` / `_t2.parquet` | idem |
| `por_uf/*.parquet` | checkpoint por UF |
| `bu2022.sqlite.zip` | tabelas t1/t2 |
| `dicionario_partidos.csv` | partidos |
| `candidatos_gov_sen.csv` | Gov/Sen nominais |
| `validacao_totais_t*.csv` | totais UF×coluna |
| `manifesto.json` | status por UF |

## Validação

### Soma cargo = QT_COMPARECIMENTO

| Turno | Cargo | Divergências |
|------:|-------|-------------:|
| 1 | PRES | 0 |
| 1 | GOV | 19585 |
| 1 | SEN | 19585 |
| 1 | DF | 19587 |
| 1 | DE | 19587 |
| 2 | PRES | 0 |
| 2 | GOV | 233994 |

### Totais presidente

| Turno | Candidato | Referência | Base | Diff |
|------:|-----------|----------:|-----:|-----:|
| 1 | Lula | 57,259,504 | 57,259,504 | 0 |
| 1 | Bolsonaro | 51,072,345 | 51,072,345 | 0 |
| 2 | Lula | 60,345,999 | 60,345,999 | 0 |
| 2 | Bolsonaro | 58,206,354 | 58,206,354 | 0 |

### Seções

| Turno | Linhas | ID únicos | Flag duplicado |
|------:|-------:|----------:|---------------:|
| 1 | 472028 | 472028 | 0 |
| 2 | 472028 | 472028 | 0 |

Referência VOTOS_T1E2: 472.027 seções. Modelo de urna não incluso (cruzar por ID_SECAO).
