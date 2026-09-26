# Validação BU Web — RR 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **1.268**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=RR): **1.268** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 207.587 | 207.587 | 0 | 1.000000 |
| Lula (13) | 68.760 | 68.760 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/rr_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rr_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
