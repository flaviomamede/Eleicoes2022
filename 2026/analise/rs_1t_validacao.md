# Validação BU Web — RS 1º turno

Fonte processada via `scripts/processar_bweb.py`.

## Seções e cobertura

- Seções no boletim: **27.201**
- Join com modelo de urna (`urnas_pres_gov.parquet`, turno=1, estado=RS): **27.201** (100.0%)

## Presidente — totais BU vs base John

| Candidato | BU Web | Base John | Diferença | Correlação (seção) |
|-----------|--------|-----------|-----------|--------------------|
| Bolsonaro (22) | 3.245.023 | 3.245.023 | 0 | 1.000000 |
| Lula (13) | 2.806.672 | 2.806.672 | 0 | 1.000000 |

## Cargos disponíveis no BU

- Deputado Estadual
- Deputado Federal
- Governador
- Presidente
- Senador

## Artefatos

- `dados/buweb/rs_1t_partido_secao.parquet` — longo (seção × cargo × partido/votável)
- `dados/buweb/rs_1t_secao.parquet` — largo (seção + presidente + modelo de urna)
