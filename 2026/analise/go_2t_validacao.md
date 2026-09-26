# Validação BU Web — GO 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **14.620**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=GO): **14.620** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 2.193.041 | 2.193.041 | 0 | 1.000000 |
| Lula (13) | 1.542.115 | 1.542.115 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/go_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/go_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
