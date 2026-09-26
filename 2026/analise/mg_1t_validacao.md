# Validação BU Web — MG 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **49.981**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=MG): **49.981** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 5.239.264 | 5.239.264 | 0 | 1.000000 |
| Lula (13) | 5.802.571 | 5.802.571 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/mg_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/mg_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
