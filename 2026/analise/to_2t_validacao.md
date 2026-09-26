# Validação BU Web — TO 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **3.957**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=TO): **3.957** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 411.654 | 411.654 | 0 | 1.000000 |
| Lula (13) | 434.593 | 434.593 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/to_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/to_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
