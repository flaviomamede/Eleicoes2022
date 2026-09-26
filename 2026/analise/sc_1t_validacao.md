# Validação BU Web — SC 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **16.242**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=SC): **16.242** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 2.694.406 | 2.694.406 | 0 | 1.000000 |
| Lula (13) | 1.279.216 | 1.279.216 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/sc_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/sc_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
