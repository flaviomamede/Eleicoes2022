# Validação BU Web — MS 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **6.912**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=MS): **6.912** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 880.606 | 880.606 | 0 | 1.000000 |
| Lula (13) | 599.547 | 599.547 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/ms_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ms_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
