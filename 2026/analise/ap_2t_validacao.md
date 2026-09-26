# Validação BU Web — AP 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **1.740**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=AP): **1.740** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 200.547 | 200.547 | 0 | 1.000000 |
| Lula (13) | 189.918 | 189.918 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/ap_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ap_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
