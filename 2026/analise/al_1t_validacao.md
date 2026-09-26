# Validação BU Web — AL 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **6.626**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=AL): **6.626** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 621.515 | 621.515 | 0 | 1.000000 |
| Lula (13) | 974.156 | 974.156 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/al_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/al_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
