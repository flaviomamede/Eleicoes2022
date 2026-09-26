# Validação BU Web — ES 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **9.239**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=ES): **9.239** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.160.030 | 1.160.030 | 0 | 1.000000 |
| Lula (13) | 897.348 | 897.348 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/es_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/es_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
