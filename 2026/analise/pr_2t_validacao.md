# Validação BU Web — PR 2º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **25.721**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=2, estado=PR): **25.721** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 4.159.343 | 4.159.343 | 0 | 1.000000 |
| Lula (13) | 2.506.605 | 2.506.605 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Presidente

## Artefatos

- `dados/buweb/pr_2t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/pr_2t_secao.parquet` — largo (seção + presidente + modelo de urna)
