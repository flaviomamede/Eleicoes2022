# Validação BU Web — RR 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **1.268**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=RR): **1.268** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 213.518 | 213.518 | 0 | 1.000000 |
| Lula (13) | 67.128 | 67.128 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/rr_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rr_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
