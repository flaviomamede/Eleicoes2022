# Validação BU Web — RS 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **27.201**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=RS): **27.201** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 3.733.185 | 3.733.185 | 0 | 1.000000 |
| Lula (13) | 2.891.851 | 2.891.851 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/rs_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rs_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
