# Validação BU Web — AM 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **7.453**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=AM): **7.453** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 961.741 | 961.741 | 0 | 1.000000 |
| Lula (13) | 1.004.991 | 1.004.991 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Governador
- Presidente

## Artefatos

- `dados/buweb/am_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/am_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
