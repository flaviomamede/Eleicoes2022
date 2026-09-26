# Validação BU Web — BA 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **34.424**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=BA): **34.424** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 2.047.599 | 2.047.599 | 0 | 1.000000 |
| Lula (13) | 5.873.081 | 5.873.081 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/ba_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/ba_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
