# Validação BU Web — GO 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **14.620**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=GO): **14.620** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 1.920.203 | 1.920.203 | 0 | 1.000000 |
| Lula (13) | 1.454.723 | 1.454.723 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/go_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/go_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
