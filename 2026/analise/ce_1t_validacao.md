# Validação BU Web — CE 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **22.796**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=CE): **22.796** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.377.827 | 1.377.827 | 0 | 1.000000 |
| Lula (13) | 3.578.355 | 3.578.355 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/ce_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ce_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
