# Validação BU Web — RN 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **7.674**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=RN): **7.674** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 711.381 | 711.381 | 0 | 1.000000 |
| Lula (13) | 1.326.785 | 1.326.785 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/rn_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rn_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
