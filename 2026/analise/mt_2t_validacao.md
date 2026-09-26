# Validação BU Web — MT 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **7.652**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=MT): **7.652** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.216.730 | 1.216.730 | 0 | 1.000000 |
| Lula (13) | 652.786 | 652.786 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/mt_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/mt_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
