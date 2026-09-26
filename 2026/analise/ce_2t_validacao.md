# Validação BU Web — CE 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **22.796**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=CE): **22.796** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.634.477 | 1.634.477 | 0 | 1.000000 |
| Lula (13) | 3.807.891 | 3.807.891 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/ce_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ce_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
